from curl_cffi import requests
import telebot

# ضع التوكن هنا
bot = telebot.TeleBot("8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA")

@bot.message_handler(func=lambda m: True)
def search(message):
    username = message.text
    # استخدام الرابط المباشر للـ API بدل المتصفح
    url = f"https://breach.vip/api/search/{username}?type=username"
    
    try:
        # impersonate="chrome110" تجعل الموقع يظن أنك متصفح حقيقي
        response = requests.get(url, impersonate="chrome110")
        bot.reply_to(message, response.text[:2000]) # إرسال النتيجة
    except Exception as e:
        bot.reply_to(message, "حدث خطأ في الاتصال.")

bot.polling()
