import telebot
from curl_cffi import requests
import os

# هذا هو التوكن الخاص بك الذي وضعته لك في مكانه الصحيح
TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def search(message):
    username = message.text.strip().replace("@", "")
    if username.startswith('/'): return
    
    wait = bot.reply_to(message, "⏳ جاري الفحص عبر الـ API...")
    
    url = f"https://breach.vip/api/search/{username}?type=username"
    
    try:
        # إرسال طلب للموقع كأننا متصفح حقيقي
        res = requests.get(url, impersonate="chrome110", timeout=15)
        
        if res.status_code == 200:
            # نحاول تحويل الرد إلى JSON
            try:
                data = res.json()
                # عرض النتيجة
                msg = f"✅ تم الاتصال بنجاح!\n\nالنتائج:\n{str(data)}"
            except:
                msg = f"❌ الموقع أرسل بيانات غير مفهومة:\n{res.text[:100]}"
        else:
            msg = f"❌ فشل الاتصال (كود: {res.status_code})\nالموقع قد يكون حظر السيرفر."
            
        bot.edit_message_text(msg, message.chat.id, wait.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ تقني: {str(e)}", message.chat.id, wait.message_id)

bot.infinity_polling()
