import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    # رسالة انتظار بسيطة كما طلبت
    wait_msg = bot.reply_to(message, "⏳ جاري البحث...")

    # طلب البحث مع تحديد النوع كـ Username
    search_url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/"
    }

    try:
        # محاكاة المتصفح لتخطي صفحة الحماية
        response = requests.get(search_url, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            full_text = response.text
            
            # التأكد من وجود قسم الانستقرام المطلوب
            target_section = "Instagram (Selfie Recovery Exploit)"
            if target_section in full_text:
                # استخراج الجزء الذي يلي القسم المطلوب مباشرة
                start_index = full_text.find(target_section)
                # نأخذ 500 حرف بعد العنوان لضمان شمول اليوزر والايميل
                relevant_part = full_text[start_index:start_index+500]

                # استخدام Regex لاستخراج اليوزر والايميل من النص
                found_user = re.search(r"username\s+(.*)", relevant_part)
                found_email = re.search(r"email\s+([\w\.-]+@[\w\.-]+)", relevant_part)

                if found_user and found_email:
                    res_username = found_user.group(1).strip()
                    res_email = found_email.group(1).strip()

                    # الرد النهائي بالبيانات فقط
                    result_msg = f"✅ **تم العثور على البيانات:**\n\n" \
                                 f"👤 **Username:** `{res_username}`\n" \
                                 f"📧 **Email:** `{res_email}`"
                    bot.edit_message_text(result_msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
                else:
                    bot.edit_message_text("❌ القسم موجود ولكن لم أستطع استخراج البيانات بدقة.", message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على `{user_input}` في قسم Instagram بالموقع.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("⚠️ فشل في الوصول للموقع، قد تكون الحماية مفعلة حالياً.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
