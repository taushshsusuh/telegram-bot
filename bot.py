import os
import telebot
from playwright.sync_api import sync_playwright
import re

# التوكن الخاص بك تم وضعه هنا مباشرة
TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"

bot = telebot.TeleBot(TOKEN)

def get_data(search_query):
    final_msg = ""
    try:
        with sync_playwright() as p:
            # تشغيل المتصفح بإعدادات مناسبة للسيرفرات
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            page = browser.new_page()

            # الدخول للموقع مع زيادة وقت الانتظار
            page.goto("https://breach.vip/", timeout=30000)

            # عملية البحث
            page.fill('input[placeholder="Search term"]', search_query)
            page.click('button:has-text("Username")')
            page.click('button:has-text("Search")')

            # انتظار ظهور النتائج
            page.wait_for_timeout(5000)

            elements = page.query_selector_all('div.mb-4')
            instagram_results = []

            for el in elements:
                text = " ".join(el.inner_text().split()).lower()

                if "instagram" in text:
                    email = "غير متوفر"
                    username = search_query

                    # استخراج الإيميل
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
                    if email_match:
                        email = email_match.group(0)

                    # استخراج اليوزر
                    username_match = re.search(r'instagram.*?(\b[a-zA-Z0-9._-]{3,}\b)', text)
                    if username_match:
                        username = username_match.group(1)

                    instagram_results.append((username, email))

            browser.close()

            if instagram_results:
                final_msg = "✅ نتائج Instagram:\n\n"
                for u, e in instagram_results:
                    final_msg += f"👤 {u}\n📧 {e}\n\n"
            else:
                final_msg = "❌ لا توجد نتائج تخص Instagram."

    except Exception as e:
        final_msg = f"❌ حدث خطأ أثناء البحث: {str(e)}"

    return final_msg

@bot.message_handler(func=lambda m: True)
def search(message):
    wait = bot.reply_to(message, "🔍 جاري البحث... يرجى الانتظار.")
    try:
        res = get_data(message.text.strip())
        bot.edit_message_text(res, message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", message.chat.id, wait.message_id)

print("✅ Bot is running...")
bot.infinity_polling()
