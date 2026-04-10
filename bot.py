import telebot
from curl_cffi import requests

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث...")

    # الرابط المباشر مع تحديد النوع
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        
        # التأكد أن الرد ليس فارغاً وأن الاتصال نجح
        if response and response.status_code == 200:
            raw_text = response.text
            if not raw_text or "just a moment" in raw_text.lower():
                bot.edit_message_text("⚠️ الموقع محمي حالياً (Cloudflare). جرب يوزر ثاني أو انتظر قليلاً.", message.chat.id, wait_msg.message_id)
                return

            lines = raw_text.splitlines()
            found_results = []
            
            # منطق الفلترة (سطر بسطر)
            is_insta = False
            for i in range(len(lines)):
                line = lines[i].strip().lower()

                # إذا لقينا قسم انستقرام نبدأ نراقب الأسطر اللي تحته
                if "instagram" in line:
                    is_insta = True
                    continue

                if is_insta:
                    # سحب اليوزر من السطر التالي لكلمة username
                    if line == "username" and (i + 1) < len(lines):
                        u_val = lines[i+1].strip()
                        # البحث عن الإيميل في الأسطر القريبة التالية
                        for j in range(i+1, min(i+10, len(lines))):
                            if lines[j].strip().lower() == "email" and (j + 1) < len(lines):
                                e_val = lines[j+1].strip()
                                found_results.append(f"👤 **User:** `{u_val}`\n📧 **Email:** `{e_val}`")
                                break
                        is_insta = False # ننهي القسم الحالي ونبحث عن غيره

                # فاصل النتائج
                if "---" in line:
                    is_insta = False

            if found_results:
                # الرد بالنتائج فقط
                final_msg = "✅ **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(found_results)
                bot.reply_to(message, final_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على بيانات انستقرام لـ `{user_input}`.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("⚠️ السيرفر مضغوط أو الموقع محمي. حاول لاحقاً.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        # منع الكراش في Railway
        print(f"Error: {e}")
        bot.edit_message_text("❌ حدث خطأ غير متوقع. جرب مرة أخرى.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
