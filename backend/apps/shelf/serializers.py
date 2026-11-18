"""
Сериализатор для личной книжной полки читателя (ShelfItemSerializer).
"""
from rest_framework import serializers
from .models import ShelfItem


class ShelfItemSerializer(serializers.ModelSerializer):
    """Сериализатор книги на полке пользователя LitHub."""
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_isbn = serializers.CharField(source="book.isbn", read_only=True)
    book_authors = serializers.SerializerMethodField()

    class Meta:
        model = ShelfItem
        fields = [
            "id",
            "user",
            "book",
            "book_title",
            "book_isbn",
            "book_authors",
            "added_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "book_title",
            "book_isbn",
            "book_authors",
            "added_at",
        ]

    def get_book_authors(self, obj) -> list[str]:
        """Возвращает список полных имен авторов книги."""
        return [author.full_name for author in obj.book.authors.all()]
