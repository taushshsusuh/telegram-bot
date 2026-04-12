import telebot
from playwright.sync_api import sync_playwright
import time

TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"
bot = telebot.TeleBot(TOKEN)

def get_data(search_query):
    with sync_playwright() as p:
        # تشغيل المتصفح (Chromium)
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        try:
            # 1. الدخول للموقع
            page.goto("https://breach.vip/", wait_until="networkidle")
            
            # 2. كتابة اليوزر في الخانة الأولى
            page.fill('input[placeholder="Search term"]', search_query)
            
            # 3. اختيار "Username" من الأزرار (حسب الفيديو هي أزرار وليست قائمة منسدلة)
            page.click('button:has-text("Username")')
            
            # 4. الضغط على زر Search
            page.click('button:has-text("Search")')
            
            # انتظار ظهور النتائج (تأخير بسيط للتأكد من التحميل)
            page.wait_for_timeout(5000) 
            
            # 5. جلب كل كتل النتائج (التي تبدأ بـ - اسم الموقع)
            results = page.query_selector_all('div.mb-4') # هذا الكلاس الشائع لكتل النتائج
            
            final_msg = f"🔍 نتائج Instagram لليوزر: {search_query}\n\n"
            found = False
            
            for item in results:
                content = item.inner_text()
                content_lower = content.lower()
                
                # الفلترة لـ Instagram فقط (مثل Selfie و Joel)
                if "instagram" in content_lower:
                    # استخراج اليوزر والايميل من النص
                    lines = content.split('\n')
                    username = "غير موجود"
                    email = "غير موجود"
                    
                    for line in lines:
                        if "username" in line.lower():
                            username = line.split()[-1]
                        if "email" in line.lower():
                            email = line.split()[-1]
                    
                    final_msg += f"📱 المصدر: Instagram\n👤 اليوزر: {username}\n📧 الإيميل: {email}\n"
                    final_msg += "------------------------\n"
                    found = True
            
            browser.close()
            if found:
                return final_msg
            else:
                return "❌ لم يتم العثور على نتائج تخص Instagram لهذا اليوزر."

        except Exception as e:
            browser.close()
            return f"⚠️ حدث خطأ أثناء المحاكاة: {str(e)}"

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    wait_msg = bot.reply_to(message, "⏳ جاري تشغيل المتصفح والبحث في Instagram... (قد يستغرق دقيقة)")
    result = get_data(message.text.strip())
    bot.edit_message_text(result, message.chat.id, wait_msg.message_id)

bot.infinity_polling()
