import telebot
from curl_cffi import requests
import re

TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص والفلترة بالتحسينات الجديدة...")

    url = f"https://breach.vip/api/search/{user_input}?type=username"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/"
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        raw_data = response.text
        
        # التحسين الذي اقترحته لمعاينة الرد في الكونسول
        print("--- بداية الرد ---")
        print(raw_data[:1000]) 
        print("--- نهاية الرد ---")

        # 1. تقسيم النص إلى بلوكات عند كل نتيجة (غالباً تفصل بينها كلمة Instagram أو فواصل)
        # استخدمنا Instagram كفاصل لضمان عزل البيانات
        sections = re.split(r"Instagram", raw_data, flags=re.IGNORECASE)
        
        insta_results = []

        for section in sections[1:]: # نبدأ من بعد أول كلمة Instagram
            # الـ Regex المحسن الذي اقترحته أنت (يلقط اليوزر والايميل حتى لو بينهم أسطر)
            results = re.findall(
                r"username\s*[:\s]+([^\n\r]+).*?email\s*[:\s]+([^\n\r]+)",
                section,
                re.IGNORECASE | re.DOTALL
            )

            for u, e in results:
                username_clean = u.strip()
                email_clean = e.strip()
                
                # التحقق أن اليوزر المطلوب موجود في النتيجة
                if user_input.lower() in username_clean.lower():
                    insta_results.append(f"👤 **User:** `{username_clean}`\n📧 **Email:** `{email_clean}`")

        if insta_results:
            msg = "✅ **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(insta_results[:10])
            bot.edit_message_text(msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
        else:
            # الحل البديل الذي اقترحته: البحث عن أي إيميل في الصفحة إذا فشلت الفلترة
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_data)
            if emails:
                msg = "⚠️ لم أجد تنسيق Instagram المعتاد، لكن هذه الإيميلات الموجودة في الصفحة:\n\n" + "\n".join(set(emails))
                bot.edit_message_text(msg, message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text("❌ لم يتم العثور على أي بيانات أو إيميلات. قد تكون الحماية مفعلة.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ فني: {str(e)}", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
