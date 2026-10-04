"""App configuration for the authentication app."""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Configure the app that handles registration and JWT login."""

    name = 'auth_app'
