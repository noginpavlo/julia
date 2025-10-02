import requests
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model


IS_PRODUCTION = False

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


"""Google Oauth and tokens granting. No refresh token needed."""  # this should be explained in doctrings


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]  # is it final?

    def post(self, request):
        token_id = request.data.get("token")
        if not token_id:
            return Response({"error": "No token provided"}, status=400)

        google_response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token_id}"
        )

        if not google_response.ok:
            return Response({"error": "Invalid Google token"}, status=400)

        payload = google_response.json()
        email = payload.get("email")
        name = payload.get("name")

        if not email:
            return Response({"error": "Email not provided by Google"}, status=400)

        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email.split("@")[0], "first_name": name}
        )

        tokens = generate_tokens(user)
        response = Response(
            data={"access": tokens["access"], "username": tokens["username"]},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, tokens["refresh"])
        print("THIS IS REFRESH TOKEN FROM GoogleAuthView")
        # print(tokens["refresh"])
        print(response.cookies.get("refresh_token"))

        return response


def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        path="/api/users/",
        # domain=".myfuturedomain.com" => use it on prod
    )
    return response


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,  # sends username to display on frontend
    }


"""Grants access token. User has to have JWT already."""


class SocialLoginJWTView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        access_token = str(AccessToken.for_user(user))

        print(f"Access token: {access_token}")

        return Response(
            data={"access": access_token, "username": user.username},
            status=status.HTTP_200_OK,
        )


"""Grants refresh and access JWTs when registered using password. No refresh token needed"""


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:  # too generic exception + controlling logic flow with try/except block
            return Response({"detail": "Invalid credentials"}, status=401)

        user = serializer.user
        tokens = generate_tokens(user)
        response = Response(
            data={"access": tokens["access"], "username": tokens["username"]},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, tokens["refresh"])
        return response


"""Refreshes access token when password auth."""


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
        print("This is tokens from CookieTokenRefreshView. WHEN PASSWORD AUTH")
        print(serializer.validated_data)
        tester = Response(serializer.validated_data)
        print(dir(tester))

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
