import os
import telebot
import requests
import time
import random
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=True)

# 🔥 بروكسيات
PROXIES = [
    "http://104.248.151.93:9090",
    "http://128.199.254.13:9090",
    "http://157.245.194.13:8888",
]

# 🧠 كاش + وقت انتهاء
CACHE = {}
CACHE_TTL = 300  # 5 دقائق

# 🛡️ منع السبام
USER_COOLDOWN = {}


def get_proxy():
    if PROXIES:
        proxy = random.choice(PROXIES)
        return {"http": proxy, "https": proxy}
    return None


def is_rate_limited(user_id):
    now = time.time()
    if user_id in USER_COOLDOWN:
        if now - USER_COOLDOWN[user_id] < 3:  # 3 ثواني
            return True
    USER_COOLDOWN[user_id] = now
    return False


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك في البوت")


def get_data(search_query):
    now = time.time()

    # ✅ كاش
    if search_query in CACHE:
        data, timestamp = CACHE[search_query]
        if now - timestamp < CACHE_TTL:
            return data

    url = "https://breach.vip/api/search"

    payload = {
        "term": search_query,
        "fields": ["email", "username"]
    }

    for attempt in range(3):
        try:
            response = requests.post(
                url,
                json=payload,
                proxies=get_proxy(),
                timeout=8
            )

            if response.status_code == 429:
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

            # 💾 تخزين بالكاش
            CACHE[search_query] = (msg, now)

            return msg

        except:
            continue

    return "⚠️ ضغط عالي أو حظر مؤقت، حاول بعد شوي"


def handle_search(message):
    user_id = message.from_user.id

    # 🛡️ منع السبام
    if is_rate_limited(user_id):
        bot.reply_to(message, "⏳ انتظر شوي قبل ترسل مرة ثانية")
        return

    wait = bot.reply_to(message, "🔍 جاري البحث...")

    result = get_data(message.text.strip())

    bot.edit_message_text(
        result,
        message.chat.id,
        wait.message_id
    )


@bot.message_handler(func=lambda m: True)
def search(message):
    # ⚡ تشغيل في ثريد منفصل
    threading.Thread(target=handle_search, args=(message,)).start()


print("🔥 Bot running (ULTRA PRO)...")
bot.infinity_polling()
