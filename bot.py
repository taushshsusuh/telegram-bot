import telebot
import cloudscraper
import random
import time

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

# قائمة البروكسيات التي زودتني بها (أضف البقية بنفس التنسيق)
PROXY_LIST = [
    "1.231.81.166:3128", "101.32.163.17:7890", "103.122.65.242:8080",
    "103.126.119.110:8080", "103.144.102.231:8085", "103.156.96.238:8088",
    "103.157.200.126:3128", "103.165.250.26:8181", "103.173.139.221:8080",
    "103.173.214.187:8080", "103.176.97.205:8082", "185.191.236.162:3128"
    # يمكنك إضافة كل القائمة هنا
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أرسل اليوزر وسأستخدم البروكسي لتخطي حماية Cloudflare.")

@bot.message_handler(func=lambda m: True)
def search_user(message):
    username = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, f"⏳ جاري محاولة التخطي باستخدام البروكسي لليوزر `{username}`...")

    url = f"https://breach.vip/api/search/{username}"
    
    # محاولة 3 بروكسيات مختلفة في حال فشل أحدها
    for i in range(3):
        proxy = random.choice(PROXY_LIST)
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        try:
            # إنشاء سكرابر جديد لكل محاولة بروكسي
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
            
            res = scraper.get(url, proxies=proxies, timeout=15)

            if res.status_code == 200 and "instagram" in res.text.lower():
                data = res.text
                lines = data.splitlines()
                extracted = []
                is_inst = False
                
                for line in lines:
                    l = line.strip()
                    if "instagram" in l.lower():
                        is_inst = True
                        extracted.append("━━━━━━━━━━━━━━━")
                    elif is_inst and (".com" in l.lower() or "---" in l):
                        if "instagram" not in l.lower(): is_inst = False
                    
                    if is_inst and l: extracted.append(l)

                final_msg = "✅ **تم التخطي بنجاح!**\n\n" + "\n".join(extracted)
                bot.edit_message_text(final_msg[:4096], message.chat.id, wait_msg.message_id, parse_mode="Markdown")
                return # الخروج من الحلقة عند النجاح

            elif "cloudflare" in res.text.lower() or res.status_code == 403:
                continue # تجربة بروكسي آخر
                
        except:
            continue # إذا كان البروكسي ميتاً، جرب غيره

    bot.edit_message_text("❌ فشلت جميع محاولات البروكسي في تخطي الحماية. الموقع يطلب حماية يدوية (Captcha) حالياً.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
