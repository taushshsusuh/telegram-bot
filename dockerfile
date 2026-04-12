# استخدام نسخة بايثون خفيفة ومستقرة
FROM python:3.13-slim

# تثبيت الحزم الأساسية لنظام التشغيل لضمان عمل المتصفح
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

# تحديد مسار مخصص للمتصفح لمنع مشاكل الصلاحيات
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت المتصفح والاعتمادات الخاصة به في المسار المخصص
RUN PLAYWRIGHT_BROWSERS_PATH=/ms-playwright playwright install chromium
RUN PLAYWRIGHT_BROWSERS_PATH=/ms-playwright playwright install-deps

# نسخ باقي ملفات البوت
COPY . .

# أمر تشغيل البوت
CMD ["python", "bot.py"]
