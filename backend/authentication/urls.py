from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    MeView,
    UserListView,
    DiagnosticLoginView,
    ExchangeCodeView,
    DiagnosticInfoView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('users/', UserListView.as_view(), name='auth-users'),
    path('diagnostic-login/', DiagnosticLoginView.as_view(), name='auth-diagnostic-login'),
    path('exchange/', ExchangeCodeView.as_view(), name='auth-exchange'),
    path('diagnostic-info/', DiagnosticInfoView.as_view(), name='auth-diagnostic-info'),
]
