

import telebot
from playwright.sync_api import sync_playwright
import re

TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

def get_instagram_data(username):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        try:
            page.goto("https://breach.vip/", timeout=60000)

            # نكتب اليوزر
            page.fill("input", username)

            # نضغط بحث
            page.keyboard.press("Enter")

            page.wait_for_timeout(5000)

            # نجيب كل النص من الصفحة
            content = page.content()

            # فلترة Instagram
            matches = re.findall(
                r"(Instagram.*?username\s*[:\s]+([^\n<]+).*?email\s*[:\s]+([^\n<]+))",
                content,
                re.IGNORECASE | re.DOTALL
            )

            for full, user, email in matches:
                results.append(
                    f"📱 Instagram\n👤 {user.strip()}\n📧 {email.strip()}"
                )

        except Exception as e:
            print("ERROR:", e)

        finally:
            browser.close()

    return results


@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🔥 ارسل يوزر")

@bot.message_handler(func=lambda m: True)
def search(msg):
    username = msg.text.strip().replace("@", "")
    wait = bot.reply_to(msg, "⏳ جاري البحث القوي...")

    try:
        data = get_instagram_data(username)

        if data:
            bot.edit_message_text(
                "✅ النتائج:\n\n" + "\n\n---\n\n".join(data[:5]),
                msg.chat.id,
                wait.message_id
            )
        else:
            bot.edit_message_text(
                "❌ ما حصلت Instagram",
                msg.chat.id,
                wait.message_id
            )

    except:
        bot.edit_message_text(
            "❌ فشل تشغيل المتصفح (Railway يحتاج ضبط)",
            msg.chat.id,
            wait.message_id
        )

bot.infinity_polling()
