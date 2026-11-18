from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Конфигурация приложения отзывов (apps.reviews)."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"
    verbose_name = "Отзывы читателей LitHub"
