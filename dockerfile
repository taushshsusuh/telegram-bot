# Dockerfile
# استخدام صورة Python خفيفة الوزن كأساس
FROM python:3.9-slim-buster

# تعيين دليل العمل داخل الحاوية
WORKDIR /app

# نسخ ملف requirements.txt وتثبيت التبعيات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت متصفحات Playwright وتوابعها
# هذا الأمر سيقوم بتنزيل المتصفحات الضرورية مثل Chromium
# و '--with-deps' سيقوم بتثبيت تبعيات النظام اللازمة للمتصفحات
RUN playwright install --with-deps

# نسخ باقي ملفات المشروع إلى دليل العمل
COPY . .

# تعيين متغير البيئة لـ Playwright
# هذا يخبر Playwright أين يبحث عن المتصفحات التي تم تنزيلها
ENV PLAYWRIGHT_BROWSERS_PATH="/ms-playwright"

# الأمر الذي سيتم تشغيله عند بدء تشغيل الحاوية
CMD ["python", "bot.py"]
