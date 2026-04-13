import os
import telebot
import requests
import time
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=True)

# 🧠 كاش
CACHE = {}
CACHE_TTL = 300  # 5 دقائق

# 🛡️ منع السبام
USER_COOLDOWN = {}


def is_rate_limited(user_id):
    now = time.time()
    if user_id in USER_COOLDOWN:
        if now - USER_COOLDOWN[user_id] < 2:
            return True
    USER_COOLDOWN[user_id] = now
    return False


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك في البوت")


def get_data(search_query):
    now = time.time()

    # ✅ كاش (يرجع فورًا)
    if search_query in CACHE:
        data, timestamp = CACHE[search_query]
        if now - timestamp < CACHE_TTL:
            return data

    url = "https://breach.vip/api/search"

    payload = {
        "term": search_query,
        "fields": ["email", "username"]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=6
        )

        if response.status_code == 429:
            return "⚠️ ضغط عالي، جرب بعد ثواني"

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

        # 💾 حفظ في الكاش
        CACHE[search_query] = (msg, now)

        return msg

    except Exception as e:
        return "⚠️ خطأ مؤقت، حاول مرة ثانية"


def handle_search(message):
    user_id = message.from_user.id

    if is_rate_limited(user_id):
        bot.reply_to(message, "⏳ انتظر شوي")
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
    threading.Thread(target=handle_search, args=(message,)).start()


print("⚡ Bot running FAST MODE...")
bot.infinity_polling()
