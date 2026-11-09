from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "username",
            "book",
            "book_title",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "user", "username", "book_title", "created_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Оценка должна быть в диапазоне от 1 до 5.")
        return value
