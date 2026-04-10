import telebot
from curl_cffi import requests
import time

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔎 أرسل اسم المستخدم (Username) للبحث عنه بدقة.")

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    username = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, f"⚡ جاري محاكاة متصفح حقيقي للبحث عن `{username}`...")

    # الرابط الذي يستخدمه الموقع للبحث
    url = f"https://breach.vip/api/search/{username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/plain, */*",
        "Referer": "https://breach.vip/",
        "Origin": "https://breach.vip"
    }

    try:
        # استخدام impersonate لمحاكاة بصمة متصفح كروم بدقة
        session = requests.Session()
        response = session.get(url, headers=headers, impersonate="chrome120", timeout=25)

        if response.status_code == 200:
            content = response.text
            
            # التحقق إذا كانت النتيجة تحتوي على بيانات فعلية أو مجرد حماية
            if "instagram" in content.lower():
                # استخراج أسطر انستقرام فقط
                lines = content.splitlines()
                results = []
                capture = False
                for line in lines:
                    if "instagram" in line.lower():
                        capture = True
                        results.append("📸 **Instagram Found:**")
                    elif capture and (".com" in line or "---" in line):
                        if "instagram" not in line.lower(): capture = False
                    
                    if capture and line.strip():
                        results.append(f"`{line.strip()}`")

                bot.edit_message_text("\n".join(results)[:4096], message.chat.id, wait_msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على بيانات انستقرام لـ `{username}` في قاعدة البيانات.", message.chat.id, wait_msg.message_id)
        
        elif response.status_code == 403 or "cloudflare" in response.text.lower():
            bot.edit_message_text("⚠️ الموقع فعل حماية قصوى الآن. حاول مجدداً بعد دقائق أو استخدم يوزراً آخر.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"❌ خطأ من الموقع (كود {response.status_code}).", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"⚠️ حدث خطأ أثناء الاتصال: `{str(e)}`", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
