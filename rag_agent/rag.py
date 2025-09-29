import json
from .models import Product_rags as Product
from .embedding import embed_text
from .filters import apply_filters
from django.conf import settings
from openai import OpenAI
from django.db import models
import hashlib
from  pgvector.django import CosineDistance
import time

ANSWER_CACHE = {}

def _cache_answer(key, val):
    ANSWER_CACHE[key] = {"resp": val, "ts": time.time()}

def _get_cached_answer(key):
    entry = ANSWER_CACHE.get(key)
    if entry and time.time() - entry["ts"] < settings.CACHE_TTL:
        return entry["resp"]
    return None

def retrieve(query, filters):
    emb = embed_text(query)
    # Assuming 'embedding' is a pgvector field and pgvector is installed

    qs = Product.objects.annotate(
        sim=CosineDistance('embedding', emb)
    )
    qs = apply_filters(qs, filters or {})
    return qs.order_by("sim")[: settings.TOP_K]

def build_context(products):
    lines = []
    for p in products:
        lines.append(f"Title: {p.title}\\nDesc: {p.description}\\nPrice: {p.price}")
    ctx = "\\n---\\n".join(lines)
    return ctx[-settings.MAX_CONTEXT_CHARS:]

def answer(query, filters):

    llm = OpenAI(base_url="https://api.gapgpt.app/v1",api_key=settings.OPENAI_API_KEY)
    key = hashlib.sha256(query.encode()).hexdigest()
    cached = _get_cached_answer(key)
    if cached:
        return cached

    prods = retrieve(query, filters)
    context = build_context(prods)

    prompt = f"Context:\\n{context}\\n\\nQuestion: {query}\\nRespond JSON with fields: title, summary, recommendation."

    resp = llm.chat.completions.create(
        model=settings.CHAT_LLM_MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.2
    )
    content = resp.choices[0].message.content
    if content is None:
        raise ValueError("LLM response content is None")
    
    # Remove Markdown code block markers if present
    if content.strip().startswith("```"):
        content = content.strip().strip("`")
        # Remove the first line (e.g., ```json) and the last line (```)
        lines = content.splitlines()
        if len(lines) >= 3:
            content = "".join(lines[1:])  # Include all lines except the first (e.g., ```json)
    
    out = json.loads(content)
    _cache_answer(key, out)
    return out
