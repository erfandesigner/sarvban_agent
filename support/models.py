
# =============================
# support/models.py
# =============================
from django.db import models
from pgvector.django import VectorField
try:
    # Optional: available in pgvector.django >= 0.2
    from pgvector.django import HnswIndex
except Exception:  # pragma: no cover
    HnswIndex = None
from django.contrib.postgres.indexes import GinIndex
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
    product_name=models.CharField(max_length=100, null=True, blank=True)
    token_usage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


def hash_chunk(text: str) -> str:
    """محاسبه SHA256 برای هر چانک متن"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RagDocument(models.Model):
    source_id = models.TextField()
    title = models.TextField()
    chunk = models.TextField()
    embedding = VectorField(dimensions=384)  # 384-dim: all-MiniLM-L6-v2 or similar
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
        # Speed up ANN search on embedding and ILIKE filter on title
        indexes = []
        # HNSW index for cosine distance (fast ANN). Requires pgvector >= 0.5
        if HnswIndex is not None:
            indexes.append(
                HnswIndex(
                    name="ragdoc_embedding_hnsw_cosine",
                    fields=["embedding"],
                    opclasses=["vector_cosine_ops"],
                )
            )
        # Trigram GIN index to accelerate ILIKE queries on title
        indexes.append(
            GinIndex(
                name="ragdoc_title_trgm",
                fields=["title"],
                opclasses=["gin_trgm_ops"],
            )
        )
