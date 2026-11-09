from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, GenreViewSet

router = DefaultRouter()
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
]
