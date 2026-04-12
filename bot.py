import telebot
from playwright.sync_api import sync_playwright

TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"
bot = telebot.TeleBot(TOKEN)

def get_data(search_query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://breach.vip/", wait_until="networkidle")
        page.fill('input[placeholder="Search term"]', search_query)
        page.click('button:has-text("Username")')
        page.click('button:has-text("Search")')
        page.wait_for_timeout(5000)
        
        # استخراج النتائج ككتل نصية
        elements = page.query_selector_all('div.mb-4')
        final_msg = ""
        
        for el in elements:
            # هنا نقوم بتنظيف النص تماماً من أي مسافات غريبة أو رموز
            text = " ".join(el.inner_text().split()).lower()
            
            # البحث المرن
            if "instagram" in text:
                final_msg += f"📱 {text[:500]}\n-----------------\n"
        
        browser.close()
        return final_msg if final_msg else "❌ لم أجد Instagram لهذا اليوزر."

@bot.message_handler(func=lambda m: True)
def search(message):
    wait = bot.reply_to(message, "🔍 جاري البحث...")
    try:
        res = get_data(message.text.strip())
        bot.edit_message_text(res, message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", message.chat.id, wait.message_id)

bot.infinity_polling()
