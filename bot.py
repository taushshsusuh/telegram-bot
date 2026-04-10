import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    # رسالة بسيطة جداً كما طلبت
    wait_msg = bot.reply_to(message, "⏳ جاري البحث...")

    # الرابط الأساسي للبحث
    url = "https://breach.vip/api/search"
    
    # هنا السر: إرسال الـ Params لتحديد نوع البحث كـ Username
    params = {
        "term": user_input,
        "type": "username" # محاكاة اختيار Username من القائمة
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        # استخدام curl_cffi لتجاوز الحماية (Cloudflare)
        response = requests.get(url, params=params, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            full_text = response.text
            
            # الفلترة: نبحث عن قسم الانستقرام Selfie Recovery
            target_header = "Instagram (Selfie Recovery Exploit)"
            
            if target_header in full_text:
                # قص الجزء اللي يخص انستقرام فقط
                start_pos = full_text.find(target_header)
                section_text = full_text[start_pos:start_pos + 800] # نأخذ مساحة كافية للبيانات
                
                # استخراج اليوزر والايميل باستخدام Regex دقيق
                user_match = re.search(r"username\s+([^\n\r]+)", section_text, re.IGNORECASE)
                email_match = re.search(r"email\s+([^\n\r]+)", section_text, re.IGNORECASE)

                if user_match and email_match:
                    found_user = user_match.group(1).strip()
                    found_email = email_match.group(1).strip()

                    # الرد النهائي: يوزر وايميل فقط كما طلبت
                    final_msg = f"👤 **Username:** `{found_user}`\n📧 **Email:** `{found_email}`"
                    bot.reply_to(message, final_msg, parse_mode="Markdown")
                    
                    # حذف رسالة "جاري البحث" عشان الشات يبقى نظيف
                    bot.delete_message(message.chat.id, wait_msg.message_id)
                else:
                    bot.edit_message_text("❌ القسم موجود ولكن البيانات بداخله غير واضحة.", message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text("❌ لم يتم العثور على سجلات Instagram (Selfie) لهذا اليوزر.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"⚠️ الموقع محمي حالياً (كود {response.status_code}). جرب لاحقاً.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ: {str(e)}", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
