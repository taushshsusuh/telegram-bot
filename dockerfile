# استخدم صورة Python خفيفة كقاعدة
FROM python:3.9-slim-buster

# تعيين دليل العمل داخل الحاوية
WORKDIR /app

# تثبيت متطلبات نظام التشغيل لـ Playwright
# تتضمن Chromium والمتطلبات الأخرى
RUN apt-get update && apt-get install -y \
    chromium \
    python3-pip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# تثبيت Playwright driver
RUN playwright install-deps

# نسخ ملفات المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات التطبيق
COPY . .

# تشغيل البوت
CMD ["python", "bot.py"]
