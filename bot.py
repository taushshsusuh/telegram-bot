import telebot
from curl_cffi import requests

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري الفلترة وسحب البيانات...")

    # الرابط اللي يحدد "Username" من البداية
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
    }

    try:
        # طلب البيانات كنص
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        
        if response and response.status_code == 200:
            lines = response.text.splitlines()
            found_results = []
            
            # منطق "الصياد" - يبحث عن الفقرة اللي تبدأ بـ Instagram
            for i in range(len(lines)):
                line_content = lines[i].strip().lower()

                # إذا السطر فيه كلمة Instagram
                if "instagram" in line_content:
                    u_val = "غير موجود"
                    e_val = "غير موجود"
                    
                    # نبحث في الـ 15 سطر اللي تحت كلمة Instagram عن اليوزر والايميل
                    for j in range(i + 1, min(i + 15, len(lines))):
                        sub_line = lines[j].strip().lower()
                        
                        # سحب اليوزر: إذا لقينا سطر فيه username، القيمة هي السطر اللي بعده
                        if sub_line == "username" and (j + 1) < len(lines):
                            u_val = lines[j+1].strip()
                        
                        # سحب الايميل: إذا لقينا سطر فيه email، القيمة هي السطر اللي بعده
                        if sub_line == "email" and (j + 1) < len(lines):
                            e_val = lines[j+1].strip()
                    
                    # إذا لقينا واحد منهم على الأقل، نضيف النتيجة
                    if u_val != "غير موجود" or e_val != "غير موجود":
                        found_results.append(f"👤 **User:** `{u_val}`\n📧 **Email:** `{e_val}`")

            if found_results:
                # إرسال النتائج الصافية (يوزر وايميل فقط)
                # استخدمت set لمنع التكرار إذا ظهرت نفس النتيجة مرتين
                unique_results = list(set(found_results))
                final_msg = "✅ **نتائج Instagram المستخرجة:**\n\n" + "\n\n---\n\n".join(unique_results)
                bot.reply_to(message, final_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على قسم Instagram لهذا اليوزر.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("⚠️ الموقع محمي بـ Cloudflare حالياً. جرب لاحقاً.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ في معالجة البيانات، حاول مرة أخرى.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
