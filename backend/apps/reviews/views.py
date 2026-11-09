from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.catalog.models import Book
from apps.users.permissions import IsOwnerOrAdmin
from .models import Review
from .serializers import ReviewSerializer


def recalculate_book_rating(book: Book) -> None:
    agg = Review.objects.filter(book=book).aggregate(avg=Avg("rating"))
    avg_value = agg["avg"] or 0.0
    book.avg_rating = round(float(avg_value), 2)
    book.save(update_fields=["avg_rating"])


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "book").all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        book_id = self.request.query_params.get("book")
        user_id = self.request.query_params.get("user")
        mine = self.request.query_params.get("mine")

        if book_id and str(book_id).isdigit():
            queryset = queryset.filter(book_id=int(book_id))
        if user_id and str(user_id).isdigit():
            queryset = queryset.filter(user_id=int(user_id))
        if mine and mine.lower() in ("true", "1", "yes") and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if "book" not in data and "book_id" in data:
            data["book"] = data["book_id"]

        book_id = data.get("book")
        if book_id and Review.objects.filter(user=request.user, book_id=book_id).exists():
            return Response(
                {"detail": "Вы уже оставляли отзыв на эту книгу."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user)

        recalculate_book_rating(review.book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        review = serializer.save()
        recalculate_book_rating(review.book)

    def perform_destroy(self, instance):
        book = instance.book
        instance.delete()
        recalculate_book_rating(book)
