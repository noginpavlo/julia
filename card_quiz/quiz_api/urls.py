from django.urls import path
from .views import QuizCardsAPIView

urlpatterns = [
    path("test/", QuizCardsAPIView.as_view(), name="quiz"),
]
