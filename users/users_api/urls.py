from django.urls import path
from .views import (
    RegisterView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    # OAuthCallbackView,
    # SocialLoginJWTView,
    GoogleAuthView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path("oauth/callback/", OAuthCallbackView.as_view(), name="oauth_callback"), # this is questionable
    # path("social/token/", SocialLoginJWTView.as_view(), name="social_token"), # this is to be removed
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'), # NEW Oauth
]
