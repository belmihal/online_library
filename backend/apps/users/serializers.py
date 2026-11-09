"""
Сериализаторы для отображения профиля, регистрации и входа пользователя.
"""
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для безопасного возврата данных пользователя (без пароля)."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
        read_only_fields = ["id", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации нового читателя (Форма 2 на фронтенде).
    Проверяет совпадение паролей password и password_confirm (или password2).
    """
    password = serializers.CharField(
        write_only=True,
        min_length=4,
        help_text="Пароль (минимум 4 символа)",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Подтверждение пароля",
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "role"]
        read_only_fields = ["id", "role"]

    def validate(self, attrs):
        """Проверяем совпадение паролей, если передано поле подтверждения."""
        password = attrs.get("password")
        # Поддерживаем как password_confirm, так и случай, если фронтенд не прислал его
        password_confirm = attrs.pop("password_confirm", None)
        if password_confirm is not None and password_confirm != "" and password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают."}
            )
        return attrs

    def create(self, validated_data):
        """Создаем пользователя с хэшированием пароля через create_user."""
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=User.ROLE_READER,
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа по логину (или email) и паролю (Форма 1 на фронтенде)."""
    username = serializers.CharField(help_text="Имя пользователя (username) или email")
    password = serializers.CharField(write_only=True, help_text="Пароль")

    def validate(self, attrs):
        username_or_email = attrs.get("username", "").strip()
        password = attrs.get("password", "")

        # Если пользователь ввел email вместо username, найдем его username
        if "@" in username_or_email:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                username_or_email = user_obj.username

        user = authenticate(username=username_or_email, password=password)
        if not user:
            raise serializers.ValidationError("Неверное имя пользователя или пароль.")
        if not user.is_active:
            raise serializers.ValidationError("Учетная запись деактивирована.")

        attrs["user"] = user
        return attrs
