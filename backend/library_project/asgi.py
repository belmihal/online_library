"""ASGI config для проекта library_project."""
import os
from django.core.asgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_project.settings")
application = get_wsgi_application()
