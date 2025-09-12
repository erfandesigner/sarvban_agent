

# =============================
# support/services/rag.py
# =============================
from typing import List, Tuple
from functools import lru_cache
from django.db import connection
from django.conf import settings
from .embeddings import embed_texts
from ..models import RagDocument

@lru_cache(maxsize=1024)
def _embed_query_cached(text: str):
    """Embed and cache query vectors to avoid recomputation.
    Returns a tuple for cacheability; convert to list where needed.
    """
    # from openai import OpenAI
    # client = OpenAI(
    #         base_url="https://api.gapgpt.app/v1",
    #         api_key=settings.OPENAI_API_KEY
    # )
    """ساخت embedding برای متن"""
    # Use local sentence-transformers model for 384-dim embeddings
    from .embeddings import _load_st_model
    model = _load_st_model()
    vec = model.encode([text], normalize_embeddings=True)[0]
    # tuple ensures hashability for lru_cache keys/values
    return tuple(float(x) for x in vec)


def semantic_search(query: str, k: int = 4, title: str = "") -> List[Tuple[str, float]]:
    """Run ANN search over pgvector with optional title filter.
    - Caches query embeddings.
    - Applies configurable pgvector tuning from settings.PGVECTOR_SEARCH_PARAMS.
    """
    embedding = list(_embed_query_cached(query))

    with connection.cursor() as cur:
        # Optional tuning: set LOCAL search params for ANN indexes
        params = getattr(settings, "PGVECTOR_SEARCH_PARAMS", {}) or {}
        if "hnsw.ef_search" in params:
            try:
                cur.execute("SET LOCAL hnsw.ef_search = %s", [int(params["hnsw.ef_search"])])
            except Exception:
                pass
        if "ivfflat.probes" in params:
            try:
                cur.execute("SET LOCAL ivfflat.probes = %s", [int(params["ivfflat.probes"])])
            except Exception:
                pass

        # Build SQL dynamically to avoid ILIKE when no title provided
        if title:
            cur.execute(
                """
                SELECT id, chunk, 1 - (embedding <=> %s::vector) AS score
                FROM support_ragdocument
                WHERE title ILIKE %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                [embedding, f"%{title}%", embedding, k],
            )
        else:
            cur.execute(
                """
                SELECT id, chunk, 1 - (embedding <=> %s::vector) AS score
                FROM support_ragdocument
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                [embedding, embedding, k],
            )
        rows = cur.fetchall()
    return [(row[1], float(row[2])) for row in rows]


def build_context(query: str, k: int = 4, min_score: float = 0.5,title='') -> str:
    hits = semantic_search(query, k=k,title=title)
    chunks = [c for c, s in hits if s >= min_score]
    return "\n\n".join(chunks)
