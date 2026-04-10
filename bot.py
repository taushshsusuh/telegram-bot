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

    # طلب البحث مع التأكيد على نوع اليوزر
    search_url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/"
    }

    try:
        # تجاوز الحماية
        response = requests.get(search_url, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            full_text = response.text
            
            # 1. تحديد القسم المطلوب بدقة
            target_header = "Instagram (Selfie Recovery Exploit)"
            
            if target_header in full_text:
                # 2. قص النص لتبدأ من القسم المطلوب فقط وتجاهل ما قبله
                start_pos = full_text.find(target_header)
                # نأخذ بلوك كافي من البيانات بعد العنوان (مثلاً 1000 حرف)
                relevant_data = full_text[start_pos:start_pos + 1000]
                
                # 3. البحث عن أول username وأول email يظهرون بوضوح في هذا القسم
                # نبحث عن السطر اللي يبدأ بـ username ثم فراغ ثم القيمة
                username_match = re.search(r"username\s+([^\n\r]+)", relevant_data, re.IGNORECASE)
                email_match = re.search(r"email\s+([^\n\r]+)", relevant_data, re.IGNORECASE)

                if username_match and email_match:
                    found_user = username_match.group(1).strip()
                    found_email = email_match.group(1).strip()

                    # الرد باليوزر والايميل فقط رداً على رسالة المستخدم
                    final_response = f"👤 **Username:** `{found_user}`\n📧 **Email:** `{found_email}`"
                    bot.reply_to(message, final_response, parse_mode="Markdown")
                    
                    # حذف رسالة "جاري البحث" لتنظيف الشات
                    bot.delete_message(message.chat.id, wait_msg.message_id)
                else:
                    bot.edit_message_text("❌ وجدنا القسم ولكن لم نجد بيانات داخله.", message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text("❌ لم يتم العثور على سجلات Instagram لهذا اليوزر.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"⚠️ خطأ في الاتصال بالموقع (كود {response.status_code})", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ: {str(e)}", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
