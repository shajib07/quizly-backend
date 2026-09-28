"""Helper functions for handling JWT tokens stored in HTTP-only cookies."""

from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


def get_cookie_settings():
    """Return the shared security settings for the auth cookies."""
    return {'httponly': True, 'secure': not settings.DEBUG, 'samesite': 'Lax'}


def set_access_cookie(response, access_token):
    """Attach the access token to the response as an HTTP-only cookie."""
    response.set_cookie('access_token', str(access_token), **get_cookie_settings())


def set_auth_cookies(response, refresh_token):
    """Attach the access and the refresh token as HTTP-only cookies."""
    set_access_cookie(response, refresh_token.access_token)
    response.set_cookie('refresh_token', str(refresh_token), **get_cookie_settings())


def delete_auth_cookies(response):
    """Remove both token cookies from the client."""
    response.delete_cookie('access_token', samesite='Lax')
    response.delete_cookie('refresh_token', samesite='Lax')


def get_new_access_token(raw_refresh_token):
    """Return a new access token for a valid refresh token, otherwise None."""
    if raw_refresh_token is None:
        return None
    try:
        return RefreshToken(raw_refresh_token).access_token
    except TokenError:
        return None


def blacklist_refresh_token(raw_refresh_token):
    """Blacklist the refresh token so it can no longer be used."""
    if raw_refresh_token is None:
        return
    try:
        RefreshToken(raw_refresh_token).blacklist()
    except TokenError:
        pass
    