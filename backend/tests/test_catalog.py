"""
Unit-тесты для каталога цифровых книг LitHub (apps.catalog).
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from apps.catalog.models import Author, Book, Genre


@pytest.mark.django_db
def test_create_book_with_sample_text_by_admin_and_forbidden_for_reader(
    admin_client, reader_client, sample_author, sample_genre
):
    """Проверяет создание книги с sample_text администратором (201) и запрет для читателя (403)."""
    payload = {
        "title": "Собачье сердце",
        "isbn": "978-5-17-090630-2",
        "description": "Сатирическая повесть.",
        "sample_text": "Глава 1. Зимний вечер в Москве\n\nМетель заметала переулки.",
        "published_year": 1925,
        "publisher": "Азбука",
        "pages": 224,
        "author_ids": [sample_author.id],
        "genre_ids": [sample_genre.id],
    }

    forbidden_resp = reader_client.post("/api/v1/books/", payload, format="json")
    assert forbidden_resp.status_code == status.HTTP_403_FORBIDDEN

    admin_resp = admin_client.post("/api/v1/books/", payload, format="json")
    assert admin_resp.status_code == status.HTTP_201_CREATED
    assert admin_resp.data["title"] == "Собачье сердце"
    assert "Глава 1." in admin_resp.data["sample_text"]
    assert admin_resp.data["reviews_count"] == 0
    assert len(admin_resp.data["authors"]) == 1
    assert len(admin_resp.data["genres"]) == 1


@pytest.mark.django_db
def test_filter_search_and_page_size(api_client, sample_book):
    """Проверяет фильтрацию по жанру, автору, поиск и параметр ?page_size=100."""
    other_genre = Genre.objects.create(name="Фантастика", slug="scifi")
    other_author = Author.objects.create(first_name="Айзек", last_name="Азимов")
    second_book = Book.objects.create(
        title="Основание",
        isbn="978-5-17-090630-6",
        published_year=1951,
    )
    second_book.genres.add(other_genre)
    second_book.authors.add(other_author)

    res_genre = api_client.get("/api/v1/books/?genre=classic")
    assert res_genre.status_code == status.HTTP_200_OK
    assert res_genre.data["count"] == 1
    assert res_genre.data["results"][0]["title"] == "Мастер и Маргарита"
    assert res_genre.data["results"][0]["reviews_count"] == 0

    res_author = api_client.get(f"/api/v1/books/?author={other_author.id}")
    assert res_author.status_code == status.HTTP_200_OK
    assert res_author.data["count"] == 1

    res_search = api_client.get("/api/v1/books/?search=Булгаков&page_size=100")
    assert res_search.status_code == status.HTTP_200_OK
    assert res_search.data["count"] == 1
    assert res_search.data["results"][0]["id"] == sample_book.id


@pytest.mark.django_db
def test_import_books_from_csv_with_sample_text(admin_client):
    """Проверяет массовый импорт книг из CSV-файла с необязательной колонкой sample_text."""
    csv_content = (
        "title,isbn,published_year,publisher,pages,description,sample_text\n"
        "Пикник на обочине,978-5-17-090700-1,1972,АСТ,256,Фантастическая повесть.,Глава 1. Туман над Зонoй.\n"
        "Герой нашего времени,978-5-17-090700-3,1840,Эксмо,224,Классический роман.,\n"
    ).encode("utf-8")

    uploaded = SimpleUploadedFile("books.csv", csv_content, content_type="text/csv")
    response = admin_client.post(
        "/api/v1/books/import-csv/",
        {"file": uploaded},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["created"] == 2
    imported_book = Book.objects.get(isbn="978-5-17-090700-1")
    assert "Глава 1." in imported_book.sample_text
