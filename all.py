import telebot

# ۱. توکن اختصاصی ربات بله (از BotFather بله بگیر)
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"

# ۲. تنظیم آدرس API بله برای کتابخانه (بسیار مهم)
bot = telebot.TeleBot(BALE_TOKEN, base_url="https://tapi.bale.ai/bot")

# ۳. هندلر برای تست نقل مکان
@bot.message_handler(func=lambda message: True)
def handle_migration_test(message):
    text = message.text
    print(f"📥 پیام جدید در بله: {text}") # نمایش در ترمینال خودت
    
    if text == "سلام":
        bot.reply_to(message, "علیک! علیرضا جان، نقل مکان به «بله» با موفقیت انجام شد. 🚀🏠")
    else:
        bot.reply_to(message, "ارتباط برقراره! من پیام رو در بله گرفتم.")

if __name__ == "__main__":
    print("---------------------------------------")
    print("🛰 ربات آماده تست در بله است...")
    print("برو توی بله و بهش بگو 'سلام'")
    print("---------------------------------------")
    bot.infinity_polling()
