import telebot
from curl_cffi import requests
import re

TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص الدقيق للأسطر...")

    url = f"https://breach.vip/api/search/{user_input}?type=username"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        raw_data = response.text

        # التأكد من وجود كلمة انستقرام في الصفحة كاملة
        if "instagram" in raw_data.lower():
            
            # 1. تقسيم النص إلى بلوكات عند كل كلمة Instagram
            # عشان نضمن إننا نسحب اليوزر والإيميل اللي "تحت" كلمة انستقرام مو غيرها
            sections = re.split(r"Instagram", raw_data, flags=re.IGNORECASE)
            
            insta_results = []

            for section in sections[1:]: # نتجاهل النص اللي قبل أول كلمة Instagram
                
                # 2. ريجكس (Regex) عبقري: 
                # يبحث عن كلمة username ثم يتجاهل أي مسافات أو أسطر \s* # ثم يلقط الكلمة اللي بعدها مباشرة (اليوزر)
                u_match = re.search(r"username\s+([^\s]+)", section, re.IGNORECASE)
                e_match = re.search(r"email\s+([^\s]+)", section, re.IGNORECASE)

                if u_match and e_match:
                    u = u_match.group(1).strip()
                    e = e_match.group(1).strip()
                    
                    # التحقق أن اليوزر هو نفسه اللي بحثنا عنه (فلترة إضافية)
                    if user_input.lower() in u.lower():
                        insta_results.append(f"👤 `{u}`\n📧 `{e}`")

            if insta_results:
                msg = "✅ **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(insta_results[:5])
                bot.edit_message_text(msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ القسم موجود، لكن لم أستطع سحب اليوزر والايميل منه (تنسيق مختلف).", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ لم يتم العثور على كلمة Instagram في كامل الصفحة.", message.chat.id, wait_msg.message_id)

    except Exception as ex:
        bot.edit_message_text("❌ حدث خطأ فني، الموقع قد يكون حظر الطلب.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
