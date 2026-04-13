import os
import telebot
import requests
import time
import threading
from queue import Queue

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=True)

# 🧠 كاش
CACHE = {}
CACHE_TTL = 300

# 🛡️ Queue لتنظيم الطلبات
REQUEST_QUEUE = Queue()

# 🛡️ منع السبام
USER_LAST = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك في البوت")


def fetch_api(query):
    url = "https://breach.vip/api/searches"

    payload = {
        "term": query,
        "fields": ["email", "username"],
        "wildcard": False
    }

    try:
        return requests.post(url, json=payload, timeout=6)
    except:
        return None


def process_request(chat_id, message_id, query):
    now = time.time()

    # ✅ كاش
    if query in CACHE:
        data, t = CACHE[query]
        if now - t < CACHE_TTL:
            bot.edit_message_text(data, chat_id, message_id)
            return

    # 🔁 retry ذكي
    for attempt in range(5):
        res = fetch_api(query)

        if not res:
            continue

        if res.status_code == 429:
            time.sleep(1.5)  # تهدئة بدل الحظر
            continue

        if res.status_code != 200:
            continue

        try:
            data = res.json()
        except:
            continue

        results = data.get("results", [])

        ig = [x for x in results if "instagram" in str(x).lower()]

        if not ig:
            bot.edit_message_text("❌ لا توجد نتائج", chat_id, message_id)
            return

        msg = "🔎 نتائج بحثك:\n\n"

        for item in ig[:10]:
            msg += (
                "━━━━━━━━━━━━━━━\n"
                f"👤 {item.get('username','غير متوفر')}\n"
                f"📧 {item.get('email','غير متوفر')}\n"
                "━━━━━━━━━━━━━━━\n\n"
            )

        CACHE[query] = (msg, now)

        bot.edit_message_text(msg, chat_id, message_id)
        return

    bot.edit_message_text("⚠️ ضغط عالي، حاول بعد شوي", chat_id, message_id)


# 🔥 Worker (ينفذ الطلبات بهدوء)
def worker():
    while True:
        chat_id, msg_id, query = REQUEST_QUEUE.get()
        process_request(chat_id, msg_id, query)
        time.sleep(0.7)  # أهم سطر (يمنع الحظر)
        REQUEST_QUEUE.task_done()


# تشغيل worker
threading.Thread(target=worker, daemon=True).start()


@bot.message_handler(func=lambda m: True)
def search(message):
    user_id = message.from_user.id
    now = time.time()

    # 🛡️ منع سبام
    if user_id in USER_LAST and now - USER_LAST[user_id] < 1:
        bot.reply_to(message, "⏳ انتظر شوي")
        return

    USER_LAST[user_id] = now

    wait = bot.reply_to(message, "🔍 جاري البحث...")

    # 🧠 نضيف الطلب للـ Queue بدل التنفيذ المباشر
    REQUEST_QUEUE.put((message.chat.id, wait.message_id, message.text.strip()))


print("🔥 BOT RUNNING (ANTI-LIMIT MODE)")
bot.infinity_polling()
