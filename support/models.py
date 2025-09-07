
# =============================
# support/models.py
# =============================
from django.db import models
from pgvector.django import VectorField
from django.conf import settings
import hashlib

class ChatSession(models.Model):
    user_id = models.CharField(max_length=128, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=[("user","user"),("assistant","assistant"),("system","system")])
    content = models.TextField()
    token_usage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


def hash_chunk(text: str) -> str:
    """محاسبه SHA256 برای هر چانک متن"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RagDocument(models.Model):
    source_id = models.TextField()
    title = models.TextField()
    chunk = models.TextField()
    embedding = VectorField(dimensions=384)  # بسته به مدل انتخابی
    metadata = models.JSONField(default=dict)
    chunk_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source_id", "chunk_hash"],
                name="unique_source_chunk"
            )
        ]

