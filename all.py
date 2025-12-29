import telebot
from google import genai

# ۱. اطلاعات اصلی
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"

# ۲. اتصال به نسخه جدید گوگل
client = genai.Client(api_key=GOOGLE_API_KEY)

# ۳. راه‌اندازی ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    try:
        print(f"📥 دریافت پیام: {message.text}")
        
        # درخواست پاسخ از هوش مصنوعی
        # در نسخه جدید باید مدل را به این شکل صدا زد
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=message.text
        )
        
        # ارسال متن پاسخ
        bot.reply_to(message, response.text)
        print("✅ پاسخ با موفقیت ارسال شد.")
        
    except Exception as e:
        # چاپ خطای دقیق در ترمینال برای عیب‌یابی
        print(f"❌ خطای واقعی اینه: {e}")
        bot.reply_to(message, "مشکلی در اتصال به مغز هوش مصنوعی پیش اومد!")

if __name__ == "__main__":
    print("🚀 ربات زنده شد! همین الان تست کن علیرضا...")
    bot.infinity_polling()
