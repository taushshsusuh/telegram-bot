import telebot
import requests
import json # لإظهار هيكل الـ API بشكل أوضح عند الحاجة

# توكن بوت التليجرام الخاص بك
TOKEN = "8781081982:AAHydfh5K-vllcSej_hGzk5LjiH0WmC1oRA"
bot = telebot.TeleBot(TOKEN)

# نقطة نهاية الـ API للبحث (افتراضية، قد تحتاج للتعديل بناءً على وثائق API الفعلية)
# بناءً على openapi.json، يبدو أن هناك نقطة نهاية للبحث
API_SEARCH_URL = "https://breach.vip/api/v1/search"

# في حال كان الـ API يحتاج لمفتاح، قم بوضعه هنا
# API_KEY = "YOUR_API_KEY_HERE"
# HEADERS = {"Authorization": f"Bearer {API_KEY}"} # مثال للمصادقة باستخدام Bearer Token
HEADERS = {"Content-Type": "application/json"} # افتراضي، قد تحتاج لتعديل إذا كان هناك مصادقة

def get_data_from_breach_api(search_query):
    """
    يتفاعل مع Breach.vip API للبحث عن اليوزر واستخراج بيانات Instagram.
    """
    payload = {
        "query": search_query,
        "type": "username" # تحديد نوع البحث كـ "username"
    }

    try:
        # إرسال طلب POST إلى الـ API
        response = requests.post(API_SEARCH_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # إظهار خطأ لرموز حالة HTTP 4xx/5xx

        data = response.json()
        
        # يمكنك طباعة الرد الكامل للمساعدة في تصحيح الأخطاء وفهم هيكل البيانات
        # print("API Response:", json.dumps(data, indent=2)) 

        final_msg = ""
        
        # افتراض أن الرد يحتوي على قائمة من النتائج
        if "data" in data and isinstance(data["data"], list):
            instagram_found = False
            for item in data["data"]:
                # البحث عن البيانات المتعلقة بـ Instagram
                # قد تحتاج لتعديل "platform" أو أي حقل آخر بناءً على الرد الفعلي
                if "platform" in item and item["platform"].lower() == "instagram":
                    instagram_found = True
                    # استخراج الإيميل واليوزر من بيانات Instagram
                    # افتراض وجود حقول مثل 'email' و 'username' مباشرة في العنصر
                    email = item.get("email", "غير متوفر")
                    username = item.get("username", search_query) # إذا لم يكن هناك يوزر محدد، استخدم يوزر البحث

                    final_msg += f"📱 **بيانات Instagram:**\n"
                    final_msg += f"  - اليوزر: `{username}`\n"
                    final_msg += f"  - الإيميل: `{email}`\n"
                    final_msg += "-----------------\n"
            
            if not instagram_found:
                return f"❌ لم يتم العثور على بيانات Instagram لليوزر `{search_query}`."
        else:
            return f"❌ لا توجد نتائج أو هيكل رد غير متوقع من الـ API لليوزر `{search_query}`."

        return final_msg if final_msg else f"❌ لم يتم العثور على بيانات Instagram لليوزر `{search_query}`."

    except requests.exceptions.HTTPError as http_err:
        return f"❌ خطأ HTTP: {http_err} - تأكد من صلاحية الـ API Key أو صحة نقطة النهاية."
    except requests.exceptions.ConnectionError as conn_err:
        return f"❌ خطأ في الاتصال: {conn_err} - تأكد من اتصالك بالإنترنت وصحة عنوان الـ API."
    except requests.exceptions.Timeout as timeout_err:
        return f"❌ انتهت مهلة الطلب: {timeout_err} - حاول مرة أخرى."
    except requests.exceptions.RequestException as req_err:
        return f"❌ خطأ عام في الطلب: {req_err}"
    except Exception as e:
        return f"❌ خطأ غير متوقع: {str(e)}"

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    """
    يتعامل مع الرسائل الواردة من المستخدمين في التليجرام.
    """
    user_query = message.text.strip()
    
    if not user_query:
        bot.reply_to(message, "الرجاء إرسال اسم المستخدم الذي تريد البحث عنه.")
        return

    wait_message = bot.reply_to(message, "🔍 جاري البحث عن بيانات اليوزر...")
    
    try:
        # استدعاء دالة البحث عن البيانات
        result_message = get_data_from_breach_api(user_query)
        
        # إرسال النتيجة إلى المستخدم
        bot.edit_message_text(
            result_message,
            chat_id=message.chat.id,
            message_id=wait_message.message_id,
            parse_mode="Markdown" # لتفعيل تنسيق Markdown في الرسالة
        )
    except Exception as e:
        bot.edit_message_text(
            f"❌ حدث خطأ غير متوقع أثناء معالجة طلبك: {str(e)}",
            chat_id=message.chat.id,
            message_id=wait_message.message_id
        )

# بدء تشغيل البوت
print("البوت يعمل الآن...")
bot.infinity_polling()
