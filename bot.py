import requests
import telebot

# 🔑 حط التوكن هنا
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أرسل اليوزر للبحث (سأبحث عن بيانات إنستقرام فقط)")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip()
    
    # رسالة انتظار عشان المستخدم يعرف إن البوت شغال
    wait_msg = bot.reply_to(message, "⏳ جارٍ البحث في قاعدة البيانات...")

    # 🔥 رابط الموقع
    url = f"https://breach.vip/api/search/{username}"

    # تحسين الهيدرز لمحاكاة متصفح حقيقي (لتجنب الحظر)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/plain, */*",
        "Referer": "https://breach.vip/"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)

        # إذا الموقع رجع كود حماية (403 أو 401)
        if res.status_code == 403 or res.status_code == 401:
            bot.edit_message_text("❌ الموقع محمي بواسطة Cloudflare أو يطلب تسجيل دخول.", message.chat.id, wait_msg.message_id)
            return

        if res.status_code != 200:
            bot.edit_message_text(f"❌ فشل الاتصال. كود الخطأ: {res.status_code}", message.chat.id, wait_msg.message_id)
            return

        text = res.text
        
        # التأكد إذا كان الرد HTML (يعني صفحة حماية) وليس بيانات
        if "<!doctype html" in text.lower() or "<html" in text.lower():
            bot.edit_message_text("❌ الموقع أرجع صفحة حماية وليس بيانات. جرب لاحقاً.", message.chat.id, wait_msg.message_id)
            return

        # فلترة النتائج
        lines = text.splitlines()
        results_list = []
        
        for line in lines:
            if "instagram" in line.lower():
                results_list.append(line.strip())

        if not results_list:
            bot.edit_message_text(f"❌ لم يتم العثور على بيانات إنستقرام لليوزر: {username}", message.chat.id, wait_msg.message_id)
            return

        # تجميع النتائج وعرضها (بحد أقصى 15 نتيجة لتجنب طول الرسالة)
        final_result = "\n".join(results_list[:15])
        bot.edit_message_text(f"✅ نتائج إنستقرام لـ (@{username}):\n\n`{final_result}`", 
                             message.chat.id, wait_msg.message_id, parse_mode="Markdown")

    except requests.exceptions.Timeout:
        bot.edit_message_text("⚠️ انتهى وقت المحاولة (Timeout). الموقع بطيء جداً.", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ حدث خطأ غير متوقع:\n`{str(e)}`", message.chat.id, wait_msg.message_id, parse_mode="Markdown")

print("Bot is running...")
bot.infinity_polling()
