# sarvban_agent
sarvban chatbot agent
کل پروژهٔ جنگو + اتصال به MongoDB برای محصولات و Postgres/pgvector برای RAG، به‌همراه اینجستر RAG و API چت—توی کانواس گذاشتم.

توی همون جا requirements.txt، تنظیمات .env، مدل‌ها، سرویس‌های RAG/ایمبدینگ/مانگو، تشخیص نیت، و endpoint /api/chat آماده است.

فایل ingest_rag.py هم هست تا اسناد رو تیکه‌تیکه کنه، ایمبدینگ بگیره و داخل pgvector ذخیره کنه.

اقدام‌های بعدی:

pgvector رو روی Postgres فعال کن (CREATE EXTENSION IF NOT EXISTS vector;).

.env رو طبق نمونه پر کن.

دیتابیس جنگو رو مایگریت کن:
python manage.py makemigrations && python manage.py migrate

اسناد RAG رو وارد کن:
python manage.py ingest_rag ./rag_docs

برای تست:
python manage.py runserver و سپس POST به /api/chat.
