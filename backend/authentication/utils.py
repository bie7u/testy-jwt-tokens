"""
Utility helpers for cookie-based JWT token management.
"""
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Generate access and refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def _cookie_kwargs(max_age=None):
    """Return common cookie keyword arguments."""
    kwargs = dict(
        httponly=settings.COOKIE_HTTPONLY,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
    )
    if max_age is not None:
        kwargs['max_age'] = max_age
    return kwargs


def set_auth_cookies(response, access_token, refresh_token):
    """Set JWT tokens as persistent HTTP-only cookies on a response.

    Used for regular (non-diagnostic) logins. Cookies carry an explicit
    ``max_age`` so they survive browser restarts.
    """
    access_max_age = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    refresh_max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE,
        value=access_token,
        **_cookie_kwargs(max_age=access_max_age),
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        **_cookie_kwargs(max_age=refresh_max_age),
    )


def set_diagnostic_cookies(response, customer_access, customer_refresh, staff_access):
    """Set session-scoped HTTP-only cookies for a diagnostic login.

    All three cookies have **no** ``max_age``/``expires``, making them pure
    session cookies that the browser discards when the tab (or browser) is
    closed.  This is intentional: a diagnostic session should not persist
    across browser restarts.

    Three cookies are set:
    * ``access_token``       — customer JWT (used by DRF to authenticate requests)
    * ``refresh_token``      — customer refresh JWT
    * ``staff_access_token`` — the initiating staff member's JWT, carried on
                               every request so the backend can audit which
                               staff member performed which action.
    """
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE,
        value=customer_access,
        **_cookie_kwargs(),
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE,
        value=customer_refresh,
        **_cookie_kwargs(),
    )
    response.set_cookie(
        key=settings.STAFF_ACCESS_TOKEN_COOKIE,
        value=staff_access,
        **_cookie_kwargs(),
    )


def clear_auth_cookies(response):
    """Clear all JWT cookies (regular and diagnostic)."""
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE)
    response.delete_cookie(settings.STAFF_ACCESS_TOKEN_COOKIE)
