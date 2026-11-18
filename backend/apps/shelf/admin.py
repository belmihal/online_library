"""Регистрация модели ShelfItem в админ-панели Django."""
from django.contrib import admin
from .models import ShelfItem


@admin.register(ShelfItem)
class ShelfItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "added_at")
    list_filter = ("added_at",)
    search_fields = ("user__username", "book__title")
