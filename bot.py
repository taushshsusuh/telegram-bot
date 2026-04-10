import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري الفلترة النهائية... تكفى هالمرة يضبط")

    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        raw_data = response.text

        if response.status_code == 200:
            # تقسيم الصفحة بناءً على أي شيء يشبه الفاصل
            sections = re.split(r'-{3,}|Instagram', raw_data, flags=re.IGNORECASE)
            
            final_results = []

            for section in sections:
                # نبحث عن نمط: كلمة username بعدها أي كلام، ثم كلمة email بعدها أي كلام
                # هذا النمط يتجاهل إذا كانت في سطر واحد أو سطرين
                user_match = re.search(r"username\s*[\s\n\r:]+([^\n\r\-]+)", section, re.IGNORECASE)
                email_match = re.search(r"email\s*[\s\n\r:]+([^\n\r\-]+)", section, re.IGNORECASE)

                if user_match and email_match:
                    u_val = user_match.group(1).strip()
                    e_val = email_match.group(1).strip()
                    
                    # نفلتر فقط النتائج اللي لها علاقة باليوزر اللي بحثت عنه أو فيها ريحة انستقرام
                    final_results.append(f"👤 **User:** `{u_val}`\n📧 **Email:** `{e_val}`")

            if final_results:
                # إزالة التكرار
                unique_res = list(set(final_results))
                response_msg = "✅ **هذي البيانات اللي قدرت أصيدها:**\n\n" + "\n\n---\n\n".join(unique_res)
                bot.reply_to(message, response_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ الموقع رجع بيانات بس مالقيت فيها 'username' و 'email' تحت بعض.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("⚠️ حماية Cloudflare قوية الحين، انتظر 5 دقائق وجرب.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ، الموقع شكله قفل الطلبات حالياً.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
