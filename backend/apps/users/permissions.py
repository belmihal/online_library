"""
Простые и понятные классы прав доступа (Permissions) для переиспользования во всех приложениях.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminRoleOrReadOnly(BasePermission):
    """
    Чтение (GET, HEAD, OPTIONS) разрешено всем (включая гостей).
    Создание, изменение и удаление (POST, PUT, PATCH, DELETE) — только пользователям с ролью 'admin'.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_admin_role", False)
        )


class IsAdminRole(BasePermission):
    """Доступ разрешен только администраторам (role == 'admin')."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_admin_role", False)
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Разрешает удаление или изменение объекта только его автору (user) или администратору.
    Используется для отзывов и выдач.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, "is_admin_role", False):
            return True
        return getattr(obj, "user_id", None) == request.user.id
