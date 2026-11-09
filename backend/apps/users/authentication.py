"""
Кастомный класс токен-аутентификации на базе стандартного TokenAuthentication из DRF.
Позволяет фронтенду передавать заголовок как в формате 'Authorization: Token <ключ>',
так и в формате 'Authorization: Bearer <ключ>', чтобы избежать любых ошибок на клиенте.
"""
from rest_framework.authentication import TokenAuthentication, get_authorization_header


class FlexibleTokenAuthentication(TokenAuthentication):
    """Поддерживает префиксы Token и Bearer для бессрочного токена DRF."""

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None

        prefix = auth[0].lower()
        if prefix not in (b"token", b"bearer"):
            return None

        if len(auth) != 2:
            return None

        try:
            token = auth[1].decode()
        except UnicodeError:
            return None

        return self.authenticate_credentials(token)
