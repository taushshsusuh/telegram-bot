import os
import telebot
import requests

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


def get_data(search_query):
    try:
        url = "https://breach.vip/api/search"

        payload = {
            "term": search_query,
            "fields": ["email", "username"]
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            return f"❌ خطأ API: {response.status_code}"

        data = response.json()
        results = data.get("results", [])

        instagram_results = []

        for item in results:
            if "instagram" in str(item).lower():
                instagram_results.append(item)

        if not instagram_results:
            return "❌ لا توجد نتائج Instagram"

        msg = ""

        for item in instagram_results[:10]:
            username = item.get("username", "غير متوفر")
            email = item.get("email", "غير متوفر")
            source = item.get("source", "Unknown")

            msg += (
                "━━━━━━━━━━━━━━━━━━\n"
                f"📸 Instagram ({source})\n\n"
                f"👤 username : `{username}`\n"
                f"📧 email    : `{email}`\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
            )

        return msg

    except Exception as e:
        return f"❌ خطأ: {str(e)}"


@bot.message_handler(func=lambda m: True)
def search(message):
    wait = bot.reply_to(message, "🔍 جاري البحث...")

    try:
        result = get_data(message.text)

        bot.edit_message_text(
            result,
            message.chat.id,
            wait.message_id,
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ خطأ: {str(e)}",
            message.chat.id,
            wait.message_id
        )


print("Bot running...")
bot.infinity_polling()
