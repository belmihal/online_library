from django.db import models
from django.utils.text import slugify


class Author(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    bio = models.TextField(blank=True, default="", verbose_name="Биография")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    class Meta:
        db_table = "catalog_author"
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.full_name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Слаг (URL)")
    description = models.TextField(blank=True, default="", verbose_name="Описание жанра")

    class Meta:
        db_table = "catalog_genre"
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or "genre"
            slug_candidate = base_slug
            counter = 1
            while Genre.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название книги")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    published_year = models.PositiveIntegerField(default=2024, verbose_name="Год издания")
    publisher = models.CharField(max_length=255, blank=True, default="", verbose_name="Издательство")
    pages = models.PositiveIntegerField(default=100, verbose_name="Количество страниц")
    language = models.CharField(max_length=50, default="Русский", verbose_name="Язык")
    cover_url = models.URLField(max_length=500, blank=True, default="", verbose_name="Ссылка на обложку")

    total_copies = models.PositiveIntegerField(default=1, verbose_name="Всего экземпляров")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Доступно для выдачи")

    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name="Средний рейтинг",
    )

    authors = models.ManyToManyField(
        Author,
        through="BookAuthor",
        related_name="books",
        blank=True,
        verbose_name="Авторы",
    )
    genres = models.ManyToManyField(
        Genre,
        through="BookGenre",
        related_name="books",
        blank=True,
        verbose_name="Жанры",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        db_table = "catalog_book"
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.title} ({self.isbn})"


class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Автор")

    class Meta:
        db_table = "catalog_book_authors"
        verbose_name = "Автор книги"
        verbose_name_plural = "Авторы книг (M2M)"
        constraints = [
            models.UniqueConstraint(fields=["book", "author"], name="unique_book_author")
        ]

    def __str__(self) -> str:
        return f"{self.book_id} <-> {self.author_id}"


class BookGenre(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Жанр")

    class Meta:
        db_table = "catalog_book_genres"
        verbose_name = "Жанр книги"
        verbose_name_plural = "Жанры книг (M2M)"
        constraints = [
            models.UniqueConstraint(fields=["book", "genre"], name="unique_book_genre")
        ]

    def __str__(self) -> str:
        return f"{self.book_id} <-> {self.genre_id}"
