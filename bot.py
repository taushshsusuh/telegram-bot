import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث...")

    # الرابط مع تحديد نوع البحث يوزرنيم
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            full_text = response.text
            
            # تقسيم النص إلى بلوكات بناءً على الفواصل "---"
            blocks = re.split(r'-{3,}', full_text)
            
            found_results = []

            for block in blocks:
                block_clean = block.strip()
                # التأكد أن البلوك يخص Instagram (سواء Selfie أو Joel أو غيرهم)
                if "instagram" in block_clean.lower():
                    # البحث عن كلمة user: أو user 
                    # والبحث عن كلمة email: أو email
                    u_match = re.search(r"user\s*[:\s]\s*([^\n\r]+)", block_clean, re.IGNORECASE)
                    e_match = re.search(r"email\s*[:\s]\s*([^\n\r]+)", block_clean, re.IGNORECASE)
                    
                    if u_match and e_match:
                        u_val = u_match.group(1).strip()
                        e_val = e_match.group(1).strip()
                        # تخزين النتيجة بتنسيق مرتب
                        found_results.append(f"👤 **User:** `{u_val}`\n📧 **Email:** `{e_val}`")

            if found_results:
                # حذف رسالة الانتظار والرد بالنتائج الصافية
                bot.delete_message(message.chat.id, wait_msg.message_id)
                final_msg = "✅ **نتائج Instagram المكتشفة:**\n\n" + "\n\n---\n\n".join(found_results)
                bot.reply_to(message, final_msg, parse_mode="Markdown")
            else:
                bot.edit_message_text(f"❌ لم أجد بيانات Instagram تحت قسم (user/email) لهذا اليوزر.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"⚠️ الموقع محمي حالياً (كود {response.status_code}).", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: `{str(e)}`", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
