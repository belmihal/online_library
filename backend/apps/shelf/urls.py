"""Маршруты книжной полки LitHub (/api/v1/shelf/)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ShelfItemViewSet

router = DefaultRouter()
router.register(r"shelf", ShelfItemViewSet, basename="shelf")

urlpatterns = [
    path("", include(router.urls)),
]
