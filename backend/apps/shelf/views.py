"""
Представления для работы с личной книжной полкой читателя LitHub (/api/v1/shelf/):
- GET    /api/v1/shelf/      — список книг на полке текущего пользователя;
- POST   /api/v1/shelf/      — добавить книгу на полку (при дубле возвращает 409 Conflict);
- DELETE /api/v1/shelf/{id}/ — убрать книгу со своей полки (204 No Content).
"""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.catalog.models import Book
from .models import ShelfItem
from .serializers import ShelfItemSerializer


class ShelfItemViewSet(viewsets.ModelViewSet):
    """Управление личной книжной полкой текущего пользователя LitHub."""
    serializer_class = ShelfItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return (
            ShelfItem.objects.filter(user=self.request.user)
            .select_related("book")
            .prefetch_related("book__authors")
        )

    def create(self, request, *args, **kwargs):
        """Добавляет книгу на полку пользователя (или возвращает 409 Conflict, если она уже там)."""
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if "book" not in data and "book_id" in data:
            data["book"] = data["book_id"]

        book_id = data.get("book")
        if not book_id:
            return Response(
                {"detail": "Необходимо указать ID книги (book или book_id)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = get_object_or_404(Book, pk=book_id)

        if ShelfItem.objects.filter(user=request.user, book=book).exists():
            return Response(
                {"detail": "Эта книга уже добавлена в вашу библиотеку."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(user=request.user, book=book)

        return Response(self.get_serializer(item).data, status=status.HTTP_201_CREATED)
