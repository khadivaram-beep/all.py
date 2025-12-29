import telebot
import google.generativeai as genai

# ۱. اطلاعات اصلی
GOOGLE_API_KEY = "AIzaSyDtTMrU6G8_ZJG5OXrQVCX-RE989YFn9s0"
BOT_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"

# ۲. اتصال به هوش مصنوعی
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ۳. تنظیمات بله (خیلی مهم)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False) # threaded رو False بذار
telebot.apihelper.API_URL = "https://api.ble.ir/bot{0}/{1}"
telebot.apihelper.CUSTOM_HEADERS = {'User-Agent': 'Mozilla/5.0'}

# ۴. بخش دریافت پیام
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        print(f"📥 پیام رسید: {message.text}")
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
        print("📤 پاسخ ارسال شد.")
    except Exception as e:
        print(f"❌ خطا در پردازش: {e}")

# ۵. اجرای مستقیم (بدون چک کردن وضعیت اولیه)
if __name__ == "__main__":
    print("🚀 ربات علیرضا در حال استارت...")
    # از polling معمولی استفاده می‌کنیم تا گیر get_me نیفتیم
    bot.polling(none_stop=True, skip_pending=True)
