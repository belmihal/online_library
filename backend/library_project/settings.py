"""
Единый файл настроек Django-проекта «Онлайн-библиотека книг».
Работает на встроенной базе данных SQLite3 из коробки — без необходимости устанавливать PostgreSQL.
"""
import os
from pathlib import Path

# Базовая директория проекта (папка backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ (для учебного проекта задано безопасное значение по умолчанию)
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-online-library-student-project-key-2026"
)

# Режим отладки (включен по умолчанию для удобной разработки и защиты)
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

# Разрешаем запросы с любых локальных адресов
ALLOWED_HOSTS = ["*"]

# Подключенные приложения проекта
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние библиотеки
    "rest_framework",
    "rest_framework.authtoken",  # Простая и надежная бессрочная токен-аутентификация
    "corsheaders",               # Разрешение запросов с React-фронтенда (CORS)
    "django_filters",            # Фильтрация каталога книг
    "drf_spectacular",           # Генерация документации Swagger (/api/v1/docs/)
    # Приложения нашего проекта (подключаются по мере выполнения Шагов 1, 2 и 3)
    "apps.users",
]

# Автоматически подключаем приложения Шага 2 и Шага 3, когда их папки будут добавлены
for app_label in ("catalog", "reviews", "loans"):
    if (BASE_DIR / "apps" / app_label).exists():
        INSTALLED_APPS.append(f"apps.{app_label}")

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Должен быть как можно выше для работы CORS
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

# База данных: используем только легкую и надежную SQLite3 (файл db.sqlite3 в папке backend/)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Указываем нашу кастомную модель пользователя с полем role ('reader' | 'admin')
AUTH_USER_MODEL = "users.User"

# Валидаторы паролей отключены для удобства тестирования и демонстрации на защите
AUTH_PASSWORD_VALIDATORS = []

# Локализация и часовой пояс
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Разрешаем все CORS-запросы с клиентского React-приложения (например, http://localhost:5173)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Настройки Django REST Framework
REST_FRAMEWORK = {
    # Аутентификация по бессрочному токену (поддерживает заголовки Token <key> и Bearer <key>)
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.authentication.FlexibleTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # По умолчанию разрешаем чтение всем, а изменение — авторизованным
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    # Бэкенды фильтрации, поиска и сортировки по умолчанию
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Пагинация списков (по 12 элементов на страницу — удобно для сетки карточек)
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    # Генератор схемы OpenAPI 3.0
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Настройки Swagger-документации (drf-spectacular)
SPECTACULAR_SETTINGS = {
    "TITLE": "Онлайн-библиотека книг API",
    "DESCRIPTION": "Учебный REST API для каталога книг, выдач (loans) и отзывов читателей (reviews).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_schema": False,
}
