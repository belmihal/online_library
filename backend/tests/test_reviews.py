"""
Unit-тесты для отзывов, пересчета avg_rating и поля reviews_count в LitHub (apps.reviews).
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
def test_review_recalculates_book_avg_rating_and_reviews_count(
    reader_client, second_reader_client, sample_book
):
    """Проверяет пересчет avg_rating и обновление reviews_count при добавлении и удалении отзывов."""
    assert float(sample_book.avg_rating) == 0.0

    resp1 = reader_client.post(
        "/api/v1/reviews/",
        {"book": sample_book.id, "rating": 5, "comment": "Отличный роман!"},
        format="json",
    )
    assert resp1.status_code == status.HTTP_201_CREATED
    sample_book.refresh_from_db()
    assert float(sample_book.avg_rating) == 5.0

    resp2 = second_reader_client.post(
        "/api/v1/reviews/",
        {"book": sample_book.id, "rating": 3, "comment": "Хорошая книга."},
        format="json",
    )
    assert resp2.status_code == status.HTTP_201_CREATED
    sample_book.refresh_from_db()
    assert float(sample_book.avg_rating) == 4.0

    book_detail = reader_client.get(f"/api/v1/books/{sample_book.id}/")
    assert book_detail.status_code == status.HTTP_200_OK
    assert book_detail.data["reviews_count"] == 2
    assert book_detail.data["avg_rating"] == 4.0

    review_id = resp2.data["id"]
    del_resp = second_reader_client.delete(f"/api/v1/reviews/{review_id}/")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
    sample_book.refresh_from_db()
    assert float(sample_book.avg_rating) == 5.0

    book_detail_after = reader_client.get(f"/api/v1/books/{sample_book.id}/")
    assert book_detail_after.data["reviews_count"] == 1


@pytest.mark.django_db
def test_duplicate_review_returns_409_conflict(reader_client, sample_book):
    """Проверяет статус 409 Conflict при повторном отзыве от одного пользователя."""
    payload = {"book": sample_book.id, "rating": 5, "comment": "Первый отзыв"}
    first_resp = reader_client.post("/api/v1/reviews/", payload, format="json")
    assert first_resp.status_code == status.HTTP_201_CREATED

    second_resp = reader_client.post("/api/v1/reviews/", payload, format="json")
    assert second_resp.status_code == status.HTTP_409_CONFLICT
