import telebot
from playwright.sync_api import sync_playwright
import os

TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"
bot = telebot.TeleBot(TOKEN)

def get_data(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://breach.vip/") # ادخل رابط البحث المباشر
        
        # 1. تحديد خيار username (يجب استبدال 'select' بالـ Selector الصحيح)
        page.select_option('select[name="type"]', 'username')
        
        # 2. إدخال اليوزر والبحث
        page.fill('input[name="query"]', username)
        page.click('button[type="submit"]')
        
        # 3. انتظار النتائج
        page.wait_for_selector('.result-item') # استبدل بكلاس النتائج الحقيقي
        
        # 4. الفلترة للـ Instagram فقط
        results = page.query_selector_all('.result-item')
        final_msg = ""
        
        for item in results:
            text = item.inner_text().lower()
            if "instagram" in text:
                # هنا يتم استخراج البيانات (اليوزر والايميل)
                # تحتاج لضبط الـ Selectors بناءً على شكل النتائج في الموقع
                user = item.query_selector('.username').inner_text()
                email = item.query_selector('.email').inner_text()
                final_msg += f"👤 {user}\n📧 {email}\n\n"
        
        browser.close()
        return final_msg if final_msg else "لم يتم العثور على نتائج Instagram"

@bot.message_handler(func=lambda m: True)
def search(message):
    wait = bot.reply_to(message, "🔍 جاري البحث والفلترة...")
    try:
        res = get_data(message.text)
        bot.edit_message_text(res, message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"حدث خطأ: {str(e)}", message.chat.id, wait.message_id)

bot.infinity_polling()
