# استخدم Python أخف وأحدث
FROM python:3.11-slim

WORKDIR /app

# نسخ الملفات
COPY requirements.txt .

# تثبيت مكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت Playwright + كل dependencies للنظام (المهم 🔥)
RUN playwright install --with-deps

# نسخ باقي المشروع
COPY . .

# تشغيل البوت
CMD ["python", "bot.py"]
