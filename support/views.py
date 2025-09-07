# TODO: پیاده‌سازی endpoint چت
# =============================
# support/views.py
# =============================
import json
from typing import Dict, Any
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings

from .models import ChatSession, ChatMessage
from .services.intents import detect_intent
from .services.mongo import search_products
from .services.rag import build_context

WELCOME = (
    "سلام! به پشتیبانی سروبان خوش آمدید. برای خرید یا فروش محصول کشاورزی چه کمکی لازم دارید؟"
)

SYSTEM_PROMPT = (
    """
    شما یک دستیار فارسی‌زبان و متخصص بازار محصولات کشاورزی هستید. 
    هدف: تشخیص نیاز کاربر (خرید/فروش/کمک) و پاسخ دقیق با تکیه بر داده‌های RAG و کاتالوگ محصولات.
    قواعد:
    - مختصر و مودبانه پاسخ بده.
    - اگر محصولی پیدا شد، کارت محصول با نام، قیمت، شهر/استان، موجودی و لینک تولید کن.
    - اگر محصول پیدا نشد، بگو موجود نیست و پیشنهاد بده محصول مشابه.
    - کاربر را به بازدید از سایت دعوت کن.
    - اگر سوالی خارج از حوزه بود، مودبانه بگو فقط در زمینه محصولات کشاورزی کمک می‌کنی.
    - غیر از دیتابیس محصولات و RAG، از هیچ منبع دیگری استفاده نکن.
    - از تاریخچه جلسه فقط 3 پیام آخر را لحاظ کن تا مصرف توکن کم باشد.
    - اگر پاسخ قطعی نیست، سوال شفاف‌ساز بپرس.
    """
)


def _get_or_create_session(user_id: str) -> ChatSession:
    sess, _ = ChatSession.objects.get_or_create(user_id=user_id)
    return sess


def _save_message(session: ChatSession, role: str, content: str, tokens: int = 0):
    ChatMessage.objects.create(session=session, role=role, content=content, token_usage=tokens)


def _recent_history(session: ChatSession, limit: int = 3):
    msgs = ChatMessage.objects.filter(session=session).order_by("-created_at")[:limit]
    return list(reversed([{"role": m.role, "content": m.content} for m in msgs]))


def _llm_complete(messages: list[dict[str, str]]) -> str:
    # Optional LLM; can be disabled to run rule-based only
    if settings.LLM_BACKEND == "openai" and settings.OPENAI_API_KEY:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.gapgpt.app/v1",api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=350,
        )
        return resp.choices[0].message.content
    # Fallback: simple rule-based stitch
    return messages[-1]["content"]


def _product_card(p: Dict[str, Any]) -> Dict[str, Any]:
    base = settings.SITE_BASE_URL.rstrip("/")
    link = p.get("link") or f"{base}/products/{p.get('slug') or p.get('id', '')}"
    return {
        "type": "product_card",
        "name": p.get("name"),
        "price": p.get("price"),
        "unit": p.get("unit", "کیلو"),
        "location": p.get("location"),
        "availability": p.get("availability", "موجود"),
        "link": link,
        "image": p.get("image"),
        "description": p.get("description"),
    }


@csrf_exempt
def chat(request: HttpRequest):
    if request.method != "POST":
        return JsonResponse({"message": WELCOME}, status=200)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Bad JSON"}, status=400)

    user_id = str(body.get("user_id", "guest"))
    text = (body.get("text") or "").strip()

    session = _get_or_create_session(user_id)

    # If first message or empty, greet
    if not text:
        _save_message(session, "assistant", WELCOME)
        return JsonResponse({"reply": WELCOME, "cards": []}, status=200)

    _save_message(session, "user", text)

    intent = detect_intent(text)

    # Tool: product search (for buy intent and also when user mentions a product)
    products = []
    context =''
    if intent["intent"] != "unknown" or intent["intent"] != "help":
        products = search_products(intent, limit=5)
    else:
        # Build RAG context to assist the LLM - اطلاعات کمکی
        context = build_context(text, k=4)

    tool_notes = []
    cards = []
    if products:
        cards = [_product_card(p) for p in products]
        tool_notes.append(f"{len(products)} محصول مرتبط یافت شد.")

    # Compose LLM messages (trim history for minimal tokens)
    history = _recent_history(session, limit=3)
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)

    user_prompt = (
        f"سوال کاربر: {text}\n\n"
        f"قصد کاربر: {intent}\n\n"
        f"اطلاعات کمکی (RAG):\n{context if context else '—'}\n\n"
        f"اگر کارت محصول همراه پاسخ می‌آید، به بازدید لینک دعوت کن."
    )
    messages.append({"role": "user", "content": user_prompt})

    reply = _llm_complete(messages)

    # Save assistant reply
    _save_message(session, "assistant", reply)

    # Add CTA when products exist
    if cards:
        reply += "\n\nبرای مشاهده جزئیات و ثبت سفارش، روی لینک هر محصول بزنید. اگر مشخصات دیگری مدنظرتان است (تناژ، بسته‌بندی، زمان تحویل)، بفرمایید تا دقیق‌تر جستجو کنم."

    return JsonResponse({
        "reply": reply,
        "intent": intent,
        "cards": cards,
        "notes": tool_notes,
    }, status=200)

