"""
Представления (Views) для аутентификации и профиля пользователя:
- POST /api/v1/auth/register/ — регистрация нового читателя и выдача токена;
- POST /api/v1/auth/login/    — вход в систему и получение бессрочного токена;
- POST /api/v1/auth/logout/   — выход из системы (удаление токена);
- GET  /api/v1/auth/me/       — получение профиля текущего авторизованного пользователя.
"""
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    """
    Регистрация нового читателя.
    Сразу создает бессрочный токен и возвращает {'token': '...', 'user': {...}},
    чтобы студент мог сразу войти или перенаправить пользователя на страницу входа.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Создаем или получаем постоянный токен для нового пользователя
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Вход пользователя по логину и паролю.
    Возвращает бессрочный токен и объект пользователя (id, username, email, role).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Получаем существующий или создаем новый токен
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    Выход из системы.
    Удаляет текущий токен пользователя из базы данных.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(
            {"detail": "Вы успешно вышли из системы."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    Получение данных текущего авторизованного пользователя (профиль).
    Используется фронтендом для проверки сессии и отображения личного кабинета.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
