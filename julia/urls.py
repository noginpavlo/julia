"""
URL configuration for julia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.users, name='users')
Class-based views
    1. Add an import:  from other_app.views import users
    2. Add a URL to urlpatterns:  path('', users.as_view(), name='users')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from card_manager import views as card_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("api/cards/", include("card_manager.api.urls")),
    path("api/quiz/", include("card_quiz.quiz_api.urls")),
    path("api/users/", include("users.users_api.urls")),
    path("decks/", card_views.show_decks, name="show-decks"),
    path("decks/<int:deck_id>/cards/", card_views.show_cards, name="show-cards"),
    path("oops/", card_views.oops_view, name="oops"),
    path("create-card/", card_views.create_card_view, name="create-card"),
    path("study/page/", card_views.show_card_template_view, name="show-card-page"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("accounts/", include("allauth.urls")),
]
