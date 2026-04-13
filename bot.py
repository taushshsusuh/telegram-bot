import os
import telebot
import requests
import time
import random

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 🔥 بروكسيات (اختياري)
PROXIES = [
    "http://104.248.151.93:9090",
    "http://128.199.254.13:9090",
]


def get_proxy():
    if PROXIES:
        proxy = random.choice(PROXIES)
        return {"http": proxy, "https": proxy}
    return None


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك في البوت")


def get_data(search_query):
    url = "https://breach.vip/api/search"

    payload = {
        "term": search_query,
        "fields": ["email", "username"]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            proxies=get_proxy(),
            timeout=10
        )

        if response.status_code == 429:
            return "⚠️ تم الحظر مؤقتًا، جرب بعد ثواني"

        if response.status_code != 200:
            return f"❌ خطأ API: {response.status_code}"

        data = response.json()
        results = data.get("results", [])

        instagram_results = [
            item for item in results
            if "instagram" in str(item).lower()
        ]

        if not instagram_results:
            return "❌ لا توجد نتائج"

        msg = "🔎 نتائج بحثك:\n\n"

        for item in instagram_results[:10]:
            username = item.get("username", "غير متوفر")
            email = item.get("email", "غير متوفر")

            msg += (
                "━━━━━━━━━━━━━━━\n"
                f"👤 {username}\n"
                f"📧 {email}\n"
                "━━━━━━━━━━━━━━━\n\n"
            )

        return msg

    except Exception as e:
        return f"❌ خطأ: {str(e)}"


@bot.message_handler(func=lambda m: True)
def search(message):
    wait = bot.reply_to(message, "🔍 جاري البحث...")

    result = get_data(message.text)

    bot.edit_message_text(
        result,
        message.chat.id,
        wait.message_id
    )


print("Bot running...")
bot.infinity_polling()
