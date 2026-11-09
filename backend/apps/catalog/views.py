import csv
import io
from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.users.permissions import IsAdminRole, IsAdminRoleOrReadOnly
from .filters import BookFilter
from .models import Author, Book, Genre
from .serializers import AuthorSerializer, BookSerializer, GenreSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminRoleOrReadOnly]
    pagination_class = None
    search_fields = ["first_name", "last_name"]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminRoleOrReadOnly]
    pagination_class = None
    search_fields = ["name", "slug"]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.prefetch_related("authors", "genres").distinct()
    serializer_class = BookSerializer
    permission_classes = [IsAdminRoleOrReadOnly]
    filterset_class = BookFilter
    search_fields = ["title", "isbn", "description", "authors__last_name", "authors__first_name"]
    ordering_fields = ["id", "title", "published_year", "avg_rating", "available_copies", "created_at"]
    ordering = ["-id"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "Нельзя удалить книгу, так как по ней есть история выдач читателям."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["post"],
        url_path="import-csv",
        permission_classes=[IsAdminRole],
        parser_classes=[MultiPartParser, FormParser, JSONParser],
    )
    def import_csv(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"detail": "Пожалуйста, прикрепите CSV-файл в поле 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decoded_text = uploaded_file.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return Response(
                {"detail": "Не удалось прочитать файл. Убедитесь, что CSV сохранен в кодировке UTF-8."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reader = csv.DictReader(io.StringIO(decoded_text))
        if not reader.fieldnames or "title" not in reader.fieldnames or "isbn" not in reader.fieldnames:
            return Response(
                {"detail": "CSV-файл должен содержать как минимум колонки 'title' и 'isbn'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_count = 0
        updated_count = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            title = (row.get("title") or "").strip()
            isbn = (row.get("isbn") or "").strip()

            if not title or not isbn:
                errors.append(f"Строка {row_num}: пропущены обязательные поля title или isbn.")
                continue

            try:
                published_year = int(row.get("published_year") or 2024)
                pages = int(row.get("pages") or 100)
                total_copies = max(1, int(row.get("total_copies") or 1))
            except ValueError:
                errors.append(f"Строка {row_num}: некорректное числовое значение года, страниц или копий.")
                continue

            defaults = {
                "title": title,
                "description": (row.get("description") or "").strip(),
                "published_year": published_year,
                "publisher": (row.get("publisher") or "").strip(),
                "pages": pages,
                "language": (row.get("language") or "Русский").strip(),
                "cover_url": (row.get("cover_url") or "").strip(),
                "total_copies": total_copies,
                "available_copies": total_copies,
            }

            _, created = Book.objects.update_or_create(isbn=isbn, defaults=defaults)
            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response(
            {
                "created": created_count,
                "updated": updated_count,
                "errors": errors,
                "detail": f"Импорт завершен: создано {created_count}, обновлено {updated_count}.",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="reviews",
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def book_reviews(self, request, pk=None):
        book = self.get_object()
        try:
            from apps.reviews.models import Review
            from apps.reviews.serializers import ReviewSerializer
            from apps.reviews.views import recalculate_book_rating
        except ImportError:
            return Response([], status=status.HTTP_200_OK)

        if request.method == "GET":
            reviews = Review.objects.filter(book=book).select_related("user").order_by("-created_at")
            return Response(ReviewSerializer(reviews, many=True).data, status=status.HTTP_200_OK)

        if Review.objects.filter(user=request.user, book=book).exists():
            return Response(
                {"detail": "Вы уже оставляли отзыв на эту книгу."},
                status=status.HTTP_409_CONFLICT,
            )

        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        data["book"] = book.id
        serializer = ReviewSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, book=book)

        recalculate_book_rating(book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
