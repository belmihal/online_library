"""
Главный файл маршрутизации (URL Configuration) проекта «Онлайн-библиотека книг».
Содержит маршруты админ-панели Django, документации Swagger и всех приложений API v1.
"""
from pathlib import Path
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    # Стандартная админ-панель Django
    path("admin/", admin.site.urls),

    # Документация OpenAPI 3.0 и интерактивный Swagger UI
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Шаг 1: Авторизация, регистрация и профиль пользователя (/api/v1/auth/...)
    path("api/v1/auth/", include("apps.users.urls")),
]

# Автоматически подключаем маршруты Шага 2 и Шага 3 по мере добавления файлов
if (BASE_DIR / "apps" / "catalog" / "urls.py").exists():
    urlpatterns.append(path("api/v1/", include("apps.catalog.urls")))

if (BASE_DIR / "apps" / "reviews" / "urls.py").exists():
    urlpatterns.append(path("api/v1/", include("apps.reviews.urls")))

if (BASE_DIR / "apps" / "loans" / "urls.py").exists():
    urlpatterns.append(path("api/v1/", include("apps.loans.urls")))
