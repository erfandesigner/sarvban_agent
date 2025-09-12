
# =============================
# support/services/embeddings.py
# =============================
from typing import List
from django.conf import settings
import os
from typing import List, Dict, Any
from django.conf import settings
from support.forms import RAGFileUploadForm
from django.shortcuts import render, redirect
from support.models import RagDocument, hash_chunk

_embeddings_model = None


def _load_st_model():
    global _embeddings_model
    if _embeddings_model is None:
        from sentence_transformers import SentenceTransformer
        name = settings.EMBEDDINGS_MODEL
        # allow alias for common short name
        if name == "sentence-transformers/all-MiniLM-L6-v2":
            name = "sentence-transformers/all-MiniLM-L6-v2"
        _embeddings_model = SentenceTransformer(name)
    return _embeddings_model

def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _chunk_text(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap
    return chunks

def embed_texts(folder: str, batch_size: int = 32) -> List[Dict[str, Any]]:
    """
    میره داخل فولدر → فایل‌ها رو می‌خونه → چانک می‌کنه → embedding می‌سازه
    خروجی: [{chunk, embedding, metadata}]
    """
    backend = settings.EMBEDDINGS_BACKEND
    model_name = settings.EMBEDDINGS_MODEL or "text-embedding-3-small"

    # آماده‌سازی
    paths = []
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.lower().endswith((".txt", ".md")):
                paths.append(os.path.join(root, fn))

    results: List[Dict[str, Any]] = []

    if backend == "openai":
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.gapgpt.app/v1",
            api_key=settings.OPENAI_API_KEY
        )

        for path in paths:
            text = _read_file(path)
            chunks = _chunk_text(text)
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                resp = client.embeddings.create(model=model_name, input=batch)
                for chunk, emb in zip(batch, resp.data):
                    results.append({
                        "chunk": chunk,
                        "embedding": emb.embedding,
                        "metadata": {"source": path, "title": os.path.basename(path)}
                    })

    else:
        model = _load_st_model()
        for path in paths:
            text = _read_file(path)
            chunks = _chunk_text(text)
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                vecs = model.encode(batch, normalize_embeddings=True).tolist()
                for chunk, vec in zip(batch, vecs):
                    results.append({
                        "chunk": chunk,
                        "embedding": vec,
                        "metadata": {"source": path, "title": os.path.basename(path)}
                    })

    return results

def createChunk(text : set, path: str, batch_size: int = 32) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    model = _load_st_model()
    chunks = _chunk_text(text)
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        vecs = model.encode(batch, normalize_embeddings=True).tolist()
        for chunk, vec in zip(batch, vecs):
            records.append({
                "chunk": chunk,
                "embedding": vec,
                "metadata": {"source": path, "title": os.path.basename(path)}
            })

        objs = []
        file_stats = {}
        duplicate_count = 0
        for r in records:
            source = r["metadata"]["source"]
            file_stats.setdefault(source, {"chunks": 0, "skipped": 0})

            chunk_hash = hash_chunk(r["chunk"])

            # بررسی تکرار قبل از ذخیره
            if RagDocument.objects.filter(source_id=source, chunk_hash=chunk_hash).exists():
                file_stats[source]["skipped"] += 1
                duplicate_count += 1
                continue

            file_stats[source]["chunks"] += 1
            objs.append(
                RagDocument(
                    source_id=source,
                    title=r["metadata"]["title"],
                    chunk=r["chunk"],
                    embedding=r["embedding"],
                    metadata=r["metadata"],
                    chunk_hash=chunk_hash,
                )
            )

        # ذخیره یک‌باره
        RagDocument.objects.bulk_create(objs, batch_size=200, ignore_conflicts=True)


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploaded_files')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def rag_upload(request):
    result = None
    if request.method == 'POST':
        form = RAGFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            file_path = os.path.join(UPLOAD_DIR, f.name)
            with open(file_path, 'wb+') as destination:
                text = f.read().decode('utf-8')
                result = createChunk(text, file_path)
            return redirect('rag_upload')
    else:
        form = RAGFileUploadForm()
    return render(request, 'support/rag_upload.html', {'form': form, 'result': result})
