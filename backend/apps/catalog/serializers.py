"""
Сериализаторы цифрового каталога книг LitHub (Author, Genre, Book).
"""
from rest_framework import serializers
from .models import Author, Book, Genre


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор автора книги."""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "full_name", "bio", "birth_date"]


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра / категории книги."""

    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "description"]
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
        }


class BookSerializer(serializers.ModelSerializer):
    """
    Универсальный сериализатор цифровой книги LitHub.
    - При GET-запросах возвращает полные объекты authors и genres, avg_rating,
      количество отзывов reviews_count и ознакомительный фрагмент sample_text.
    - При POST/PATCH-запросах принимает списки ID авторов и жанров (author_ids / genre_ids).
    """
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="Список ID авторов книги",
    )
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="Список ID жанров книги",
    )
    avg_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "description",
            "sample_text",
            "published_year",
            "publisher",
            "pages",
            "language",
            "cover_url",
            "avg_rating",
            "reviews_count",
            "authors",
            "genres",
            "author_ids",
            "genre_ids",
            "created_at",
        ]
        read_only_fields = ["id", "avg_rating", "reviews_count", "created_at"]

    def get_reviews_count(self, obj) -> int:
        """Возвращает количество отзывов, оставленных к данной книге."""
        return obj.reviews.count()

    def to_internal_value(self, data):
        """Поддержка передачи списков ID как в author_ids/genre_ids, так и в authors/genres."""
        if hasattr(data, "copy"):
            mutable_data = data.copy()
        else:
            mutable_data = dict(data)

        if "author_ids" not in mutable_data and "authors" in mutable_data:
            raw_authors = mutable_data.get("authors")
            if isinstance(raw_authors, list) and all(not isinstance(x, dict) for x in raw_authors):
                mutable_data["author_ids"] = raw_authors

        if "genre_ids" not in mutable_data and "genres" in mutable_data:
            raw_genres = mutable_data.get("genres")
            if isinstance(raw_genres, list) and all(not isinstance(x, dict) for x in raw_genres):
                mutable_data["genre_ids"] = raw_genres

        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        author_ids = validated_data.pop("author_ids", [])
        genre_ids = validated_data.pop("genre_ids", [])

        book = Book.objects.create(**validated_data)
        if author_ids:
            book.authors.set(author_ids)
        if genre_ids:
            book.genres.set(genre_ids)
        return book

    def update(self, instance, validated_data):
        author_ids = validated_data.pop("author_ids", None)
        genre_ids = validated_data.pop("genre_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if author_ids is not None:
            instance.authors.set(author_ids)
        if genre_ids is not None:
            instance.genres.set(genre_ids)
        return instance
