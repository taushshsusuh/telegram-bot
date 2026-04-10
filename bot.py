import telebot
from playwright.sync_api import sync_playwright
import re
import time

# 🔑 التوكن الخاص بك
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

# وظيفة البحث باستخدام محرك المتصفح Playwright
def scrape_instagram_data(username):
    final_results = []
    
    with sync_playwright() as p:
        # 1. عدل تشغيل المتصفح (مهم جداً للعمل على Railway)
        # أضفنا args لمنع الكراش وزيادة التوافق
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled" # أخف بصمة أتمتة
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # الدخول للموقع
            page.goto("https://breach.vip/", timeout=60000)
            
            # اختار input الصحيح (التعديل الذي اقترحته)
            # نكتب اليوزر مباشرة في الحقل
            page.fill("input[name='term']", username)
            
            # اختيار Username من القائمة المنسدلة
            page.select_option("select[name='type']", "username")
            
            # ضغط زر البحث
            page.click("button:has-text('Search')")
            
            # حط وقت انتظار أطول (التعديل الذي اقترحته لضمان تحميل الـ JS)
            # ننتظر 12 ثانية كاملة
            page.wait_for_timeout(12000)
            
            # الآن: سحب محتوى الصفحة بالكامل بعد التحميل
            # نبحث عن البيانات التي تظهر في الواجهة
            
            # سحب كل النصوص من الـ tags المحتملة (pre or results list)
            elements = page.query_selector_all("pre, .results-list-item, div.result")
            
            for el in elements:
                text_content = el.inner_text()
                
                # الفلترة الذكية: التأكد أن البلوك يخص Instagram
                if "instagram" in text_content.lower():
                    # استخدام Regex مطاطي لسحب اليوزر والايميل حتى لو بينهم أسطر
                    # يبحث عن username:xxx أو username xxx
                    u_match = re.search(r"username\s*[:\s]\s*([^\n\r\-]+)", text_content, re.IGNORECASE)
                    e_match = re.search(r"email\s*[:\s]\s*([^\n\r\-]+)", text_content, re.IGNORECASE)
                    
                    if u_match and e_match:
                        found_user = u_match.group(1).strip()
                        found_email = e_match.group(1).strip()
                        
                        # فلترة إضافية: التأكد أن اليوزر الذي نبحث عنه جزء من النتيجة
                        if username.lower() in found_user.lower():
                            final_results.append(f"👤 **User:** `{found_user}`\n📧 **Email:** `{found_email}`")

        except Exception as e:
            print(f"Browser Scraper Error: {e}")
            
        finally:
            browser.close()
            
    return final_results

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔎 أهلاً بك! أنا بوت البحث الاحترافي عن بيانات Instagram.\n\nأرسل اليوزرنيم (بدون @) للبدء.")

@bot.message_handler(func=lambda m: True)
def search(message):
    username = message.text.strip().replace('@', '')
    
    # رسالة الانتظار
    wait_msg = bot.reply_to(message, f"🔥 جاري تشغيل المتصفح الحقيقي للبحث عن `{username}` في Instagram...\n(قد يستغرق دقيقة)")

    try:
        # تشغيل المحرك
        results = scrape_instagram_data(username)

        if results:
            # تنظيف التكرار وإرسال النتائج
            unique_results = list(set(results))
            response_msg = "✅ **تم بنجاح! هذي نتائج Instagram المكتشفة:**\n\n" + "\n\n---\n\n".join(unique_results)
            bot.edit_message_text(response_msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
            
        else:
            bot.edit_message_text(f"❌ لم يتم العثور على أي أقسام مرتبة لـ Instagram لليوزر `{username}`.\n\n(الموقع غالباً لم يرجع النتيجة المطلوبة في الواجهة)", message.chat.id, wait_msg.message_id)

    except Exception as e:
        # في حال حدوث خطأ كارثي (مثلاً نقص في الرام على Railway)
        print(f"Critcal Error: {e}")
        bot.edit_message_text("❌ حدث خطأ غير متوقع في محرك المتصفح. قد يكون السيرفر مضغوطاً.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
