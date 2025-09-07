import os

# پوشه اصلی پروژه
BASE_DIR = "sarvban_agent"
os.makedirs(BASE_DIR, exist_ok=True)

# ساخت پوشه‌ها
folders = [
    "support/services",
    "support/management/commands",
    "sarvban_agent",
]
for folder in folders:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# فایل‌ها و محتوا
files = {
    "requirements.txt": """Django>=5.0
pydantic>=2.7
python-dotenv>=1.0
pymongo[srv]>=4.8
psycopg2-binary>=2.9
pgvector>=0.2.5
django-pgvector>=0.2.3
sentence-transformers>=3.0
openai>=1.40
uvicorn>=0.30
""",

    ".env.example": """DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sarvban
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

MONGO_URI=mongodb://localhost:27017
MONGO_DB=sarvban
MONGO_PRODUCTS_COLLECTION=products

EMBEDDINGS_BACKEND=sentence-transformers
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
OPENAI_API_KEY=
LLM_BACKEND=openai
LLM_MODEL=gpt-4o-mini

SITE_BASE_URL=https://sarvban.com
""",

    "manage.py": """#!/usr/bin/env python
import os, sys
def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sarvban_agent.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == "__main__":
    main()
""",

    "README.md": "# Sarvban Agro Support Agent\n\nپروژه جنگو برای پشتیبان هوشمند فروش محصولات کشاورزی.",

    "sarvban_agent/__init__.py": "",
    "sarvban_agent/settings.py": "# تنظیمات جنگو (باید تکمیل شود)",
    "sarvban_agent/urls.py": "from django.urls import path, include\nurlpatterns = [path('api/', include('support.urls'))]\n",
    "sarvban_agent/wsgi.py": """import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sarvban_agent.settings')
application=get_wsgi_application()
""",

    "support/__init__.py": "",
    "support/apps.py": "from django.apps import AppConfig\nclass SupportConfig(AppConfig):\n    default_auto_field='django.db.models.BigAutoField'\n    name='support'\n",
    "support/urls.py": "from django.urls import path\nfrom .views import chat\nurlpatterns = [path('chat', chat)]\n",
    "support/views.py": "# TODO: پیاده‌سازی endpoint چت",
    "support/models.py": "# TODO: مدل‌های چت و RAG",
    "support/services/embeddings.py": "# TODO: سرویس ساخت embedding",
    "support/services/rag.py": "# TODO: سرویس RAG",
    "support/services/mongo.py": "# TODO: سرویس MongoDB",
    "support/services/intents.py": "# TODO: تشخیص نیت کاربر",
    "support/management/commands/ingest_rag.py": "# TODO: دستور ingestion برای RAG",
}

# نوشتن فایل‌ها
for path, content in files.items():
    file_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ پروژه در پوشه `{BASE_DIR}` ساخته شد.")
