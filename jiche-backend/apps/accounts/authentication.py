from rest_framework import authentication, exceptions
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings

from apps.accounts.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate_header(self, request):
        return self.keyword

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode('utf-8')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]
        try:
            backend = TokenBackend(
                api_settings.ALGORITHM,
                api_settings.SIGNING_KEY,
                api_settings.VERIFYING_KEY,
                api_settings.AUDIENCE,
                api_settings.ISSUER,
                api_settings.JWK_URL,
                api_settings.LEEWAY,
                api_settings.JSON_ENCODER,
            )
            payload = backend.decode(token, verify=True)
            user_id = payload.get(api_settings.USER_ID_CLAIM)
            if user_id is None:
                raise exceptions.AuthenticationFailed('无效 token')
            user = User.objects.filter(pk=user_id, is_deleted=False, is_active=True).first()
            if user is None:
                # 无 WWW-Authenticate 时 DRF 会把未认证压成 403；配合 authenticate_header 返回 401
                return None
            return user, token
        except (InvalidToken, TokenError) as exc:
            raise exceptions.AuthenticationFailed('登录已过期，请重新登录') from exc
