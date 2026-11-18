"""
Представления (Views) аутентификации и профиля пользователя LitHub:
- POST /api/v1/auth/register/ — регистрация читателя;
- POST /api/v1/auth/login/    — вход в систему;
- POST /api/v1/auth/logout/   — выход из системы;
- GET  /api/v1/auth/me/       — получение профиля текущего пользователя.
"""
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    """Регистрация нового читателя LitHub."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Вход в аккаунт LitHub по логину и паролю."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Выход из системы (удаление токена)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(
            {"detail": "Вы успешно вышли из системы."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Получение данных текущего пользователя."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
