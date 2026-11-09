import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="Оценка (1..5)")),
                ("comment", models.TextField(blank=True, default="", verbose_name="Текст отзыва")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="catalog.book", verbose_name="Книга")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to=settings.AUTH_USER_MODEL, verbose_name="Пользователь")),
            ],
            options={
                "verbose_name": "Отзыв",
                "verbose_name_plural": "Отзывы",
                "db_table": "reviews_review",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(fields=("user", "book"), name="unique_user_book_review"),
        ),
    ]
