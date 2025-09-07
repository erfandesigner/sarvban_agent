# =============================
# support/admin.py (optional, to inspect in admin)
# =============================
from django.contrib import admin
from .models import ChatSession, ChatMessage, RagDocument


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("user_id", "created_at", "last_activity")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "created_at", "token_usage")
    list_filter = ("role",)


@admin.register(RagDocument)
class RagDocAdmin(admin.ModelAdmin):
    list_display = ("source_id", "title", "created_at")
    search_fields = ("source_id", "title", "chunk")

