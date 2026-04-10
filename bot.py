import telebot
from curl_cffi import requests
import re

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث والفلترة...")

    # الرابط المباشر مع تحديد نوع البحث يوزرنيم
    url = f"https://breach.vip/api/search/{user_input}?type=username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)

        if response.status_code == 200:
            full_text = response.text
            
            # محاكاة "البحث في الصفحة" (Find in page) عن كلمة instagram
            # نقسم النص لقطع تبدأ بكلمة Instagram وتنتهي بـ ---
            insta_sections = re.findall(r"(Instagram.*?(?=---|$))", full_text, re.DOTALL | re.IGNORECASE)
            
            final_results = []

            for section in insta_sections:
                # استخراج اليوزر والإيميل من القطعة اللي لقيناها
                # نبحث عن السطر اللي فيه username والقيمة اللي بعده
                # والسطر اللي فيه email والقيمة اللي بعده
                u_match = re.search(r"username\s*[\n\r]+\s*([^\n\r]+)", section, re.IGNORECASE)
                e_match = re.search(r"email\s*[\n\r]+\s*([^\n\r]+)", section, re.IGNORECASE)
                
                if u_match and e_match:
                    found_user = u_match.group(1).strip()
                    found_email = e_match.group(1).strip()
                    final_results.append(f"👤 **User:** `{found_user}`\n📧 **Email:** `{found_email}`")

            if final_results:
                # إرسال النتائج الصافية (يوزر وايميل فقط)
                response_msg = "📸 **نتائج Instagram المكتشفة:**\n\n" + "\n\n---\n\n".join(final_results)
                bot.reply_to(message, response_msg, parse_mode="Markdown")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text(f"❌ لم يتم العثور على أي حسابات Instagram لليوزر `{user_input}`.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("⚠️ الموقع محمي حالياً (Cloudflare). جرب لاحقاً.", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ فني، حاول مرة أخرى.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
