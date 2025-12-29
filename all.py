import telebot
import google.generativeai as genai

# ۱. تنظیمات دیتای دریافتی (نسخه نهایی علیرضا)
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"
BOT_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"

# ۲. پیکربندی هوش مصنوعی گوگل (Gemini)
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ هوش مصنوعی گوگل با موفقیت متصل شد.")
except Exception as e:
    print(f"❌ خطا در لود هوش مصنوعی: {e}")

# ۳. پیکربندی ربات بله با تنظیمات ضد مسدودی
bot = telebot.TeleBot(BOT_TOKEN)
telebot.apihelper.API_URL = "https://api.ble.ir/bot{0}/{1}"
# هدر اختصاصی برای جلوگیری از خطای 404 nginx
telebot.apihelper.CUSTOM_HEADERS = {'User-Agent': 'Mozilla/5.0'}

# ۴. پردازش پیام‌های دریافتی
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # نمایش پیام در ترمینال برای تست
        print(f"📥 پیام از بله: {message.text}")
        
        # ارسال پیام به جمینای برای دریافت پاسخ
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(message.text)
        
        # ارسال پاسخ نهایی به کاربر در بله
        bot.reply_to(message, response.text)
        print("📤 پاسخ با موفقیت به بله ارسال شد.")
        
    except Exception as e:
        print(f"❌ خطای عملیاتی: {e}")

# ۵. استارت ربات
if __name__ == "__main__":
    print("---------------------------------------")
    print("🚀 ربات @Next_Gen_bot روشن شد!")
    print("📡 در حال شنود پیام‌ها...")
    print("---------------------------------------")
    
    # استفاده از infinity_polling برای پایداری در Codespaces
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
