from django.urls import path
from .views import QuizCardsAPIView

urlpatterns = [
    path('quiz-decks/', QuizCardsAPIView.as_view(), name='quiz-decks'),
]