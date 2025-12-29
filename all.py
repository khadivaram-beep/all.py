import telebot
from google import genai
import os

# اطلاعات شما
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"

client = genai.Client(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    try:
        print(f"📥 پیام رسید: {message.text}")
        
        # تست با مدل قدیمی‌تر و پایدارتر که معمولاً محدودیت کمتری دارد
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=message.text
        )
        
        bot.reply_to(message, response.text)
        print("✅ پاسخ با موفقیت ارسال شد.")
        
    except Exception as e:
        err = str(e)
        print(f"❌ ارور دقیق: {err}")
        
        if "429" in err:
            bot.reply_to(message, "🚨 علیرضا، گوگل اجازه نمیده! میگه 'ظرفیت رایگان این کلید (API Key) تمام شده'. باید یا صبر کنی یا یک کلید جدید بسازی.")
        elif "404" in err:
            bot.reply_to(message, "❌ مدل رو پیدا نمی‌کنم. احتمالاً باید از gemini-pro استفاده کنیم.")
        else:
            bot.reply_to(message, f"خطای ناشناخته: {err[:100]}")

if __name__ == "__main__":
    print("🚀 ربات در حالت عیب‌یابی روشن شد...")
    bot.infinity_polling()
