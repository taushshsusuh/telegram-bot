
import requests
import telebot

# 🔑 حط التوكن هنا
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 ارسل اليوزر للبحث (راح أطلع لك إنستقرام فقط)")


@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip()

    # 🔥 رابط الموقع
    url = f"https://breach.vip/api/search/{username}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            bot.reply_to(message, "❌ فشل الاتصال بالموقع")
            return

        text = res.text.lower()

        # ❌ إذا الموقع محمي
        if "<html" in text:
            bot.reply_to(message, "❌ الموقع محمي أو ما يسمح للبوت")
            return

        # ❌ إذا ما فيه إنستقرام
        if "instagram" not in text:
            bot.reply_to(message, "❌ ما حصلت حسابات انستقرام")
            return

        # 🔥 فلترة نتائج إنستقرام
        lines = res.text.split("\n")
        result = ""
        capture = False

        for line in lines:
            if "instagram" in line.lower():
                capture = True

            if capture:
                result += line + "\n"

                # نوقف بعد عدد أسطر معين
                if result.count("\n") > 20:
                    break

        bot.reply_to(message, f"📸 نتائج انستقرام:\n\n{result[:4000]}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ خطأ:\n{e}")


print("Bot is running...")
bot.infinity_polling()
