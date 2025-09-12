# =============================
# sarvban_agent/urls.py
# =============================
from django.contrib import admin
from django.urls import path, include
from support.services.embeddings import rag_upload

urlpatterns = [
    path("admin/", admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path("api/", include("support.urls")),
    path('rag-upload/', rag_upload, name='rag_upload'),
]
