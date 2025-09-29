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
from .services.mongo import search_products,search_products_by_api
from .services.rag import build_context

from django.shortcuts import render, redirect

import os

WELCOME = (
    "سلام! به پشتیبانی سروبان خوش آمدید. برای خرید یا فروش محصول کشاورزی چه کمکی لازم دارید؟"
)

# SYSTEM_PROMPT = (
#     """
#     شما دستیار فارسی‌زبان بازار محصولات کشاورزی هستید. 
#     - نیاز کاربر را (خرید/فروش/راهنمایی) تشخیص بده. 
#     - فقط از داده‌های RAG و کاتالوگ پاسخ بده. 
#     - اگر محصول موجود بود: معرفی کن و به بازدید دعوت کن (جزئیات نگو). 
#     - اگر نبود: بگو موجود نیست و نزدیک‌ترین محصول مشابه را از RAG پیشنهاد کن. 
#     - اگر باز هم نبود: از کاربر بخواه دقیق‌تر (نوع، مقدار، فصل) مشخص کند. 
#     - خارج از حوزه کشاورزی: مودبانه بگو فقط در همین زمینه کمک می‌کنی. 
#     - فقط ۳ پیام آخر کاربر را در نظر بگیر. 
#     - اگر شماره تماس خواست: پشتیبانی ۰۹۴۲۲۰۵۴۳۲۱ را بده.
#     """
# )

SYSTEM_PROMPT = (
    """
    شما دستیار فارسی‌زبان بازار محصولات کشاورزی هستید. 
    از قوانین و دستورالعمل‌های RAG استفاده کن و پاسخ را تولید کن.
    """
)

def _get_or_create_session(user_id: str) -> ChatSession:
    sess, _ = ChatSession.objects.get_or_create(user_id=user_id)
    return sess


def _save_message(session: ChatSession, role: str, content: str,product_name : str, tokens: int = 0):
    ChatMessage.objects.create(session=session, role=role, content=content, token_usage=tokens,product_name=product_name)


def _recent_history(session: ChatSession, limit: int = 3):
    msgs = ChatMessage.objects.filter(session=session).order_by("-created_at")[:limit]
    return list(reversed([{"role": m.role, "content": m.content} for m in msgs]))


def _llm_complete(messages: list[dict[str, str]]) -> str:
    # Optional LLM; can be disabled to run rule-based only
    if settings.LLM_BACKEND == "openai" and settings.OPENAI_API_KEY:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.gapgpt.app/v1",api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=settings.CHAT_LLM_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=350,
        )
        return resp.choices[0].message.content
    # Fallback: simple rule-based stitch
    return messages[-1]["content"]


def _product_card(p: Dict[str, Any]) -> Dict[str, Any]:
    link = p.get("link") or f"https://sarvban.com/market/details/{p.get('invoiceNum') or p.get('id', '')}"
    return {
        "id": p.get("id"),
        "name": p.get("title"),
        "price": p.get("price"),
        "unit": p.get("unit", "کیلو"),
        "location": p.get("location"),
        "availability": p.get("availability", "موجود"),
        "imagePath" :  f"https://sarvban.com/uploads/market/{p.get('userId')}/",
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
        _save_message(session, "assistant", WELCOME,'')
        return JsonResponse({"reply": WELCOME, "cards": []}, status=200)

    _save_message(session, "user", text,'')

    intent = detect_intent(text)

    # Tool: product search (for buy intent and also when user mentions a product)
    products = []
    context =''
    if intent["intent"] != "unknown" and intent["intent"] != "help":
        # products = search_products(intent, limit=5)
        products = search_products_by_api(intent, limit=5)
    else:
        # Build RAG context to assist the LLM - اطلاعات کمکی
        context = build_context(text, k=4)

    rag_rules = build_context(text, k=4,title='rules.txt')

    cards = []
    if products:
        cards = [_product_card(p) for p in products]

    # Compose LLM messages (trim history for minimal tokens)
    history = _recent_history(session, limit=3)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"قوانین RAG:\n{rag_rules}"},
        ]
    messages.extend(history)

    if context:
        messages.append({"role": "system", "content": f"اطلاعات کمکی (RAG):\n{context}"})   
        

    user_prompt = (
        f"سوال کاربر: {text}\n\n"
        f"قصد کاربر: {intent}\n\n"
        # f"اطلاعات کمکی (RAG):\n{context if context else '—'}\n\n"
        f"تعداد محصول یافت شده:\n{len(products)  if products else '0'}\n\n"
        f"اگر کارت محصول همراه پاسخ می‌آید، به بازدید لینک دعوت کن."
    )
    messages.append({"role": "user", "content": user_prompt})

    reply = _llm_complete(messages)

    # Save assistant reply
    _save_message(session, "assistant", reply,intent["product"])

    # Add CTA when products exist
    if cards:
        reply += "\n\nبرای مشاهده جزئیات و ثبت سفارش، روی لینک هر محصول بزنید. اگر مشخصات دیگری مدنظرتان است (تناژ، بسته‌بندی، زمان تحویل)، بفرمایید تا دقیق‌تر جستجو کنم."
    reply=reply.replace('\n\n','<br/>').strip()
    return JsonResponse({
        "reply": reply,
        "intent": intent,
        "cards": cards,
    }, status=200)



def chat_room(request):
    return render(request, 'chatbot/index.html')

