from django.conf import settings
from django.db import models

from apps.catalog.models import Book


class Loan(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_RETURNED = "returned"
    STATUS_OVERDUE = "overdue"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "На руках"),
        (STATUS_RETURNED, "Возвращена"),
        (STATUS_OVERDUE, "Просрочена"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="Читатель",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="loans",
        verbose_name="Книга",
    )
    borrowed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата выдачи",
    )
    due_at = models.DateTimeField(
        verbose_name="Срок возврата (до какой даты)",
    )
    returned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Фактическая дата возврата",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name="Статус выдачи",
    )

    class Meta:
        db_table = "loans_loan"
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"
        ordering = ["-borrowed_at"]

    def __str__(self) -> str:
        return f"{self.user.username} -> «{self.book.title}» ({self.status})"
