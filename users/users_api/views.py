from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework import status
import json


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


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            refresh_token = response.data.get("refresh")
            access_token = response.data.get("access")

            cookie_max_age = 7 * 24 * 60 * 60 # 7 days in seconds

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                # secure=True, | this ensures that data is sent via HTTPS only (which means that can't be used in dev)
                samesite="Strict",
                max_age=cookie_max_age,
                path="/api/users/token/refresh/",
            )

            response.data.pop("refresh")
            response.data = {"access": access_token}

            # 🔽 Print response info
            print("=== Response Info ===")
            print("Status Code:", response.status_code)
            print("Headers:")
            for k, v in response.items():
                print(f"{k}: {v}")
            print("Cookies Set:")
            for c in response.cookies.values():
                print(c.output())
            print("Body:")
            print(json.dumps(response.data, indent=4))
            print("=======================")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response(
                {"detail": "Refresh token cookie not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Include refresh token to request.data body (HTTP-only cookies, no refresh token in body)
        request.data._mutable = True
        request.data["refresh"] = refresh_token
        request.data._mutable = False

        # how in this function the token is sent via COOKIES only if there is no lines that remove refresh tok from the body?
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request):
        response = Response({"detail": "Logged out"}, status=200)
        response.delete_cookie("refresh_token", path="/api/users/token/refresh/")
        return response

