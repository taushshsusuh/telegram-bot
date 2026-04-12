import telebot
from playwright.sync_api import sync_playwright
import re # لاستخدام التعبيرات العادية لاستخراج الإيميل واسم المستخدم

TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA" # تأكد من أن هذا التوكن صحيح
bot = telebot.TeleBot(TOKEN)

def get_data(search_query):
    with sync_playwright() as p:
        # إعداد المتصفح بدون واجهة رسومية (headless)
        # معالجتها لأخطاء الساندبوكس في بيئات مثل Docker
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        try:
            page.goto("https://breach.vip/", wait_until="networkidle")

            # التأكد من وجود حقل البحث قبل محاولة الملء
            page.wait_for_selector('input[placeholder="Search term"]', timeout=10000)
            page.fill('input[placeholder="Search term"]', search_query)

            # التأكد من وجود زر "Username" قبل النقر
            page.wait_for_selector('button:has-text("Username")', timeout=10000)
            page.click('button:has-text("Username")')

            # التأكد من وجود زر "Search" قبل النقر
            page.wait_for_selector('button:has-text("Search")', timeout=10000)
            page.click('button:has-text("Search")')

            # الانتظار حتى يتم تحميل النتائج
            # يمكن تحسين هذا بالانتظار لعنصر معين يظهر بعد تحميل النتائج بدلاً من وقت ثابت
            page.wait_for_timeout(7000) # زيادة الوقت قليلاً لضمان تحميل النتائج

            elements = page.query_selector_all('div.mb-4')
            instagram_results = []

            for el in elements:
                text = " ".join(el.inner_text().split()).lower()
                if "instagram" in text:
                    # محاولة استخراج الإيميل واسم المستخدم باستخدام التعبيرات العادية
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                    username_match = re.search(r'(?:user|username|account):\s*([a-zA-Z0-9_.]+)', text) # مثال لاسم مستخدم
                    
                    email = email_match.group(0) if email_match else "غير متوفر"
                    username = username_match.group(1) if username_match else search_query # نفترض أن اسم المستخدم هو نفسه البحث إذا لم نجد

                    instagram_results.append(f"📱 **Instagram Result:**\n"
                                             f"  **Username:** `{username}`\n"
                                             f"  **Email:** `{email}`\n"
                                             f"  **Source Text (partial):** {text[:200]}...\n" # جزء من النص الأصلي
                                             f"-----------------------------------\n")
            
            final_msg = "".join(instagram_results)
            if not final_msg:
                final_msg = "❌ لم أجد أي نتائج لـ Instagram لهذا اليوزر."

            return final_msg

        except Exception as e:
            return f"❌ حدث خطأ أثناء البحث: {str(e)}"
        finally:
            browser.close()

@bot.message_handler(func=lambda m: True)
def search(message):
    wait_message = bot.reply_to(message, "🔍 جاري البحث عن نتائج Instagram...")
    try:
        res = get_data(message.text.strip())
        bot.edit_message_text(res, message.chat.id, wait_message.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ غير متوقع: {str(e)}", message.chat.id, wait_message.message_id)

bot.infinity_polling()
