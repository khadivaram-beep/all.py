import telebot
from google import genai

# ۱. اطلاعات (بدون تغییر)
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"

# ۲. تنظیمات جدید گوگل (نسخه جدید)
client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = "gemini-2.0-flash" # استفاده از جدیدترین مدل

# ۳. راه‌اندازی ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    try:
        print(f"📥 پیام از {message.from_user.first_name}: {message.text}")
        
        # ارسال پیام به نسخه جدید جمینای
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=message.text
        )
        
        # ارسال پاسخ به تلگرام
        bot.reply_to(message, response.text)
        print("✅ پاسخ جمینای ارسال شد.")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        bot.reply_to(message, "کمی صبر کن، دارم فکر می‌کنم...")

if __name__ == "__main__":
    print("---------------------------------------")
    print("🚀 ربات با نسخه جدید Gemini فعال شد!")
    print("---------------------------------------")
    bot.infinity_polling()
