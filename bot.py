import telebot
from curl_cffi import requests

TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def search(message):
    username = message.text.strip()
    wait = bot.reply_to(message, "🔍 جاري البحث...")
    
    # سنستخدم "جلسة" تحاكي متصفح كروم حقيقي لتجاوز الحماية
    url = f"https://breach.vip/api/search/{username}?type=username"
    
    try:
        # السر هنا في impersonate="chrome110"
        res = requests.get(url, impersonate="chrome110", timeout=10)
        
        # طباعة الرد لنرى ماذا يحدث بالضبط
        if res.status_code == 200:
            data = res.text
            # هنا الفلترة التي طلبتها للـ Instagram
            if "instagram" in data.lower():
                bot.edit_message_text(f"✅ وجدت نتائج:\n{data[:2000]}", message.chat.id, wait.message_id)
            else:
                bot.edit_message_text("❌ لم أجد بيانات Instagram لهذا اليوزر.", message.chat.id, wait.message_id)
        else:
            bot.edit_message_text(f"⚠️ الموقع رفض الطلب (كود {res.status_code})", message.chat.id, wait.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ تقني: {str(e)}", message.chat.id, wait.message_id)

bot.infinity_polling()
