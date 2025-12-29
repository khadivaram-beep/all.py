import telebot
import requests

# اطلاعات اصلی
TELEGRAM_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
GOOGLE_API_KEY = "AIzaSyADduA9rZ9VQSDaCYVp7_L0-Cr5gbjwYAE"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(text):
    # تغییر از v1beta به v1 (نسخه پایدار)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": text}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: {result.get('error', {}).get('message', 'Not Found')}"
    except:
        return "سرور پاسخگو نیست."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📥 پیام رسید: {message.text}")
    bot_response = get_gemini_response(message.text)
    bot.reply_to(message, bot_response)

if __name__ == "__main__":
    print("🚀 آخرین تست هوش مصنوعی...")
    bot.infinity_polling()
