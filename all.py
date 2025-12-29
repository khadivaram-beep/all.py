import telebot
import requests
import json

# ۱. اطلاعات اصلی
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(text):
    # تغییر آدرس به v1 و مدل به gemini-pro برای پایداری بیشتر
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        
        # استخراج متن پاسخ
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # اگر gemini-pro هم نشد، یک شانس به مدل flash در نسخه v1 می‌دهیم
            url_alt = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
            response_alt = requests.post(url_alt, headers=headers, data=json.dumps(data))
            result_alt = response_alt.json()
            return result_alt['candidates'][0]['content']['parts'][0]['text']
            
    except Exception as e:
        return f"❌ خطا در پردازش: {str(result.get('error', {}).get('message', 'مدل پیدا نشد'))}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        print(f"📥 پیام رسید: {message.text}")
        bot_response = get_gemini_response(message.text)
        bot.reply_to(message, bot_response)
        print("✅ پاسخ ارسال شد.")
    except:
        bot.reply_to(message, "مشکل در دریافت پاسخ. لطفاً دوباره تلاش کنید.")

if __name__ == "__main__":
    print("🚀 تلاش نهایی با مدل gemini-pro...")
    bot.infinity_polling()
