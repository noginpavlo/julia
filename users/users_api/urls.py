from django.urls import path
from .views import (
    RegisterView,
    DashboardAPIView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    OAuthCallbackView,
    SocialLoginJWTView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("oauth/callback/", OAuthCallbackView.as_view(), name="oauth_callback"),
    path("social/token/", SocialLoginJWTView.as_view(), name="social_token"),
]
