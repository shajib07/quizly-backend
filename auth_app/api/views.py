"""API views for registration, login, logout and token refresh."""

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.utils import (
    blacklist_refresh_token,
    delete_auth_cookies,
    get_login_data,
    get_new_access_token,
    set_access_cookie,
    set_auth_cookies,
)
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    """Create a new user account."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Validate the submitted data and save the new user."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'User created successfully!'},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Log a user in and set the JWT cookies."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Validate the credentials and return the user data."""
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password'),
        )
        if user is None:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response(get_login_data(user))
        set_auth_cookies(response, RefreshToken.for_user(user))
        return response


class LogoutView(APIView):
    """Log the user out, blacklist the refresh token and clear the cookies."""

    def post(self, request):
        """Invalidate the refresh token and delete both cookies."""
        blacklist_refresh_token(request.COOKIES.get('refresh_token'))
        response = Response({
            'detail': 'Log-Out successfully! All Tokens will be deleted. '
                      'Refresh token is now invalid.'
        })
        delete_auth_cookies(response)
        return response


class CookieTokenRefreshView(APIView):
    """Issue a new access token using the refresh token cookie."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Set a new access token cookie if the refresh token is valid."""
        raw_refresh_token = request.COOKIES.get('refresh_token')
        access_token = get_new_access_token(raw_refresh_token)
        if access_token is None:
            return Response(
                {'detail': 'Refresh token invalid or missing.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response({'detail': 'Token refreshed'})
        set_access_cookie(response, access_token)
        return response