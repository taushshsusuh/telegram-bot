
import requests
import telebot
from bs4 import BeautifulSoup

# 👇 حط التوكن هنا
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "ارسل اليوزر نيم 🔍")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip()

    # 👇 حط رابط موقعك هنا
    url = f"https://breach.vip/search?username={username}"

    try:
        res = requests.get(url, timeout=10)
        results = []

        # لو الموقع يرجع JSON
        try:
            data = res.json()
            for item in data:
                if "instagram.com" in str(item).lower():
                    results.append(str(item))
        except:
            # لو الموقع HTML
            soup = BeautifulSoup(res.text, "html.parser")
            for link in soup.find_all("a", href=True):
                if "instagram.com" in link["href"]:
                    results.append(link["href"])

        if results:
            bot.reply_to(message, "\n".join(results[:10]))
        else:
            bot.reply_to(message, "❌ ما حصلت حسابات إنستقرام")

    except:
        bot.reply_to(message, "❌ صار خطأ")

bot.infinity_polling()
