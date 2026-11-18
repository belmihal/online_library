# Начальная миграция модели ShelfItem для цифровой библиотеки LitHub
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
            name="ShelfItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("added_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления на полку")),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shelf_items", to="catalog.book", verbose_name="Книга")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shelf_items", to=settings.AUTH_USER_MODEL, verbose_name="Читатель")),
            ],
            options={
                "verbose_name": "Книга на полке",
                "verbose_name_plural": "Книжные полки читателей",
                "db_table": "shelf_item",
                "ordering": ["-added_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="shelfitem",
            constraint=models.UniqueConstraint(fields=("user", "book"), name="unique_user_book_shelf"),
        ),
    ]
