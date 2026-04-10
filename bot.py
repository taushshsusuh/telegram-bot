import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث والفلترة بطريقة الفيديو...")

    # الرابط المباشر مع تحديد نوع البحث يوزرنيم
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
    }

    try:
        # نطلب الاستجابة كـ "نص خام" عشان نتفادى خطأ JSON اللي طلع لك
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        raw_data = response.text # هنا نأخذ النص مهما كان شكله

        if response.status_code == 200:
            # محاكاة "البحث في الصفحة" عن أي بلوك يحتوي Instagram
            # الكود بيبحث عن كلمة Instagram وبياخذ اللي تحتها لين يوصل لفاصل ---
            sections = re.findall(r"(Instagram.*?(?=-{3,}|$))", raw_data, re.DOTALL | re.IGNORECASE)
            
            final_results = []

            for section in sections:
                # تنظيف النص وتقسيمه لأسطر
                lines = [l.strip() for l in section.splitlines() if l.strip()]
                
                res_user = None
                res_email = None

                for i in range(len(lines)):
                    # إذا لقى سطر فيه كلمة username (بأي شكل) ياخذ السطر اللي بعده
                    if "username" in lines[i].lower() and (i + 1) < len(lines):
                        res_user = lines[i+1]
                    # إذا لقى سطر فيه كلمة email ياخذ السطر اللي بعده
                    if "email" in lines[i].lower() and (i + 1) < len(lines):
                        res_email = lines[i+1]

                if res_user and res_email:
                    final_results.append(f"👤 **User:** `{res_user}`\n📧 **Email:** `{res_email}`")

            if final_results:
                # حذف التكرار وإرسال النتيجة
                unique_res = list(set(final_results))
                response_msg = "📸 **نتائج Instagram المكتشفة:**\n\n" + "\n\n---\n\n".join(unique_res)
                bot.reply_to(message, response_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم أجد أقسام Instagram لهذا اليوزر في الصفحة.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"⚠️ الموقع محمي حالياً (Cloudflare). جرب لاحقاً.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ في الاتصال، حاول مرة أخرى.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
