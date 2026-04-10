import telebot
from curl_cffi import requests
import re
import time

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

def fetch_data(username):
    # استخدام رابط البحث المباشر مع تحديد النوع
    url = f"https://breach.vip/api/search/{username}?type=username"
    
    # محاكاة بصمة متصفح أندرويد (غالباً ما تكون الحماية فيها أخف)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
        "Accept": "text/plain, */*",
        "Referer": "https://breach.vip/",
        "Origin": "https://breach.vip",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        # المحاولة بدون بروكسي أولاً باستخدام بصمة متطورة
        # إذا كنت على Railway، قد تحتاج لمحاولة الطلب أكثر من مرة
        session = requests.Session()
        res = session.get(url, headers=headers, impersonate="chrome110", timeout=25)
        
        if res.status_code == 200:
            if "just a moment" in res.text.lower():
                return "PROTECTED" # الموقع كشف البوت
            return res.text
        return None
    except:
        return None

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    username = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث...")

    data = fetch_data(username)

    if data == "PROTECTED":
        bot.edit_message_text("⚠️ الموقع يطلب تحقق بشري حالياً. جرب بعد قليل.", message.chat.id, wait_msg.message_id)
        return
    elif not data:
        bot.edit_message_text("❌ فشل الاتصال بالموقع. تأكد من أن السيرفر يعمل.", message.chat.id, wait_msg.message_id)
        return

    # الفلترة الشاملة لـ Joel و Selfie وجميع أنواع الانستقرام
    # نبحث عن الكتل التي تبدأ بـ Instagram وتنتهي بـ ---
    results = []
    # استخراج كافة الكتل التي تحتوي على كلمة instagram
    sections = re.findall(r"(Instagram.*?(?=---|$))", data, re.DOTALL | re.IGNORECASE)

    for section in sections:
        # استخراج اليوزر والايميل من كل كتلة
        u_match = re.search(r"username\s+([^\n\r]+)", section, re.IGNORECASE)
        e_match = re.search(r"email\s+([^\n\r]+)", section, re.IGNORECASE)
        
        if u_match and e_match:
            user = u_match.group(1).strip()
            email = e_match.group(1).strip()
            results.append(f"👤 **User:** `{user}`\n📧 **Email:** `{email}`")

    if results:
        # الرد بالنتائج فقط (يوزر وايميل)
        final_msg = "✅ **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(results)
        bot.reply_to(message, final_msg, parse_mode="Markdown")
        bot.delete_message(message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text(f"❌ لم يتم العثور على بيانات Instagram لـ `{username}`.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
