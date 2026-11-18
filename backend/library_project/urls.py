"""
Главный файл маршрутизации (URL Configuration) цифровой онлайн-библиотеки «LitHub».
Содержит маршруты админ-панели Django, Swagger UI и всех приложений API v1.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Админ-панель Django
    path("admin/", admin.site.urls),

    # Документация OpenAPI 3.0 и интерактивный Swagger UI
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Приложения API v1 проекта LitHub
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/", include("apps.reviews.urls")),
    path("api/v1/", include("apps.shelf.urls")),
]
