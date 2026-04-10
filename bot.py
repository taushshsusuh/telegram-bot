import telebot
from curl_cffi import requests # مكتبة أسرع وأقوى للتخطي

TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def search(message):
    username = message.text.strip()
    wait_msg = bot.reply_to(message, "⚡ جاري البحث السريع...")
    
    url = f"https://breach.vip/api/search/{username}"
    
    try:
        # محاكاة متصفح كروم حقيقي بأحدث إصدار
        res = requests.get(url, impersonate="chrome110", timeout=10)
        
        if res.status_code == 200:
            data = res.text
            if "instagram" in data.lower():
                # (هنا نضع نفس منطق استخراج البيانات السابق)
                bot.edit_message_text("✅ تم العثور على البيانات!", message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text("❌ لم يتم العثور على انستقرام.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"⚠️ الموقع محمي (كود {res.status_code}). تحتاج لبروكسي سكني.", message.chat.id, wait_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
