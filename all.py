import telebot

# ۱. توکن جدید بازوی بله
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"

# ۲. تنظیم آدرس سرور بله (Base URL)
bot = telebot.TeleBot(BALE_TOKEN, base_url="https://tapi.bale.ai/bot")

# ۳. هندلر برای تست نقل مکان به بله
@bot.message_handler(func=lambda message: True)
def handle_bale_test(message):
    user_text = message.text
    print(f"📥 پیام از بله رسید: {user_text}") # توی ترمینال نمایش میده
    
    if user_text == "سلام":
        bot.reply_to(message, "علیک! علیرضا جان، نقل مکان به «بله» با موفقیت انجام شد. 🚀🏠")
    else:
        bot.reply_to(message, "پیام شما در بستر بله دریافت شد. سامانه آماده دستور بعدی است.")

if __name__ == "__main__":
    print("---------------------------------------")
    print("🚀 بازوی @Next_Gen_bot در بله فعال شد!")
    print("علیرضا، برو توی بله و بهش بگو 'سلام'")
    print("---------------------------------------")
    bot.infinity_polling()
