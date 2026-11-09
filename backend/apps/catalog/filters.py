import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(method="filter_by_genre", label="ID или slug жанра")
    author = django_filters.NumberFilter(field_name="authors__id", label="ID автора")
    published_year = django_filters.NumberFilter(field_name="published_year", label="Год издания")
    available = django_filters.BooleanFilter(method="filter_available", label="Только доступные для выдачи")

    class Meta:
        model = Book
        fields = ["genre", "author", "published_year", "available"]

    def filter_by_genre(self, queryset, name, value):
        if not value:
            return queryset
        if str(value).isdigit():
            return queryset.filter(genres__id=int(value)).distinct()
        return queryset.filter(genres__slug__iexact=str(value)).distinct()

    def filter_available(self, queryset, name, value):
        if value is True:
            return queryset.filter(available_copies__gt=0)
        if value is False:
            return queryset.filter(available_copies=0)
        return queryset
