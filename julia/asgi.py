"""Add docstring text here for the module."""

import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julia.settings")
django.setup()

import card_manager.routing

django_app = get_asgi_application()
django_app = ASGIStaticFilesHandler(django_app)

application = ProtocolTypeRouter(
    {
        "http": django_app,
        "websocket": AuthMiddlewareStack(URLRouter(card_manager.routing.websocket_urlpatterns)),
    }
)
