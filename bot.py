import telebot
import cloudscraper

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

# إنشاء السكرابر
scraper = cloudscraper.create_scraper()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أرسل اليوزر لجلب بيانات Instagram.")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip()
    wait_msg = bot.reply_to(message, f"⏳ جاري فحص قاعدة البيانات لـ `{username}`...")

    # الرابط الأساسي
    url = "https://breach.vip/api/search"
    
    # محاولة إرسال الطلب كـ POST لأن الخطأ 405 غالباً بسبب الـ GET
    payload = {
        "term": username,
        "type": "username"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://breach.vip",
        "Referer": "https://breach.vip/",
        "Accept": "application/json, text/plain, */*"
    }

    try:
        # استخدام post بدلاً من get لتجنب خطأ 405
        res = scraper.post(url, data=payload, headers=headers, timeout=20)

        # إذا استمر 405، نجرب الـ GET مرة أخرى بتنسيق مختلف
        if res.status_code == 405:
            res = scraper.get(url, params=payload, headers=headers, timeout=20)

        if res.status_code != 200:
            bot.edit_message_text(f"❌ فشل الاتصال. كود الخطأ: {res.status_code}", message.chat.id, wait_msg.message_id)
            return

        text_data = res.text
        lines = text_data.splitlines()
        
        instagram_results = []
        capture = False
        temp_block = []

        for line in lines:
            line_clean = line.strip()
            if not line_clean: continue

            # اكتشاف بلوك الانستقرام
            if "instagram" in line_clean.lower():
                capture = True
                if temp_block:
                    instagram_results.append("\n".join(temp_block))
                temp_block = []

            # التوقف عند بدء خدمة أخرى
            elif capture and ("---" in line_clean or ".com" in line_clean.lower() or "social" in line_clean.lower()):
                if "instagram" not in line_clean.lower():
                    if temp_block: instagram_results.append("\n".join(temp_block))
                    temp_block = []
                    capture = False

            if capture:
                temp_block.append(line_clean)

        if capture and temp_block:
            instagram_results.append("\n".join(temp_block))

        if not instagram_results:
            bot.edit_message_text(f"❌ لم يتم العثور على بيانات انستقرام لـ `{username}`.", message.chat.id, wait_msg.message_id)
        else:
            final_output = "📸 **نتائج Instagram المستخرجة:**\n\n"
            for r in instagram_results:
                final_output += f"```\n{r}\n```\n"
            bot.edit_message_text(final_output[:4096], message.chat.id, wait_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ: `{str(e)}`", message.chat.id, wait_msg.message_id, parse_mode="Markdown")

bot.infinity_polling()
