from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework.views import APIView


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {"message": f"Hello {request.user.username}, welcome to your dashboard!"}
        )
