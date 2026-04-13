import os
import telebot
import requests
import threading
import time

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=True)

CACHE = {}
CACHE_TTL = 300

USER_COOLDOWN = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك")


def is_limited(user_id):
    now = time.time()
    if user_id in USER_COOLDOWN:
        if now - USER_COOLDOWN[user_id] < 2:
            return True
    USER_COOLDOWN[user_id] = now
    return False


def get_data(query):
    now = time.time()

    # 🧠 كاش
    if query in CACHE:
        data, t = CACHE[query]
        if now - t < CACHE_TTL:
            return data

    url = "https://breach.vip/api/searches"

    payload = {
        "term": query,
        "fields": ["email", "username"]
    }

    all_results = []

    # 🔁 نحاول عدة مرات
    for _ in range(5):
        try:
            r = requests.post(url, json=payload, timeout=6)

            if r.status_code == 429:
                continue

            if r.status_code != 200:
                continue

            data = r.json()
            results = data.get("results", [])

            if results:
                all_results.extend(results)

        except:
            continue

    if not all_results:
        return "❌ لا توجد نتائج"

    # 🔍 فلترة Instagram
    ig = [x for x in all_results if "instagram" in str(x).lower()]

    # 🔥 إذا ما فيه IG يطلع أي شيء بدل ما يسكت
    if not ig:
        ig = all_results[:5]

    msg = "🔎 نتائج بحثك:\n\n"

    for item in ig[:10]:
        msg += (
            "━━━━━━━━━━━━━━━\n"
            f"👤 {item.get('username','غير متوفر')}\n"
            f"📧 {item.get('email','غير متوفر')}\n"
            "━━━━━━━━━━━━━━━\n\n"
        )

    CACHE[query] = (msg, now)

    return msg


def handle(message):
    user_id = message.from_user.id

    if is_limited(user_id):
        bot.reply_to(message, "⏳ انتظر شوي")
        return

    wait = bot.reply_to(message, "🔍 جاري البحث...")

    result = get_data(message.text.strip())

    try:
        bot.edit_message_text(result, message.chat.id, wait.message_id)
    except:
        bot.send_message(message.chat.id, result)


@bot.message_handler(func=lambda m: True)
def search(message):
    threading.Thread(target=handle, args=(message,)).start()


print("🔥 BOT RUNNING (BALANCED MODE)")
bot.infinity_polling()
