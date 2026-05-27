"""ASGI entrypoint for async-capable Django servers."""

import os

from django.core.asgi import get_asgi_application

# Django needs the settings module before building the ASGI application object.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()
