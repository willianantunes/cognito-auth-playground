import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cognito_custom_ui_and_api.settings")

application = get_asgi_application()
