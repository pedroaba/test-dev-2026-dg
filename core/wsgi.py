"""WSGI entrypoint for traditional synchronous Django servers."""

import os

from django.core.wsgi import get_wsgi_application

# Django needs the settings module before building the WSGI application object.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
