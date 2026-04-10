import telebot
import cloudscraper
import json

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

    url = "https://breach.vip/api/search"
    
    # البيانات بصيغة ديكشنري ليتم تحويلها لـ JSON
    payload = {
        "term": username,
        "type": "username"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json", # ضروري جداً لتجنب خطأ 400
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://breach.vip",
        "Referer": "https://breach.vip/"
    }

    try:
        # إرسال البيانات كـ JSON باستخدام json=payload
        res = scraper.post(url, json=payload, headers=headers, timeout=20)

        # إذا الموقع لا يزال يرفض الـ POST، سنجرب آخر محاولة بالـ GET المنسق
        if res.status_code != 200:
            res = scraper.get(f"{url}/{username}", headers=headers, timeout=20)

        if res.status_code != 200:
            bot.edit_message_text(f"❌ فشل الاتصال النهائي. كود الخطأ: {res.status_code}\nالموقع قد يكون غير متاح حالياً للبوتات.", message.chat.id, wait_msg.message_id)
            return

        text_data = res.text
        
        # الفلترة الذكية لاستخراج انستقرام فقط
        lines = text_data.splitlines()
        instagram_results = []
        current_block = []
        capture = False

        for line in lines:
            line_s = line.strip()
            if not line_s: continue

            # بدء بلوك انستقرام
            if "instagram" in line_s.lower():
                if capture and current_block:
                    instagram_results.append("\n".join(current_block))
                capture = True
                current_block = [line_s]
            
            # نهاية البلوك (إذا وجدنا خدمة أخرى)
            elif capture and ("---" in line_s or ".com" in line_s.lower()):
                if "instagram" not in line_s.lower():
                    instagram_results.append("\n".join(current_block))
                    current_block = []
                    capture = False
            
            elif capture:
                current_block.append(line_s)

        # إضافة آخر نتيجة
        if capture and current_block:
            instagram_results.append("\n".join(current_block))

        if not instagram_results:
            bot.edit_message_text(f"❌ لم يتم العثور على حساب انستقرام لـ `{username}` (قد تكون البيانات لخدمات أخرى).", message.chat.id, wait_msg.message_id)
        else:
            final_output = "📸 **نتائج Instagram المستخرجة:**\n\n"
            for r in instagram_results:
                final_output += f"```\n{r}\n```\n"
            bot.edit_message_text(final_output[:4096], message.chat.id, wait_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ غير متوقع: `{str(e)}`", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
