"""
Модель элемента личной книжной полки читателя (таблица shelf_item).
Позволяет пользователям LitHub сохранять понравившиеся цифровые книги в свою библиотеку.
"""
from django.conf import settings
from django.db import models

from apps.catalog.models import Book


class ShelfItem(models.Model):
    """Книга, добавленная на полку пользователя LitHub."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shelf_items",
        verbose_name="Читатель",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="shelf_items",
        verbose_name="Книга",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления на полку",
    )

    class Meta:
        db_table = "shelf_item"
        verbose_name = "Книга на полке"
        verbose_name_plural = "Книжные полки читателей"
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_book_shelf",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.username} -> «{self.book.title}»"
