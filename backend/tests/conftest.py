"""
Общие фикстуры pytest для тестирования API цифровой онлайн-библиотеки «LitHub».
"""
import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.catalog.models import Author, Book, Genre
from apps.users.models import User


@pytest.fixture
def api_client():
    """Неавторизованный тестовый клиент DRF APIClient."""
    return APIClient()


@pytest.fixture
def reader_user(db):
    """Создает пользователя с ролью 'reader' (читатель LitHub)."""
    return User.objects.create_user(
        username="test_reader",
        email="reader@lithub.local",
        password="password123",
        role=User.ROLE_READER,
    )


@pytest.fixture
def second_reader_user(db):
    """Создает второго читателя для проверки пересчета среднего рейтинга."""
    return User.objects.create_user(
        username="second_reader",
        email="reader2@lithub.local",
        password="password123",
        role=User.ROLE_READER,
    )


@pytest.fixture
def admin_user(db):
    """Создает пользователя с ролью 'admin' (администратор LitHub)."""
    return User.objects.create_user(
        username="test_admin",
        email="admin@lithub.local",
        password="password123",
        role=User.ROLE_ADMIN,
        is_staff=True,
    )


@pytest.fixture
def reader_client(reader_user):
    """APIClient, авторизованный токеном читателя."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=reader_user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def second_reader_client(second_reader_user):
    """APIClient, авторизованный токеном второго читателя."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=second_reader_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    return client


@pytest.fixture
def admin_client(admin_user):
    """APIClient, авторизованный токеном администратора."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def sample_author(db):
    """Создает тестового автора."""
    return Author.objects.create(
        first_name="Михаил",
        last_name="Булгаков",
        bio="Классик русской литературы XX века.",
    )


@pytest.fixture
def sample_genre(db):
    """Создает тестовый жанр."""
    return Genre.objects.create(
        name="Классика",
        slug="classic",
        description="Произведения классической литературы.",
    )


@pytest.fixture
def sample_book(db, sample_author, sample_genre):
    """Создает тестовую цифровую книгу с привязкой к автору и жанру."""
    book = Book.objects.create(
        title="Мастер и Маргарита",
        isbn="978-5-17-090630-1",
        description="Философский и мистический роман.",
        published_year=1967,
        publisher="АСТ",
        pages=480,
        language="Русский",
    )
    book.authors.add(sample_author)
    book.genres.add(sample_genre)
    return book
