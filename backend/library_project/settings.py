"""
Единый файл настроек Django-проекта цифровой онлайн-библиотеки «LitHub».
Работает на встроенной базе данных SQLite3 (db.sqlite3) из коробки.
"""
import os
from pathlib import Path

# Базовая директория проекта (папка backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ приложения
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-lithub-digital-library-project-key-2026",
)

# Режим отладки
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

# Разрешенные хосты
ALLOWED_HOSTS = ["*"]

# Подключенные приложения проекта LitHub
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние библиотеки
    "rest_framework",
    "rest_framework.authtoken",  # Бессрочная токен-аутентификация
    "corsheaders",               # Разрешение CORS-запросов с React-фронтенда
    "django_filters",            # Фильтрация каталога книг
    "drf_spectacular",           # Интерактивная документация Swagger (/api/v1/docs/)
    # Приложения цифровой библиотеки LitHub
    "apps.users",
    "apps.catalog",
    "apps.reviews",
    "apps.shelf",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "library_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "library_project.wsgi.application"
ASGI_APPLICATION = "library_project.asgi.application"

# База данных SQLite3 (файл db.sqlite3 создается в папке backend/)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Кастомная модель пользователя с полем role ('reader' | 'admin')
AUTH_USER_MODEL = "users.User"

# Валидаторы паролей отключены для удобства тестирования на защите
AUTH_PASSWORD_VALIDATORS = []

# Локализация и часовой пояс
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Разрешаем CORS-запросы с фронтенда
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Настройки Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.authentication.FlexibleTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "library_project.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Настройки документации OpenAPI / Swagger UI
SPECTACULAR_SETTINGS = {
    "TITLE": "LitHub API",
    "DESCRIPTION": "REST API цифровой онлайн-библиотеки LitHub: каталог книг, книжная полка (shelf) и отзывы читателей (reviews).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
