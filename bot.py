import telebot
import cloudscraper

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)
scraper = cloudscraper.create_scraper()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أرسل اليوزر وسأستخرج لك بيانات انستقرام منه.")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip().replace('@', '') # إزالة @ لو وجدت
    wait_msg = bot.reply_to(message, f"⏳ جاري البحث عن `{username}`...")

    # الرابط الذي يظهر في المتصفح للبحث المباشر
    url = f"https://breach.vip/api/search/{username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
        "Accept": "text/plain, */*"
    }

    try:
        # محاولة طلب البيانات مباشرة
        res = scraper.get(url, headers=headers, timeout=20)

        if res.status_code != 200:
            bot.edit_message_text(f"❌ فشل الاتصال. كود: {res.status_code}", message.chat.id, wait_msg.message_id)
            return

        full_text = res.text
        
        # إذا كان الموقع يرجع HTML بدلاً من نص، سنحاول استخراج النصوص منه
        if "<html" in full_text.lower():
            bot.edit_message_text("⚠️ الموقع يطلب حماية يدوية (Cloudflare). جرب يوزراً آخر أو انتظر قليلاً.", message.chat.id, wait_msg.message_id)
            return

        # فلترة النتائج - نبحث عن أي بلوك يحتوي instagram
        blocks = full_text.split('\n\n') # تقسيم النتائج لمجموعات
        instagram_info = []

        for block in blocks:
            if "instagram" in block.lower():
                instagram_info.append(block.strip())

        if not instagram_info:
            # محاولة أخيرة: البحث في الأسطر بشكل مفصل
            lines = full_text.splitlines()
            temp_lines = []
            found = False
            for line in lines:
                if "instagram" in line.lower():
                    found = True
                if found:
                    temp_lines.append(line)
                    if len(temp_lines) > 5: break # نأخذ 5 أسطر بعد كلمة انستقرام
            
            if temp_lines:
                instagram_info.append("\n".join(temp_lines))

        if instagram_info:
            result_msg = "📸 **بيانات انستقرام المكتشفة:**\n\n"
            for info in instagram_info:
                result_msg += f"```\n{info}\n```\n"
            bot.edit_message_text(result_msg[:4096], message.chat.id, wait_msg.message_id, parse_mode="Markdown")
        else:
            # لو لم يجد انستقرام، سأرسل لك أول 200 حرف من الرد لنفهم المشكلة
            bot.edit_message_text(f"❓ لم أجد كلمة انستقرام في النتائج.\n\n**بداية الرد من الموقع:**\n`{full_text[:300]}`", message.chat.id, wait_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ: `{str(e)}`", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
