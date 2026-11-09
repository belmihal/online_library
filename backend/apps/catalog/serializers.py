from rest_framework import serializers
from .models import Author, Book, Genre


class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "full_name", "bio", "birth_date"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "description"]
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
        }


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "description",
            "published_year",
            "publisher",
            "pages",
            "language",
            "cover_url",
            "total_copies",
            "available_copies",
            "avg_rating",
            "authors",
            "genres",
            "author_ids",
            "genre_ids",
            "created_at",
        ]
        read_only_fields = ["id", "avg_rating", "created_at"]

    def to_internal_value(self, data):
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

    def validate(self, attrs):
        total = attrs.get("total_copies", getattr(self.instance, "total_copies", 1))
        if "available_copies" not in attrs and self.instance is None:
            attrs["available_copies"] = total
        available = attrs.get("available_copies", getattr(self.instance, "available_copies", total))

        if available > total:
            raise serializers.ValidationError(
                {"available_copies": "Доступных копий не может быть больше общего количества (total_copies)."}
            )
        return attrs

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
