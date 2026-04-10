import telebot
from playwright.sync_api import sync_playwright
import re
import time

TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

def get_instagram_data(username):
    results = []
    with sync_playwright() as p:
        # إضافة args ضرورية لتشغيل المتصفح في السيرفرات
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            page.goto("https://breach.vip/", timeout=60000)
            
            # انتظر تحميل القائمة المنسدلة واختر Username
            page.wait_for_selector("select")
            page.select_option("select", "username")

            # كتابة اليوزر في الحقل الصحيح
            page.fill("input[type='text'], input[name='term']", username)
            page.keyboard.press("Enter")

            # انتظر ظهور النتائج (مهم جداً لأن الموقع بطيء)
            time.sleep(7) 

            # اسحب النص الصافي من الصفحة (كما يظهر للمستخدم)
            clean_text = page.evaluate("() => document.body.innerText")

            # الفلترة الذكية للقسم المطلوب
            # نبحث عن Instagram ثم أي نص حتى نجد username و email
            pattern = r"Instagram.*?username\s*[:\s]+([^\n\r]+).*?email\s*[:\s]+([^\n\r]+)"
            matches = re.findall(pattern, clean_text, re.IGNORECASE | re.DOTALL)

            for user, email in matches:
                if username.lower() in user.lower() or True: # True لضمان جلب كل ما يخص انستقرام
                    results.append(f"👤 **User:** `{user.strip()}`\n📧 **Email:** `{email.strip()}`")

        except Exception as e:
            print(f"Playwright Error: {e}")
        finally:
            browser.close()

    return list(set(results)) # منع التكرار

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🔥 أرسل اليوزرنيم لبدء البحث الاحترافي عبر المتصفح")

@bot.message_handler(func=lambda m: True)
def search(msg):
    username = msg.text.strip().replace("@", "")
    wait = bot.reply_to(msg, "⏳ جاري تشغيل المتصفح الحقيقي والبحث...")

    try:
        data = get_instagram_data(username)
        if data:
            bot.edit_message_text(f"✅ **النتائج المستخرجة:**\n\n" + "\n\n---\n\n".join(data[:10]), msg.chat.id, wait.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("❌ لم يظهر قسم Instagram في المتصفح. (تأكد من صحة اليوزر أو جرب لاحقاً)", msg.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ في محرك البحث: {str(e)}", msg.chat.id, wait.message_id)

bot.infinity_polling()
