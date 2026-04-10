import telebot
from curl_cffi import requests
import re
import random

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

# قائمة البروكسيات الجديدة التي زودتني بها
PROXIES = [
    "155.117.18.36:25388", "159.223.225.118:8888", "163.223.150.21:8080",
    "167.103.115.102:8800", "167.103.144.127:8800", "167.103.31.122:8800",
    "185.191.236.162:3128", "209.126.84.232:8888", "38.255.85.145:999"
    # أضف البقية هنا بنفس التنسيق
]

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    user_input = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "⏳ جاري البحث باستخدام البروكسي...")

    url = "https://breach.vip/api/search"
    params = {"term": user_input, "type": "username"}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://breach.vip/",
        "X-Requested-With": "XMLHttpRequest"
    }

    # محاولة البحث عبر 3 بروكسيات مختلفة قبل الاستسلام
    for attempt in range(3):
        proxy_addr = random.choice(PROXIES)
        proxies_dict = {"http": f"http://{proxy_addr}", "https": f"http://{proxy_addr}"}
        
        try:
            response = requests.get(url, params=params, headers=headers, 
                                    proxies=proxies_dict, impersonate="chrome110", timeout=15)

            if response.status_code == 200:
                full_text = response.text
                
                # البحث عن كل أقسام انستقرام (Selfie, Joel, etc)
                # نستخدم Regex للبحث عن البلوكات التي تحتوي على Instagram
                # التقسيم يتم بناءً على الفواصل المتعارف عليها في الموقع (---)
                sections = re.split(r"-{3,}", full_text)
                found_results = []

                for section in sections:
                    if "instagram" in section.lower():
                        # استخراج اليوزر والإيميل من هذا القسم تحديداً
                        u_match = re.search(r"username\s+([^\n\r]+)", section, re.IGNORECASE)
                        e_match = re.search(r"email\s+([^\n\r]+)", section, re.IGNORECASE)
                        
                        if u_match and e_match:
                            user = u_match.group(1).strip()
                            email = e_match.group(1).strip()
                            found_results.append(f"👤 **User:** `{user}`\n📧 **Email:** `{email}`")

                if found_results:
                    # تجميع كل النتائج المكتشفة (للانستقرام فقط)
                    final_msg = "✅ **نتائج Instagram المكتشفة:**\n\n" + "\n\n---\n\n".join(found_results)
                    bot.reply_to(message, final_msg, parse_mode="Markdown")
                    bot.delete_message(message.chat.id, wait_msg.message_id)
                    return # نجحنا، نخرج من الدوارة
                else:
                    bot.edit_message_text(f"❌ لم أجد بيانات Instagram لليوزر `{user_input}`.", message.chat.id, wait_msg.message_id)
                    return
            
            elif response.status_code == 403:
                continue # البروكسي محظور، جرب غيره
        except:
            continue # خطأ في البروكسي، جرب غيره

    bot.edit_message_text("⚠️ فشل التخطي: الموقع محمي أو جميع البروكسيات محظورة حالياً.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
