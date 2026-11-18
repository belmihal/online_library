"""
Unit-тесты для личной книжной полки читателя LitHub (apps.shelf).
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
def test_add_list_and_remove_book_on_shelf(reader_client, sample_book):
    """Проверяет добавление книги на полку, просмотр полки и удаление книги с полки."""
    # 1. Добавляем книгу на полку
    add_resp = reader_client.post(
        "/api/v1/shelf/",
        {"book": sample_book.id},
        format="json",
    )
    assert add_resp.status_code == status.HTTP_201_CREATED
    assert add_resp.data["book"] == sample_book.id
    assert add_resp.data["book_title"] == "Мастер и Маргарита"
    assert add_resp.data["book_isbn"] == "978-5-17-090630-1"
    assert add_resp.data["book_authors"] == ["Михаил Булгаков"]

    # 2. Получаем список книг на полке
    list_resp = reader_client.get("/api/v1/shelf/")
    assert list_resp.status_code == status.HTTP_200_OK
    assert len(list_resp.data) == 1

    # 3. Удаляем книгу со своей полки
    item_id = add_resp.data["id"]
    del_resp = reader_client.delete(f"/api/v1/shelf/{item_id}/")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    empty_list_resp = reader_client.get("/api/v1/shelf/")
    assert len(empty_list_resp.data) == 0


@pytest.mark.django_db
def test_duplicate_book_on_shelf_returns_409_conflict(reader_client, sample_book):
    """Проверяет, что повторное добавление той же книги на полку возвращает 409 Conflict."""
    first_resp = reader_client.post("/api/v1/shelf/", {"book": sample_book.id}, format="json")
    assert first_resp.status_code == status.HTTP_201_CREATED

    duplicate_resp = reader_client.post("/api/v1/shelf/", {"book": sample_book.id}, format="json")
    assert duplicate_resp.status_code == status.HTTP_409_CONFLICT
    assert duplicate_resp.data["detail"] == "Эта книга уже добавлена в вашу библиотеку."


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_shelf(api_client):
    """Проверяет, что неавторизованный гость не имеет доступа к /api/v1/shelf/."""
    resp = api_client.get("/api/v1/shelf/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
