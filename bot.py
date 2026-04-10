import telebot
from curl_cffi import requests

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث والفلترة...")

    # الرابط المباشر للبحث بنوع يوزرنيم
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            lines = response.text.splitlines()
            
            found_data = []
            is_instagram_section = False
            temp_user = None
            temp_email = None

            for i in range(len(lines)):
                line = lines[i].strip().lower()

                # 1. اكتشاف بداية قسم الانستقرام (أي نوع)
                if "instagram" in line:
                    is_instagram_section = True
                    continue

                if is_instagram_section:
                    # 2. إذا وجدنا كلمة username، القيمة في السطر التالي
                    if line == "username" and (i + 1) < len(lines):
                        temp_user = lines[i+1].strip()
                    
                    # 3. إذا وجدنا كلمة email، القيمة في السطر التالي
                    if line == "email" and (i + 1) < len(lines):
                        temp_email = lines[i+1].strip()

                    # 4. إذا اكتمل اليوزر والايميل، نحفظهم ونصفر البحث للقسم القادم
                    if temp_user and temp_email:
                        found_data.append(f"👤 **Username:** `{temp_user}`\n📧 **Email:** `{temp_email}`")
                        temp_user = None
                        temp_email = None
                        is_instagram_section = False # ننتظر قسم انستقرام جديد

                # إذا واجهنا فاصل كبير أو خدمة أخرى، نوقف البحث في القسم الحالي
                if "---" in line or (".com" in line and "instagram" not in line):
                    is_instagram_section = False

            if found_data:
                final_msg = "📸 **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(found_data)
                bot.reply_to(message, final_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على يوزر وإيميل تحت قسم Instagram لـ `{user_input}`.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"⚠️ الموقع محمي حالياً (كود {response.status_code}).", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ فني: `{str(e)}`", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
