import telebot
from curl_cffi import requests
import os

# التوكن الجديد الذي أرسلته
TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أهلاً بك! أرسل اليوزر للبحث عن بياناته.")

@bot.message_handler(func=lambda m: True)
def search(message):
    username = message.text.strip().replace("@", "")
    wait = bot.reply_to(message, "⏳ جاري الاتصال بالـ API الرسمي...")

    # الرابط الأساسي للبحث بناءً على تحليل OpenAPI
    url = f"https://breach.vip/api/search/{username}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        # استخدام impersonate لتجنب كشف البوت
        res = requests.get(url, headers=headers, impersonate="chrome110", timeout=20)
        
        if res.status_code == 200:
            data = res.json()
            
            # هنا نقوم بفلترة النتائج التي تحتوي على كلمة instagram
            # إذا كان الـ API يرجع قائمة من النتائج
            results_found = []
            
            # تحويل البيانات إلى نص للبحث داخلها
            data_str = str(data).lower()
            
            if "instagram" in data_str:
                # محاولة استخراج اليوزر والايميل إذا وجدت
                msg = "✅ نتائج Instagram الموجودة:\n\n"
                # (ملاحظة: هيكل الـ JSON يعتمد على ما يرجعه الموقع فعلياً)
                msg += f"```json\n{data}\n```" # عرض البيانات الخام للتأكد من الهيكل
            else:
                msg = "❌ لا توجد نتائج مرتبطة بـ Instagram لهذا اليوزر."
        
        else:
            msg = f"❌ خطأ في الاتصال (كود: {res.status_code}). الموقع قد يكون قام بحظر السيرفر."

        bot.edit_message_text(msg, message.chat.id, wait.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ تقني: {str(e)}", message.chat.id, wait.message_id)

bot.infinity_polling()
