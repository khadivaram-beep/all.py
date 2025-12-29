import telebot
import requests
import json

# ۱. اطلاعات اصلی
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(text):
    # آدرس مستقیم API گوگل بدون نیاز به کتابخانه اضافی
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    
    # استخراج متن پاسخ
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"❌ خطای گوگل: {result.get('error', {}).get('message', 'خطای ناشناخته')}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        print(f"📥 پیام رسید: {message.text}")
        
        # دریافت پاسخ از تابع مستقیم
        bot_response = get_gemini_response(message.text)
        
        bot.reply_to(message, bot_response)
        print("✅ پاسخ ارسال شد.")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        bot.reply_to(message, "یه مشکل فنی پیش اومد، دوباره امتحان کن.")

if __name__ == "__main__":
    print("🔥 ربات با اتصال مستقیم فعال شد!")
    bot.infinity_polling()
