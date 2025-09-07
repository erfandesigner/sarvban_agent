# =============================
# support/services/intents.py
# =============================
from typing import Literal
import re
from openai import OpenAI
from django.conf import settings
import json
from typing import TypedDict

class Intent(TypedDict):
    intent: Literal["buyer", "seller", "help", "unknown"]
    product: str  # نام محصول یا خدمتی که کاربر اشاره کرده است

BUY_PAT = re.compile(r"\b(خرید|می‌خرم|میخوام بخرم|قیمت|سفارش|میخوام سفارش)\b")
SELL_PAT = re.compile(r"\b(فروش|می‌فروشم|میخوام بفروشم|عرضه| تامین )\b")
HELP_PAT = re.compile(r"\b(کمک|راهنمایی|سوال|پشتیبانی)\b")
SYSTEM_PROMPT="""
    در پیامی که کاربر ارسال می‌کند، نیت او را به یکی از این دسته‌ها تشخیص بده: خرید، فروش، کمک، نامشخص.
    فقط یکی از این دسته‌ها را به عنوان پاسخ بده و هیچ توضیح اضافه‌ای نده.
    اگر مطمئن نیستی، "نامشخص" را انتخاب کن. جواب را به صورت jsonو در قالب زیر برگردان:
    {"intent": "buyer" | "seller" | "help" | "unknown", "product": "نام محصول یا خدمتی که کاربر اشاره کرده است"}
    """


def detect_intent(text: str) -> Intent:
    user_prompt = text.strip()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": user_prompt} )

    client = OpenAI(base_url="https://api.gapgpt.app/v1",api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=350,
    )
    ai_res = resp.choices[0].message.content
    return json.loads(ai_res)


# if BUY_PAT.search(t):
    #     return "buy"
    # if SELL_PAT.search(t):
    #     return "sell"
    # if HELP_PAT.search(t):
    #     return "help"
    # return "unknown"

