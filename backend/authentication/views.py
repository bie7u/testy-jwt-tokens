from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .models import DiagnosticExchangeCode
from .serializers import UserSerializer, LoginSerializer, DiagnosticLoginSerializer
from .utils import get_tokens_for_user, set_auth_cookies, clear_auth_cookies


class LoginView(APIView):
    """
    Authenticate a user and set JWT tokens in HTTP-only cookies.
    Optionally restrict to staff-only or customer-only depending on the
    ``require_staff`` query parameter supplied by the frontend.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Enforce staff-only login when the frontend requests it
        require_staff = request.query_params.get('require_staff', 'false').lower() == 'true'
        if require_staff and not user.is_staff:
            return Response(
                {'detail': 'Staff access required.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = get_tokens_for_user(user)
        response = Response({
            'user': UserSerializer(user).data,
        })
        set_auth_cookies(response, tokens['access'], tokens['refresh'])
        return response


class LogoutView(APIView):
    """Clear the JWT cookies to log the user out."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({'detail': 'Logged out successfully.'})
        clear_auth_cookies(response)
        return response


class RefreshTokenView(APIView):
    """Use the refresh token cookie to obtain a new access token."""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE)
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token not found.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                new_refresh_token = str(token)
            else:
                new_refresh_token = refresh_token

        except TokenError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response({'detail': 'Token refreshed.'})
        set_auth_cookies(response, access_token, new_refresh_token)
        return response


class MeView(APIView):
    """Return info about the currently authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserListView(APIView):
    """List all non-staff (customer) users. Staff only."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        customers = User.objects.filter(is_staff=False, is_active=True).order_by('username')
        return Response(UserSerializer(customers, many=True).data)


class DiagnosticLoginView(APIView):
    """
    Staff-only endpoint. Creates a short-lived exchange code that can be used
    to open the customer frontend in a new tab as a specific customer, while
    retaining the staff identity for audit/logging purposes.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = DiagnosticLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = serializer.validated_data['customer_id']
        try:
            customer = User.objects.get(id=customer_id, is_staff=False, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Customer not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate tokens for the customer
        customer_tokens = get_tokens_for_user(customer)

        # Store a short-lived exchange code
        exchange = DiagnosticExchangeCode.objects.create(
            staff_user_id=request.user.id,
            customer_user_id=customer.id,
            customer_access_token=customer_tokens['access'],
            customer_refresh_token=customer_tokens['refresh'],
        )

        return Response({
            'code': str(exchange.code),
            'customer': UserSerializer(customer).data,
        })


class ExchangeCodeView(APIView):
    """
    Exchange a one-time diagnostic code for customer JWT cookies.
    The response body also includes the staff user's info so the customer
    frontend can display a diagnostic banner.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response(
                {'detail': 'Exchange code is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expiry_delta = timedelta(seconds=settings.DIAGNOSTIC_CODE_EXPIRY)
        cutoff = timezone.now() - expiry_delta

        try:
            exchange = DiagnosticExchangeCode.objects.get(
                code=code,
                used=False,
                created_at__gte=cutoff,
            )
        except DiagnosticExchangeCode.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired exchange code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark the code as used (one-time use)
        exchange.used = True
        exchange.save()

        try:
            customer = User.objects.get(id=exchange.customer_user_id)
            staff_user = User.objects.get(id=exchange.staff_user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        response = Response({
            'customer': UserSerializer(customer).data,
            'staff': UserSerializer(staff_user).data,
            'diagnostic': True,
        })
        set_auth_cookies(
            response,
            exchange.customer_access_token,
            exchange.customer_refresh_token,
        )
        return response
