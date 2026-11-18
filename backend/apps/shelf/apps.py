from django.apps import AppConfig


class ShelfConfig(AppConfig):
    """Конфигурация приложения книжной полки (apps.shelf)."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shelf"
    verbose_name = "Книжная полка LitHub"
