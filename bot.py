import telebot
import cloudscraper
import time

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

# إنشاء سكرابر متطور
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أرسل اليوزر وسأحاول تخطي الحماية وجلب بيانات انستقرام.")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, f"⏳ جاري محاولة اختراق حماية Cloudflare لليوزر `{username}`...")

    # الرابط المباشر للبيانات
    url = f"https://breach.vip/api/search/{username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Referer": "https://breach.vip/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        # إضافة تأخير بسيط لمحاكاة العنصر البشري
        time.sleep(2)
        
        res = scraper.get(url, headers=headers, timeout=25)

        if res.status_code == 403 or "<html" in res.text.lower():
            bot.edit_message_text("⚠️ فشل التخطي: الموقع يطلب حماية Cloudflare يدوية.\n\nهذا النوع من الحماية يحتاج لفتح الموقع في متصفح حقيقي لتجاوز الـ Captcha.", message.chat.id, wait_msg.message_id)
            return

        data = res.text
        if "instagram" not in data.lower():
            bot.edit_message_text(f"❌ تم الاتصال بنجاح، لكن لم يتم العثور على `Instagram` في النتائج لهذا اليوزر.", message.chat.id, wait_msg.message_id)
            return

        # استخراج بلوك الانستقرام بدقة
        lines = data.splitlines()
        extracted = []
        is_inst = False
        
        for line in lines:
            l = line.strip()
            if "instagram" in l.lower():
                is_inst = True
                extracted.append("━━━━━━━━━━━━━━━")
            elif is_inst and (".com" in l.lower() or "---" in l):
                if "instagram" not in l.lower():
                    is_inst = False
            
            if is_inst and l:
                extracted.append(l)

        final_msg = "✅ **بيانات Instagram المستخرجة:**\n\n" + "\n".join(extracted)
        bot.edit_message_text(final_msg[:4096], message.chat.id, wait_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ فني: `{str(e)}`", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
