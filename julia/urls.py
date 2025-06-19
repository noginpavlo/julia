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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("api/card_manager/", include("card_manager.api.urls")),
    path("api/quiz/", include("card_quiz.quiz_api.urls")),
    path("api/users/", include("users.users_api.urls")),
    path("accounts/", include("allauth.urls")), # deprecated
]
