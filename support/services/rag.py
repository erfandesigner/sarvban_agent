

# =============================
# support/services/rag.py
# =============================
from typing import List, Tuple
from django.db import connection
from django.conf import settings
from .embeddings import embed_texts
from ..models import RagDocument


def semantic_search(query: str, k: int = 4) -> List[Tuple[str, float]]:
    q_vec = embed_texts([query])[0]
    # Use raw SQL for cosine distance for performance
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT id, chunk, 1 - (embedding <=> %s::vector) AS score
            FROM support_ragdocument
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            [q_vec, q_vec, k],
        )
        rows = cur.fetchall()
    return [(row[1], float(row[2])) for row in rows]


def build_context(query: str, k: int = 4, min_score: float = 0.5) -> str:
    hits = semantic_search(query, k=k)
    chunks = [c for c, s in hits if s >= min_score]
    return "\n\n".join(chunks)
