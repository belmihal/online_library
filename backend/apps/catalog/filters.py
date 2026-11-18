"""
Фильтры для каталога книг LitHub (django-filter):
- ?genre=<id или slug жанра>
- ?author=<id автора>
- ?published_year=<год>
"""
import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    """Набор фильтров для списка книг GET /api/v1/books/."""
    genre = django_filters.CharFilter(method="filter_by_genre", label="ID или slug жанра")
    author = django_filters.NumberFilter(field_name="authors__id", label="ID автора")
    published_year = django_filters.NumberFilter(field_name="published_year", label="Год издания")

    class Meta:
        model = Book
        fields = ["genre", "author", "published_year"]

    def filter_by_genre(self, queryset, name, value):
        """Позволяет передавать как числовой ID жанра (?genre=1), так и текстовый slug (?genre=classic)."""
        if not value:
            return queryset
        if str(value).isdigit():
            return queryset.filter(genres__id=int(value)).distinct()
        return queryset.filter(genres__slug__iexact=str(value)).distinct()
