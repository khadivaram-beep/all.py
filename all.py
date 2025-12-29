import telebot
import requests
import json

# ۱. اطلاعات اصلی (تلگرام و کلید جدید گوگل)
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyADduA9rZ9VQSDaCYVp7_L0-Cr5gbjwYAE"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(text):
    # استفاده از مدل 1.5-flash که بسیار سریع و پایدار است
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": text}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # نمایش خطای احتمالی برای عیب‌یابی
            error_msg = result.get('error', {}).get('message', 'خطای ناشناخته')
            return f"❌ خطای گوگل: {error_msg}"
    except Exception as e:
        return "⚠️ ارتباط با هوش مصنوعی قطع شد، دوباره تلاش کن."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📥 پیام از {message.from_user.first_name}: {message.text}")
    
    # دریافت پاسخ از هوش مصنوعی
    bot_response = get_gemini_response(message.text)
    
    # ارسال پاسخ به تلگرام
    bot.reply_to(message, bot_response)
    print("✅ پاسخ ارسال شد.")

if __name__ == "__main__":
    print("---------------------------------------")
    print("🚀 تبریک! ربات با کلید جدید روشن شد.")
    print("📡 همین الان توی تلگرام تستش کن...")
    print("---------------------------------------")
    bot.infinity_polling()
