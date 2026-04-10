import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث والفلترة...")

    # الرابط مع تحديد النوع كـ username بشكل قطعي
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        # استخدام بصمة متصفح حقيقي لتجاوز الحماية
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            full_text = response.text
            
            # منطق الفلترة الجديد: تقسيم النص إلى بلوكات بناءً على الفواصل
            # الموقع عادة يفصل بين النتائج بـ "---" أو أسطر فارغة
            blocks = re.split(r'-{3,}', full_text)
            
            final_results = []

            for block in blocks:
                # التأكد أن البلوك يخص Instagram
                if "instagram" in block.lower():
                    # استخراج اليوزر والإيميل باستخدام Regex مرن جداً
                    # يبحث عن كلمة username أو email ويأخذ القيمة اللي بعدها في نفس السطر
                    u_match = re.search(r"username\s*[:\s]\s*([^\n\r]+)", block, re.IGNORECASE)
                    e_match = re.search(r"email\s*[:\s]\s*([^\n\r]+)", block, re.IGNORECASE)
                    
                    if u_match and e_match:
                        user_val = u_match.group(1).strip()
                        email_val = e_match.group(1).strip()
                        final_results.append(f"👤 **Username:** `{user_val}`\n📧 **Email:** `{email_val}`")

            if final_results:
                # دمج النتائج إذا كان هناك أكثر من حساب انستقرام لنفس اليوزر
                response_msg = "✅ **تم استخراج بيانات Instagram بنجاح:**\n\n" + "\n\n---\n\n".join(final_results)
                bot.reply_to(message, response_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ بحثت في كل النتائج وما لقيت قسم 'Instagram' لليوزر `{user_input}`.", message.chat.id, wait_msg.message_id)
        
        elif response.status_code == 403:
            bot.edit_message_text("⚠️ الموقع محمي بـ Cloudflare حالياً، جرب ترسل يوزر ثاني أو انتظر شوي.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"⚠️ فشل الاتصال (كود {response.status_code}).", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ فني: `{str(e)}`", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
