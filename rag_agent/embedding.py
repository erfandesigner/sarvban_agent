import time, hashlib
from django.conf import settings
from openai import OpenAI


EMB_CACHE = {}
TTL = settings.CACHE_TTL

def _hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def embed_text(text):
    clientEmb = OpenAI(
        base_url="https://api.gapgpt.app/v1",
        api_key=settings.OPENAI_API_KEY
    )
    key = _hash(text)
    entry = EMB_CACHE.get(key)
    if entry and time.time() - entry["ts"] < TTL:
        return entry["emb"]
    resp = clientEmb.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    emb = resp.data[0].embedding
    EMB_CACHE[key] = {"emb": emb, "ts": time.time()}
    return emb
