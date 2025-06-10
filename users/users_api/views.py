from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegisterSerializer


IS_PRODUCTION = False


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {"message": f"Hello {request.user.username}, welcome to your dashboard!"}
        )


def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="Lax",
        max_age= 7 * 24 * 60 * 60, # 7 days in seconds
        path="/api/users/",
    )
    return response


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username, #sends username to display on frontend
    }


"""Grants refresh token. User is expected to be authenticated via session."""
class OAuthCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('http://localhost:5173/login')

        tokens = generate_tokens(user)
        response = Response(
            data={"access": tokens["access"], "username": tokens["username"]},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, tokens["refresh"])
        return response


"""Grants access token. User has to have JWT already."""
class SocialLoginJWTView(APIView):
    permission_classes = [IsAuthenticated] #JWTauthentication

    def get(self, request):
        user = request.user
        access_token = str(AccessToken.for_user(user))
        return Response(
            data={"access": access_token, "username": user.username},
            status=status.HTTP_200_OK,
        )


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Invalid credentials"}, status=401)

        user = serializer.user
        tokens = generate_tokens(user)
        response = Response(
            data={"access": tokens["access"], "username": tokens["username"]},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, tokens["refresh"])
        return response


"""Refreshes access token when password auth"""
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        print(serializer.validated_data)
        tester = Response(serializer.validated_data)
        print(dir(tester))

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.headers.get("Authorization"))

        response = Response({"detail": "Logged out"}, status=200)
        response.set_cookie(
            key="refresh_token",
            value=None,
            httponly=True,
            secure=IS_PRODUCTION,
            samesite="Lax",
            path="/api/users/",
        )

        return response
