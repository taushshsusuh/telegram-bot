

import requests
import telebot
from bs4 import BeautifulSoup

TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "ارسل اليوزر نيم 🔍")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text

    url = f"https://breach.vip/search?username={username}"

    try:
        res = requests.get(url)
        results = []

        try:
            data = res.json()
            for item in data:
                if "instagram.com" in str(item).lower():
                    results.append(str(item))
        except:
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")

            for link in links:
                href = link.get("href")
                if href and "instagram.com" in href:
                    results.append(href)

        if results:
            bot.reply_to(message, "\n".join(results[:10]))
        else:
            bot.reply_to(message, "❌ ما حصلت نتائج")

    except:
        bot.reply_to(message, "❌ صار خطأ")

bot.infinity_polling()
