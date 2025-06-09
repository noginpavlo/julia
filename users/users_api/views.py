from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegisterSerializer


IS_PRODUCTION = False


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {"message": f"Hello {request.user.username}, welcome to your dashboard!"}
        )


def generate_jwt_response(user, status_code=status.HTTP_200_OK, redirect_url=None):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    cookie_max_age = 7 * 24 * 60 * 60  # 7 days in seconds

    response_data = {
        "access": access_token,
        "username": user.username,
    } if not redirect_url else None
    response = Response(data=response_data, status=status_code)

    if redirect_url:
        response['Location'] = redirect_url

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="Strict",
        max_age=cookie_max_age,
        path="/api/users/",
    )

    print(response.data)

    return response


"""Grants refresh token. User is expected to be authenticated via session."""
class OAuthCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated: # session authenticated
            return redirect('http://localhost:5173/login')

        return generate_jwt_response(
            user,
            status_code=status.HTTP_302_FOUND,
            redirect_url='http://localhost:5173/oauth/callback'
        )


"""Grants access token. User has to have JWT already."""
class SocialLoginJWTView(APIView):
    permission_classes = [IsAuthenticated] #JWT-authenticated

    def get(self, request):
        return generate_jwt_response(request.user)


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Invalid credentials"}, status=401)

        user = serializer.user
        return generate_jwt_response(user)


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

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        response = Response({"detail": "Logged out"}, status=200)
        response.delete_cookie("refresh_token", path="/api/users/token/refresh/")
        response.delete_cookie("refresh_token", path="/api/users/")
        return response
