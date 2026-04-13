import os
import telebot
import requests
import time
import random

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 🔥 بروكسيات
PROXIES = [
    "http://104.248.151.93:9090",
    "http://128.199.254.13:9090",
    "http://157.245.194.13:8888",
    "http://159.223.225.118:8888",
    "http://172.105.130.80:8888",
    "http://178.128.243.121:3128",
]


# 🔁 اختيار بروكسي شغال
def get_proxy():
    random.shuffle(PROXIES)

    for proxy in PROXIES:
        try:
            r = requests.get(
                "http://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=5
            )
            if r.status_code == 200:
                return {"http": proxy, "https": proxy}
        except:
            continue

    return None


# 🟢 start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك في البوت")


def get_data(search_query):
    url = "https://breach.vip/api/search"

    payload = {
        "term": search_query,
        "fields": ["email", "username"]
    }

    for attempt in range(5):
        try:
            time.sleep(2)

            proxy = get_proxy()

            response = requests.post(
                url,
                json=payload,
                proxies=proxy,
                timeout=15
            )

            if response.status_code == 429:
                time.sleep(5)
                continue

            if response.status_code != 200:
                continue

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

        except:
            time.sleep(3)

    return "⚠️ فشل (حظر مؤقت أو بروكسي ضعيف)"


# 🔍 البحث (بدون اشتراك)
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
