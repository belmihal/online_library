from datetime import datetime, time, timedelta
from django.utils import timezone
from rest_framework import serializers

from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_isbn = serializers.CharField(source="book.isbn", read_only=True)
    book_cover_url = serializers.CharField(source="book.cover_url", read_only=True)
    due_at = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Loan
        fields = [
            "id",
            "user",
            "username",
            "book",
            "book_title",
            "book_isbn",
            "book_cover_url",
            "borrowed_at",
            "due_at",
            "returned_at",
            "status",
        ]
        read_only_fields = [
            "id",
            "user",
            "username",
            "book_title",
            "book_isbn",
            "book_cover_url",
            "borrowed_at",
            "returned_at",
            "status",
        ]

    def validate_due_at(self, value):
        if not value:
            return timezone.now() + timedelta(days=14)

        raw = str(value).strip()
        try:
            if len(raw) == 10 and raw.count("-") == 2:
                parsed_date = datetime.strptime(raw, "%Y-%m-%d").date()
                dt = datetime.combine(parsed_date, time(23, 59, 59))
                return timezone.make_aware(dt) if timezone.is_naive(dt) else dt

            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except ValueError:
            raise serializers.ValidationError("Некорректный формат даты due_at. Используйте YYYY-MM-DD.")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.due_at:
            data["due_at"] = instance.due_at.isoformat()
        return data
