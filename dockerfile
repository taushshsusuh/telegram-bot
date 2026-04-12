# استخدم صورة Python أساسية
FROM python:3.9-slim-buster

# تعيين دليل العمل داخل الحاوية
WORKDIR /app

# تثبيت متطلبات نظام التشغيل لـ Playwright
# هذه الخطوات ضرورية لضمان تشغيل Chromium بشكل صحيح
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm-dev \
    libgbm-dev \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxkbcommon0 \
    libxshmfence-dev \
    xdg-utils \
    # Chromium نفسه سيتم تنزيله بواسطة Playwright
    # ولكن هذه المكتبات ضرورية لتشغيله
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف requirements.txt وتثبيت مكتبات Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت متصفحات Playwright (Chromium في هذه الحالة)
# هذا هو الأمر الذي يحل مشكلة "Executable doesn't exist"
RUN playwright install chromium

# نسخ ملف البوت إلى دليل العمل
COPY bot.py .

# تحديد الأمر الافتراضي لتشغيل البوت
CMD ["python", "bot.py"]
