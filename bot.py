import requests
import telebot

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أرسل اليوزر للبحث عن اختراقات انستقرام فقط")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip()
    wait_msg = bot.reply_to(message, f"⏳ جاري البحث عن `{username}` في قواعد بيانات انستقرام...")

    # الرابط الفعلي الذي يستخدمه الموقع للبحث
    url = "https://breach.vip/api/search"
    
    # البيانات المطلوبة لمحاكاة البحث كـ Username
    params = {
        "term": username,
        "type": "username"  # هنا حددنا نوع البحث كما في الصورة
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
        "Accept": "application/json, text/plain, */*"
    }

    try:
        # إرسال طلب البحث
        res = requests.get(url, params=params, headers=headers, timeout=15)

        if res.status_code != 200:
            bot.edit_message_text("❌ الموقع رفض الطلب أو محمي حالياً. جرب لاحقاً.", message.chat.id, wait_msg.message_id)
            return

        # الموقع يرجع البيانات غالباً بصيغة JSON أو نص منسق
        data = res.text
        
        if "<html" in data.lower():
            bot.edit_message_text("⚠️ الموقع يطلب توثيق (Cloudflare). لا يمكن للبوت تجاوزه حالياً.", message.chat.id, wait_msg.message_id)
            return

        # فلترة النتائج لاستخراج بلوكات انستقرام فقط
        lines = data.splitlines()
        extracted_results = []
        is_instagram = False
        current_block = []

        for line in lines:
            # بداية بلوك جديد (بناءً على شكل الموقع في الصور)
            if "---" in line or ".com" in line or "Instagram" in line:
                if is_instagram and current_block:
                    extracted_results.append("\n".join(current_block))
                
                current_block = []
                is_instagram = "instagram" in line.lower()
            
            current_block.append(line.strip())

        # إضافة آخر بلوك إذا كان انستقرام
        if is_instagram and current_block:
            extracted_results.append("\n".join(current_block))

        if not extracted_results:
            bot.edit_message_text(f"❌ لم يتم العثور على نتائج انستقرام لـ `{username}`.", message.chat.id, wait_msg.message_id)
        else:
            final_text = "📸 **نتائج Instagram المستخرجة:**\n\n" + "\n\n--- \n\n".join(extracted_results)
            # تقسيم الرسالة إذا كانت طويلة جداً
            if len(final_text) > 4096:
                bot.edit_message_text(final_text[:4000] + "...", message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(final_text, message.chat.id, wait_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ أثناء البحث: {str(e)}", message.chat.id, wait_msg.message_id)

print("Bot is running...")
bot.infinity_polling()
