import telebot
from curl_cffi import requests
import re

TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص... إذا فشل هذه المرة سأخبرك بالسبب الدقيق.")

    url = f"https://breach.vip/api/search/{user_input}?type=username"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://breach.vip/"
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        raw_data = response.text
        
        # ميزة للمطور (أنت): اطبع أول 200 حرف في الكونسول عشان تشيك
        print(f"DEBUG: Response length: {len(raw_data)}")

        # البحث عن النمط بغض النظر عن المسافات أو الأسطر
        # النمط: كلمة Instagram يتبعها أي كلام لين يلقى username ثم قيمة ثم email ثم قيمة
        pattern = r"Instagram.*?username\s+([^\s\n]+).*?email\s+([^\s\n]+)"
        results = re.findall(pattern, raw_data, re.IGNORECASE | re.DOTALL)

        if results:
            insta_results = []
            for u, e in results:
                insta_results.append(f"👤 **User:** `{u}`\n📧 **Email:** `{e}`")
            
            msg = "✅ **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(insta_results)
            bot.edit_message_text(msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
        
        else:
            # إذا ما لقى بالنمط، نجرب نبحث عن الإيميلات فقط كحل أخير
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
            if emails:
                msg = "⚠️ لم أجد قسم Instagram مرتب، لكن وجدت هذه الإيميلات في الصفحة:\n\n" + "\n".join(set(emails))
                bot.edit_message_text(msg, message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text("❌ الموقع لم يرجع أي بيانات نصية (ربما حماية Cloudflare منعتني).", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ فني: {str(e)}", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
