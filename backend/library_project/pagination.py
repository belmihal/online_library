"""
Настройка пагинации REST API цифровой онлайн-библиотеки LitHub.
По умолчанию возвращает 12 книг на страницу, но поддерживает параметр ?page_size=100
(например, для загрузки полного списка книг в таблице администратора).
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Пагинация списков с поддержкой параметра ?page_size=..."""
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 200
