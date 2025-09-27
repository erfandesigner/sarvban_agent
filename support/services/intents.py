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
    intent: Literal["buy", "sell", "help", "unknown"]
    product: str  # نام محصول یا خدمتی که کاربر اشاره کرده است

BUY_PAT = re.compile(r"\b(خرید|می‌خرم|میخوام بخرم|قیمت|سفارش|میخوام سفارش)\b")
SELL_PAT = re.compile(r"\b(فروش|می‌فروشم|میخوام بفروشم|عرضه| تامین )\b")
HELP_PAT = re.compile(r"\b(کمک|راهنمایی|سوال|پشتیبانی)\b")
SYSTEM_PROMPT={
        "Objective": "تشخیص نیت کاربر و استخراج اطلاعات مربوط به محصول و ویژگی‌های آن از متن پیام.",
        "Persona_Details": {
            "Role": "سیستم پردازش زبان طبیعی",
            "Focus": "تحلیل متن فارسی برای دسته‌بندی نیت و شناسایی محصول"
        },
        "Task_Instructions": {
            "1": "نیت کاربر را از متن به یکی از دسته‌های زیر تشخیص بده: 'buy' (خرید)، 'sell' (فروش)، 'help' (کمک)، 'unknown' (نامشخص).",
            "2": "فقط یکی از دسته‌ها را انتخاب کن و هیچ توضیح اضافه‌ای ارائه نده.",
            "3": "نام محصول را جدا کن و هرگونه شهر، استان یا ویژگی را حذف کن. رنگ رو حذف نکن.",
            "4": "کلمات مرتبط با ویژگی‌ها مثل 'صادراتی' را در بخش 'info' ذخیره کن.",
            "5": "اگر متن درباره 'سروبان' بود، فیلد محصول را خالی بگذار.",
            "6": "اگر مطمئن نیستی، دسته '' خالی را انتخاب کن."
        },
        "Response_Format": {
            "intent": "buy | sell | help | unknown",
            "product": "نام محصول یا خدمت",
            "info": "صفت یا ویژگی محصول مثل صادراتی | گلخانه ای | سوپری | صنعتی | میدانی | کارخانه ای",
            "province": "نام استان ایران",
            "cat": "دسته بندی محصول مثل باغی | زراعی | نهاده | گیاهان دارویی",
        }
    }



def detect_intent(text: str) -> Intent:
    user_prompt = text.strip()
    messages = [
        {
            "role": "system",
            "content": json.dumps(SYSTEM_PROMPT, ensure_ascii=False)
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]


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

