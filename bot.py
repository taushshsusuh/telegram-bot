import telebot
from curl_cffi import requests

# 🔑 توكن البوت الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🔎 أرسل اليوزر وسأستخرج لك بيانات Instagram (Selfie Recovery Exploit) فقط.")

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, f"⏳ جاري البحث عن `{user_input}` في قسم اليوزرات...")

    # الرابط المباشر للبحث مع تحديد الـ Type كـ Username
    search_url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
        "Accept": "application/json, text/plain, */*"
    }

    try:
        # استخدام curl_cffi لتخطي حماية الموقع (Cloudflare)
        response = requests.get(search_url, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            content = response.text
            
            # البحث عن قطعة الـ Instagram المحددة
            if "Instagram (Selfie Recovery Exploit)" in content:
                # تقسيم النص للوصول للجزء المطلوب فقط
                parts = content.split("Instagram (Selfie Recovery Exploit)")
                sub_content = parts[1].split("-")[0] # أخذ البيانات حتى بداية القسم التالي
                
                # تنظيف واستخراج الـ Username والـ Email
                lines = [line.strip() for line in sub_content.split('\n') if line.strip()]
                final_data = []
                for line in lines:
                    if "username" in line.lower() or "email" in line.lower():
                        final_data.append(f"🔹 {line}")

                if final_data:
                    msg = "✅ **تم العثور على بيانات Instagram:**\n\n" + "\n".join(final_data)
                    bot.edit_message_text(msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
                else:
                    bot.edit_message_text("❌ لم أتمكن من تنسيق البيانات، رغم وجود القسم.", message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على 'Selfie Recovery Exploit' لهذا اليوزر.", message.chat.id, wait_msg.message_id)
        
        else:
            bot.edit_message_text(f"⚠️ فشل الاتصال بالموقع (كود: {response.status_code}). حاول لاحقاً.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ فني: {str(e)}", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
