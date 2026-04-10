import telebot
from curl_cffi import requests

# 🔑 التوكن حقك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث...")

    # الرابط المباشر
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
    }

    try:
        # طلب البيانات كنص خام (Text) وليس JSON لتجنب خطأ الصورة
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        
        # تحويل الاستجابة لنص مباشرة
        raw_text = response.text
        
        if response.status_code == 200:
            lines = raw_text.splitlines()
            found_results = []
            
            # متغيرات مؤقتة لحفظ البيانات أثناء القراءة
            is_insta = False
            current_user = None
            current_email = None

            for i in range(len(lines)):
                line = lines[i].strip().lower()

                # إذا لقينا قسم انستقرام
                if "instagram" in line:
                    is_insta = True
                    continue

                if is_insta:
                    # إذا السطر فيه كلمة username، خذ السطر اللي بعده
                    if line == "username" and (i + 1) < len(lines):
                        current_user = lines[i+1].strip()
                    
                    # إذا السطر فيه كلمة email، خذ السطر اللي بعده
                    if line == "email" and (i + 1) < len(lines):
                        current_email = lines[i+1].strip()

                    # إذا اكتمل الطقم (يوزر وإيميل)
                    if current_user and current_email:
                        found_results.append(f"👤 **User:** `{current_user}`\n📧 **Email:** `{current_email}`")
                        # تصفير المتغيرات للبحث عن القسم القادم
                        current_user = None
                        current_email = None
                        is_insta = False 

                # لو دخلنا في سطر فيه "---" يعني القسم خلص
                if "---" in line:
                    is_insta = False

            if found_results:
                final_msg = "✅ **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(found_results)
                bot.reply_to(message, final_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على بيانات انستقرام لـ `{user_input}`.", message.chat.id, wait_msg.message_id)
        
        else:
            bot.edit_message_text(f"⚠️ الموقع محمي حالياً (كود {response.status_code}).", message.chat.id, wait_msg.message_id)

    except Exception as e:
        # هنا عشان لو صار خطأ ما يوقف البوت، بس يعطيك إشعار
        bot.edit_message_text(f"❌ حدث خطأ أثناء القراءة. حاول مجدداً.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
