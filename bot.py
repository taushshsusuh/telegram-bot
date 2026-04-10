import telebot
from playwright.sync_api import sync_playwright
import time

# 🔑 توكن البوت
TOKEN = "8781081982:AAF5NLXtFqZU8XGfm0u5ErfvFWTmWmsLO2k"
bot = telebot.TeleBot(TOKEN)

def scrape_with_browser(username):
    results = []
    with sync_playwright() as p:
        # تشغيل متصفح خفي
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # الدخول للموقع مباشرة
            page.goto(f"https://breach.vip/", timeout=60000)
            
            # اختيار "Username" من القائمة المنسدلة
            page.select_option("select[name='type']", "username")
            
            # كتابة اليوزر والبحث
            page.fill("input[name='term']", username)
            page.press("input[name='term']", "Enter")
            
            # الانتظار حتى تظهر النتائج (أو ننتظر قليلاً للـ JS)
            time.sleep(5) 
            
            # الآن: "البحث في الصفحة" عن كل البلوكات التي تحتوي كلمة Instagram
            # نستخدم كود JS داخل المتصفح لسحب البيانات تماماً كما تراها
            insta_data = page.evaluate("""() => {
                let found = [];
                let items = document.querySelectorAll('pre'); // الموقع يعرض البيانات في tag pre
                items.forEach(item => {
                    let text = item.innerText;
                    if (text.toLowerCase().includes('instagram')) {
                        found.append(text);
                    }
                });
                return found;
            }""")
            
            # تنظيف البيانات المستخرجة
            for entry in insta_data:
                u_match = re.search(r"username\s*[:\s]\s*([^\n\r]+)", entry, re.IGNORECASE)
                e_match = re.search(r"email\s*[:\s]\s*([^\n\r]+)", entry, re.IGNORECASE)
                if u_match and e_match:
                    results.append(f"👤 **User:** `{u_match.group(1).strip()}`\n📧 **Email:** `{e_match.group(1).strip()}`")

        except Exception as e:
            print(f"Browser Error: {e}")
        finally:
            browser.close()
    return results

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    username = message.text.strip().replace('@', '')
    wait_msg = bot.reply_to(message, "🔥 جاري تشغيل المتصفح الاحترافي للبحث عن Instagram...")

    try:
        final_results = scrape_with_browser(username)

        if final_results:
            msg = "✅ **نتائج Instagram (من المتصفح الحقيقي):**\n\n" + "\n\n---\n\n".join(list(set(final_results)))
            bot.edit_message_text(msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"❌ حتى المتصفح لم يجد Instagram لليوزر `{username}`.", message.chat.id, wait_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ في تشغيل محرك البحث.", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
