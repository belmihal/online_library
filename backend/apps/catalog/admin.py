from django.contrib import admin
from .models import Author, Book, BookAuthor, BookGenre, Genre


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


class BookGenreInline(admin.TabularInline):
    model = BookGenre
    extra = 1


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "birth_date")
    search_fields = ("first_name", "last_name")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "isbn", "published_year", "available_copies", "total_copies", "avg_rating")
    list_filter = ("published_year", "language")
    search_fields = ("title", "isbn")
    inlines = [BookAuthorInline, BookGenreInline]
