from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.catalog.models import Book


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Книга",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка (1..5)",
    )
    comment = models.TextField(
        blank=True,
        default="",
        verbose_name="Текст отзыва",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        db_table = "reviews_review"
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_book_review",
            )
        ]

    def __str__(self) -> str:
        return f"Отзыв {self.user} на «{self.book.title}» ({self.rating}/5)"
