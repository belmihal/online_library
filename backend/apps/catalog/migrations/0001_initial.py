import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=100, verbose_name="Имя")),
                ("last_name", models.CharField(max_length=100, verbose_name="Фамилия")),
                ("bio", models.TextField(blank=True, default="", verbose_name="Биография")),
                ("birth_date", models.DateField(blank=True, null=True, verbose_name="Дата рождения")),
            ],
            options={
                "verbose_name": "Автор",
                "verbose_name_plural": "Авторы",
                "db_table": "catalog_author",
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название книги")),
                ("isbn", models.CharField(max_length=20, unique=True, verbose_name="ISBN")),
                ("description", models.TextField(blank=True, default="", verbose_name="Описание")),
                ("published_year", models.PositiveIntegerField(default=2024, verbose_name="Год издания")),
                ("publisher", models.CharField(blank=True, default="", max_length=255, verbose_name="Издательство")),
                ("pages", models.PositiveIntegerField(default=100, verbose_name="Количество страниц")),
                ("language", models.CharField(default="Русский", max_length=50, verbose_name="Язык")),
                ("cover_url", models.URLField(blank=True, default="", max_length=500, verbose_name="Ссылка на обложку")),
                ("total_copies", models.PositiveIntegerField(default=1, verbose_name="Всего экземпляров")),
                ("available_copies", models.PositiveIntegerField(default=1, verbose_name="Доступно для выдачи")),
                ("avg_rating", models.DecimalField(decimal_places=2, default=0.0, max_digits=3, verbose_name="Средний рейтинг")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")),
            ],
            options={
                "verbose_name": "Книга",
                "verbose_name_plural": "Книги",
                "db_table": "catalog_book",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Название жанра")),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True, verbose_name="Слаг (URL)")),
                ("description", models.TextField(blank=True, default="", verbose_name="Описание жанра")),
            ],
            options={
                "verbose_name": "Жанр",
                "verbose_name_plural": "Жанры",
                "db_table": "catalog_genre",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="BookAuthor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="catalog.author", verbose_name="Автор")),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="catalog.book", verbose_name="Книга")),
            ],
            options={
                "verbose_name": "Автор книги",
                "verbose_name_plural": "Авторы книг (M2M)",
                "db_table": "catalog_book_authors",
            },
        ),
        migrations.CreateModel(
            name="BookGenre",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="catalog.book", verbose_name="Книга")),
                ("genre", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="catalog.genre", verbose_name="Жанр")),
            ],
            options={
                "verbose_name": "Жанр книги",
                "verbose_name_plural": "Жанры книг (M2M)",
                "db_table": "catalog_book_genres",
            },
        ),
        migrations.AddField(
            model_name="book",
            name="authors",
            field=models.ManyToManyField(blank=True, related_name="books", through="catalog.BookAuthor", to="catalog.author", verbose_name="Авторы"),
        ),
        migrations.AddField(
            model_name="book",
            name="genres",
            field=models.ManyToManyField(blank=True, related_name="books", through="catalog.BookGenre", to="catalog.genre", verbose_name="Жанры"),
        ),
        migrations.AddConstraint(
            model_name="bookauthor",
            constraint=models.UniqueConstraint(fields=("book", "author"), name="unique_book_author"),
        ),
        migrations.AddConstraint(
            model_name="bookgenre",
            constraint=models.UniqueConstraint(fields=("book", "genre"), name="unique_book_genre"),
        ),
    ]
