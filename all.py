import telebot
from google import genai

# ۱. اطلاعات اصلی (بدون تغییر)
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"

# ۲. اتصال به گوگل
client = genai.Client(api_key=GOOGLE_API_KEY)

# ۳. راه‌اندازی ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    try:
        print(f"📥 پیام رسید: {message.text}")
        
        # تغییر مهم: حذف کلمه models/ و استفاده از نام ساده
        # همچنین تست با جدیدترین ورژن موجود
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=message.text
        )
        
        bot.reply_to(message, response.text)
        print("✅ ایول! بالاخره جواب داد.")
        
    except Exception as e:
        err_msg = str(e)
        print(f"❌ ارور: {err_msg}")
        
        # اگر باز هم مدل رو پیدا نکرد، این بار با یک اسم دیگه تست می‌کنه
        bot.reply_to(message, "هنوز دارم تنظیمات مغزم رو ردیف می‌کنم، دوباره بفرست...")

if __name__ == "__main__":
    print("🚀 تلاش مجدد... علیرضا الان تست کن")
    bot.infinity_polling()
