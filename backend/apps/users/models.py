"""
Модель пользователя цифровой онлайн-библиотеки «LitHub».
Наследуется от AbstractUser и добавляет поле роли (role):
- 'reader' (читатель) — может добавлять книги на свою полку и оставлять отзывы;
- 'admin' (администратор) — управляет каталогом книг, авторами, жанрами и импортом CSV.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя LitHub с разделением ролей (reader / admin)."""

    ROLE_READER = "reader"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_READER, "Читатель"),
        (ROLE_ADMIN, "Администратор"),
    ]

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
        help_text="Уникальный email пользователя",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_READER,
        verbose_name="Роль пользователя",
    )

    class Meta:
        db_table = "users_user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        """При создании суперпользователя автоматически назначаем роль admin."""
        if self.is_superuser:
            self.role = self.ROLE_ADMIN
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self) -> bool:
        """Проверка: является ли пользователь администратором LitHub."""
        return self.role == self.ROLE_ADMIN or self.is_superuser or self.is_staff

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
