import telebot
from playwright.sync_api import sync_playwright
import re # لاستخدام التعبيرات العادية لاستخراج أفضل

# التوكن الخاص بالبوت الخاص بك (تم تضمينه بناءً على طلبك)
TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA" 
bot = telebot.TeleBot(TOKEN)

def get_data(search_query):
    final_msg = ""
    try:
        with sync_playwright() as p:
            # تشغيل متصفح Chromium في وضع headless (بدون واجهة رسومية)
            # Playwright سيجد المتصفح تلقائيًا في بيئة Docker المهيأة
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--single-process'] 
            )
            page = browser.new_page()
            
            # الانتقال إلى الموقع والانتظار حتى يتم تحميل الشبكة بالكامل
            page.goto("https://breach.vip/", wait_until="networkidle")
            
            # ملء حقل البحث
            # استخدم selector أكثر تحديدًا لتجنب الأخطاء
            page.fill('input[placeholder="Search term"]', search_query)
            
            # النقر على زر "Username"
            # استخدام :has-text يمكن أن يكون حساسًا للحالة أو المسافات، يمكن تحسينه
            # أو الاعتماد على ترتيب الأزرار إذا كان ثابتًا
            page.click('button:has-text("Username")')
            
            # النقر على زر "Search"
            page.click('button:has-text("Search")')
            
            # الانتظار لمدة 5 ثوانٍ لتحميل النتائج
            # يمكن استخدام page.wait_for_selector لانتظار ظهور النتائج بدلاً من وقت ثابت
            page.wait_for_timeout(5000) 
            
            # تحديد جميع عناصر النتائج
            elements = page.query_selector_all('div.mb-4') 
            
            instagram_results = []

            for el in elements:
                text = " ".join(el.inner_text().split()).lower()
                if "instagram" in text:
                    extracted_email = "غير متوفر"
                    extracted_username = "غير متوفر"

                    # محاولة استخراج البريد الإلكتروني باستخدام تعبير عادي
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                    if email_match:
                        extracted_email = email_match.group(0)
                    
                    # محاولة استخراج اسم المستخدم (افتراضيًا بعد "instagram" أو من سطر معين)
                    # هذا الجزء قد يحتاج إلى تعديل دقيق حسب هيكل البيانات الفعلي في breach.vip
                    # نفترض أن اسم المستخدم يظهر بعد كلمة "instagram" أو في سطر منفصل مميز
                    # أو قد يكون هو نفسه الـ search_query إذا كانت النتيجة مطابقة لاسم المستخدم
                    
                    # محاولة استخراج اسم مستخدم افتراضي من النص بعد كلمة instagram
                    # هذا استنتاج وقد لا يكون دقيقًا دائمًا
                    username_match = re.search(r'instagram.*?(\b[a-zA-Z0-9._-]{3,}\b)', text)
                    if username_match:
                        # يجب أن نكون حذرين، هذا قد يستخرج أي كلمة بعد instagram
                        # يمكن تحسينه إذا كان هناك نمط محدد لأسماء المستخدمين
                        extracted_username = username_match.group(1)
                    
                    # إذا لم يتم العثور على اسم مستخدم محدد، يمكن استخدام الـ search_query كافتراضي
                    if extracted_username == "غير متوفر":
                        extracted_username = search_query
                        
                    instagram_results.append({
                        "email": extracted_email,
                        "username": extracted_username,
                        "original_text": text
                    })
            
            browser.close()

            if instagram_results:
                final_msg += "✅ نتائج Instagram التي تم العثور عليها:\n\n"
                for res in instagram_results:
                    final_msg += f"👤 **اسم المستخدم:** {res['username']}\n"
                    final_msg += f"📧 **البريد الإلكتروني:** {res['email']}\n"
                    # يمكن إضافة المزيد من التفاصيل إذا كانت متوفرة وضرورية
                    # final_msg += f"📜 **تفاصيل:** {res['original_text'][:200]}...\n" # لعرض جزء من النص الأصلي
                    final_msg += "-----------------\n"
            else:
                final_msg = "❌ لم يتم العثور على أي نتائج Instagram لهذا اليوزر."

    except Exception as e:
        final_msg = f"❌ حدث خطأ غير متوقع أثناء البحث: {str(e)}"
    
    return final_msg

@bot.message_handler(func=lambda m: True)
def search(message):
    wait = bot.reply_to(message, "🔍 جاري البحث عن معلومات اليوزر، يرجى الانتظار...")
    try:
        res = get_data(message.text.strip())
        bot.edit_message_text(res, message.chat.id, wait.message_id, parse_mode='Markdown') # استخدام Markdown للتحسين
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ في معالجة طلبك: {str(e)}", message.chat.id, wait.message_id)

print("البوت بدأ العمل...")
bot.infinity_polling()
