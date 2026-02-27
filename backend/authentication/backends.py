"""
Custom JWT authentication backend that reads tokens from HTTP-only cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads the JWT access token from an HTTP-only cookie instead of the
    Authorization header.
    """

    def authenticate(self, request):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE)
        if access_token is None:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
        except TokenError:
            return None

        return self.get_user(validated_token), validated_token
