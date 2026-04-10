
import requests
import telebot

# 🔑 حط التوكن هنا
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 ارسل اليوزر نيم للبحث")


@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip()

    # 🔥 رابط الموقع (API)
    url = f"https://breach.vip/api/search/{username}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            try:
                data = res.json()
            except:
                bot.reply_to(message, "❌ الموقع رجع بيانات غير مفهومة")
                return

            if not data:
                bot.reply_to(message, "❌ لا يوجد بيانات")
            else:
                # ترتيب النتائج
                result = ""

                for item in data[:10]:  # أول 10 نتائج فقط
                    result += f"📧 Email: {item.get('email','-')}\n"
                    result += f"👤 User: {item.get('username','-')}\n"
                    result += f"🔑 Pass: {item.get('password','-')}\n"
                    result += f"{'-'*20}\n"

                bot.reply_to(message, f"✅ النتائج:\n\n{result}")

        else:
            bot.reply_to(message, f"❌ فشل الاتصال (Status: {res.status_code})")

    except Exception as e:
        bot.reply_to(message, f"⚠️ خطأ:\n{e}")


print("Bot is running...")
bot.infinity_polling()
