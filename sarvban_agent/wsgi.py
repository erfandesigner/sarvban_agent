
# =============================
# sarvban_agent/wsgi.py
# =============================
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sarvban_agent.settings")
application = get_wsgi_application()


# =============================
# support/apps.py
# =============================
from django.apps import AppConfig

class SupportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "support"

