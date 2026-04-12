# استخدام نسخة بايثون متوافقة
FROM python:3.13-slim

# تثبيت المكتبات الأساسية التي يحتاجها المتصفح للعمل على نظام لينكس
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت متصفح كروم الخاص بـ playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# نسخ باقي ملفات البوت
COPY . .

# أمر تشغيل البوت
CMD ["python", "bot.py"]
