import os
import telebot
from playwright.sync_api import sync_playwright
import threading
import time

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=True)

CACHE = {}
CACHE_TTL = 300


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك في البوت")


def scrape_data(query):
    now = time.time()

    # 🧠 كاش
    if query in CACHE:
        data, t = CACHE[query]
        if now - t < CACHE_TTL:
            return data

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-setuid-sandbox",
                    "--no-first-run",
                    "--no-zygote",
                    "--single-process"
                ]
            )

            page = browser.new_page()

            # 🔥 timeout أعلى
            page.goto("https://breach.vip/", timeout=30000)

            page.fill('input[placeholder="Search term"]', query)
            page.click('button:has-text("Username")')
            page.click('button:has-text("Search")')

            # ⏳ انتظار أطول
            page.wait_for_timeout(5000)

            elements = page.query_selector_all("div.mb-4")

            results = []

            for el in elements:
                text = el.inner_text().lower()

                if "instagram" in text:
                    username = "غير متوفر"
                    email = "غير متوفر"

                    lines = text.split("\n")

                    for line in lines:
                        if "username" in line:
                            username = line.split()[-1]
                        if "email" in line:
                            email = line.split()[-1]

                    results.append((username, email))

            browser.close()

            if not results:
                return "❌ لا توجد نتائج"

            msg = "🔎 نتائج بحثك:\n\n"

            for u, e in results[:10]:
                msg += (
                    "━━━━━━━━━━━━━━━\n"
                    f"👤 {u}\n"
                    f"📧 {e}\n"
                    "━━━━━━━━━━━━━━━\n\n"
                )

            # 💾 حفظ بالكاش
            CACHE[query] = (msg, now)

            return msg

    except Exception as e:
        return "⚠️ الموقع بطيء أو السيرفر ضعيف، حاول مرة ثانية"


def handle(message):
    wait = bot.reply_to(message, "🔍 جاري البحث...")

    result = scrape_data(message.text.strip())

    try:
        bot.edit_message_text(
            result,
            message.chat.id,
            wait.message_id
        )
    except:
        bot.send_message(message.chat.id, result)


@bot.message_handler(func=lambda m: True)
def search(message):
    threading.Thread(target=handle, args=(message,)).start()


print("🔥 BOT RUNNING (FAST SCRAPER MODE)")
bot.infinity_polling()
