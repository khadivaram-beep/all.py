import telebot
import google.generativeai as genai

# ۱. اطلاعات جدید (تلگرام و گوگل)
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"

# ۲. تنظیمات هوش مصنوعی Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ۳. راه‌اندازی ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

print("--- سیستم در حال بالا آمدن است ---")

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    try:
        # نمایش وضعیت در ترمینال
        print(f"📥 پیام از {message.from_user.first_name}: {message.text}")
        
        # ارسال پیام به هوش مصنوعی
        response = model.generate_content(message.text)
        
        # ارسال پاسخ هوش مصنوعی به تلگرام
        bot.reply_to(message, response.text)
        print("✅ پاسخ جمینای ارسال شد.")
        
    except Exception as e:
        print(f"❌ خطایی رخ داد: {e}")
        bot.reply_to(message, "ببخشید، یه مشکلی پیش اومد. دوباره بگو؟")

# ۴. استارت نهایی
if __name__ == "__main__":
    print("---------------------------------------")
    print("🚀 ربات @Khadivarr_bot در تلگرام روشن شد!")
    print("📡 آماده دریافت پیام‌های شما هستیم...")
    print("---------------------------------------")
    bot.infinity_polling()
