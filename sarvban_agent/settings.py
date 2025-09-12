
# =============================
# sarvban_agent/settings.py
# =============================
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INTERNAL_IPS = ["127.0.0.1","localhost"]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pgvector.django",  # pgvector integration
    "support",
    "debug_toolbar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]

ROOT_URLCONF = "sarvban_agent.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sarvban_agent.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "sarvban"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5400"),
        "OPTIONS": {"options": "-c search_path=public"},
    }
}

# Static files
STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(Path(__file__).resolve().parent.parent, 'static')
]
print("STATICFILES_DIRS:", STATICFILES_DIRS)
# Mongo
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("MONGO_DB", "phalcon")
MONGO_PRODUCTS_COLLECTION = os.environ.get("MONGO_PRODUCTS_COLLECTION", "adv")

# Embeddings / LLM
EMBEDDINGS_BACKEND = os.environ.get("EMBEDDINGS_BACKEND", "sentence-transformers")
EMBEDDINGS_MODEL = os.environ.get("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
LLM_BACKEND = os.environ.get("LLM_BACKEND", "openai")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
CHAT_LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "http://localhost:8000")

PGVECTOR_DIM = 384 if "MiniLM" in EMBEDDINGS_MODEL else 1536
