import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري استخراج بيانات Instagram من الـ API الخام...")

    url = f"https://breach.vip/api/search/{user_input}?type=username"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/"
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        raw_data = response.text
        
        # طباعة أول جزء من البيانات للتأكد (ستظهر في Railway Logs)
        print("--- RAW DATA PREVIEW ---")
        print(raw_data[:1000])

        # 🎯 الحل الذي اقترحته: البحث عن النمط الذي يحتوي instagram واليوزر والايميل معاً
        # هذا النمط يبحث عن كلمة instagram ثم أي كلام، ثم username، ثم email
        pattern = r"(instagram[^\n]*).*?username\s*[:\s]+([^\n\r]+).*?email\s*[:\s]+([^\n\r]+)"
        results = re.findall(pattern, raw_data, re.IGNORECASE | re.DOTALL)

        insta_results = []

        for site_info, u, e in results:
            u_clean = u.strip()
            e_clean = e.strip()
            
            # التأكد أن النتيجة تخص اليوزر المطلوب (فلترة إضافية لضمان الدقة)
            if user_input.lower() in u_clean.lower():
                insta_results.append(f"📱 **Instagram Info:** `{site_info.strip()}`\n👤 **User:** `{u_clean}`\n📧 **Email:** `{e_clean}`")

        if insta_results:
            # مسح التكرار وإرسال النتائج
            unique_res = list(set(insta_results))
            msg = "✅ **تم بنجاح! هذي نتائج Instagram من البيانات الخام:**\n\n" + "\n\n---\n\n".join(unique_res)
            bot.edit_message_text(msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
        else:
            # إذا فشل النمط المركب، نجرب البحث عن أي بلوك فيه كلمة instagram فقط
            # كحل أخير لنعرف أين المشكلة
            if "instagram" in raw_data.lower():
                bot.edit_message_text("❌ كلمة Instagram موجودة في البيانات، لكن النمط (User/Email) لم يتطابق. الموقع غير ترتيب الكلمات.", message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ الـ API لم يرجع أي ذكر لـ Instagram لليوزر `{user_input}`.", message.chat.id, wait_msg.message_id)

    except Exception as ex:
        bot.edit_message_text(f"❌ خطأ في الاتصال بالسيرفر.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
