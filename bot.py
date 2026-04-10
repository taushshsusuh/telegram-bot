import telebot
import cloudscraper # المكتبة السحرية لتجاوز الحماية

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

# إنشاء كائن scraper لتجاوز Cloudflare
scraper = cloudscraper.create_scraper()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أرسل اليوزر لجلب بيانات Instagram فقط.")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip()
    wait_msg = bot.reply_to(message, f"⏳ جاري فك الحماية والبحث عن `{username}`...")

    # الرابط والبارامترات
    url = "https://breach.vip/api/search"
    params = {"term": username, "type": "username"}

    try:
        # استخدام scraper بدلاً من requests
        res = scraper.get(url, params=params, timeout=20)

        if res.status_code != 200:
            bot.edit_message_text(f"❌ فشل الاتصال. كود الخطأ: {res.status_code}", message.chat.id, wait_msg.message_id)
            return

        text_data = res.text
        
        # تقسيم البيانات إلى أسطر
        lines = text_data.splitlines()
        
        instagram_results = []
        capture = False
        temp_block = []

        for line in lines:
            line_clean = line.strip()
            
            # إذا وجدنا كلمة انستقرام نبدأ السحب
            if "instagram" in line_clean.lower():
                capture = True
                if temp_block: # حفظ البلوك السابق إذا كان موجوداً
                    instagram_results.append("\n".join(temp_block))
                temp_block = []

            # إذا وجدنا بداية بلوك جديد لخدمة أخرى نتوقف عن السحب
            elif capture and (".com" in line_clean.lower() or "---" in line_clean):
                 if "instagram" not in line_clean.lower():
                    instagram_results.append("\n".join(temp_block))
                    temp_block = []
                    capture = False

            if capture and line_clean:
                temp_block.append(line_clean)

        # إضافة آخر بلوك تم سحبه
        if capture and temp_block:
            instagram_results.append("\n".join(temp_block))

        if not instagram_results:
            bot.edit_message_text(f"❌ لم يتم العثور على أي حسابات Instagram لليوزر: `{username}`", message.chat.id, wait_msg.message_id)
        else:
            # تجميع النتائج بشكل مرتب
            final_output = "✅ **نتائج انستقرام المستخرجة:**\n\n"
            for result in instagram_results:
                final_output += f"```{result}```\n\n"
            
            bot.edit_message_text(final_output[:4096], message.chat.id, wait_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ حدث خطأ أثناء التجاوز:\n`{str(e)}`", message.chat.id, wait_msg.message_id, parse_mode="Markdown")

print("Bot is running with Cloudflare Bypass...")
bot.infinity_polling()
