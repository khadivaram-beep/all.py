import telebot
from telebot import types
import sqlite3
import uuid
from datetime import datetime

# ۱. اطلاعات اصلی
TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
bot = telebot.TeleBot(TOKEN)

# ۲. ساخت دیتابیس (اگر وجود نداشته باشد)
def init_db():
    conn = sqlite3.connect('crisis_center.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reports 
                      (ticket_id TEXT, user_id INTEGER, category TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ۳. تابع ساخت منوی شیشه‌ای (Inline)
def get_inline_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🚨 ثبت گزارش بحران", callback_data="start_report")
    btn2 = types.InlineKeyboardButton("🔍 پیگیری با کد", callback_data="track_report")
    btn3 = types.InlineKeyboardButton("📦 موجودی انبار", callback_data="view_storage")
    btn4 = types.InlineKeyboardButton("🏢 تماس با مرکز", callback_data="contact_admin")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# ۴. پاسخ به سلام و پیام‌های متنی
@bot.message_handler(func=lambda message: True)
def welcome_text(message):
    user_name = message.from_user.first_name
    if message.text.lower() in ["سلام", "درود", "hi", "/start"]:
        bot.send_message(
            message.chat.id, 
            f"سلام {user_name} عزیز 🏛\nبه **مرکز کنترل و مدیریت بحران** خوش آمدید.\n\nلطفاً یکی از گزینه‌های زیر را برای شروع انتخاب کنید:", 
            reply_markup=get_inline_menu(),
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(message, "⚠️ لطفاً برای تعامل با سامانه از منوی هوشمند زیر استفاده کنید:", reply_markup=get_inline_menu())

# ۵. مدیریت کلیک روی دکمه‌های شیشه‌ای
@bot.callback_query_handler(func=lambda call: True)
def callback_manager(call):
    if call.data == "start_report":
        # ارسال دکمه لوکیشن برای شروع
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("📍 ارسال لوکیشن دقیق برای امداد", request_location=True))
        bot.send_message(call.message.chat.id, "جهت اعزام نیرو، ابتدا لوکیشن خود را بفرستید:", reply_markup=markup)
        
    elif call.data == "view_storage":
        bot.answer_callback_query(call.id, "در حال استعلام از دیتابیس انبار...")
        bot.send_message(call.message.chat.id, "📦 **وضعیت انبار مرکزی:**\n- دارو: ۸۰٪\n- سوخت: ۹۵٪\n- جیره غذایی: ۴۰٪ (نیاز به شارژ)")

    elif call.data == "contact_admin":
        bot.send_message(call.message.chat.id, "📞 خط مستقیم ستاد مرکزی:\n021-12345678")

# ۶. هندلر لوکیشن (ثبت نهایی در دیتابیس)
@bot.message_handler(content_types=['location'])
def handle_location(message):
    ticket = str(uuid.uuid4())[:8].upper()
    # اینجا می‌تونی بقیه مراحل ثبت در دیتابیس رو انجام بدی
    bot.send_message(message.chat.id, f"✅ لوکیشن دریافت شد.\n🎫 کد رهگیری شما در دیتابیس دولتی: `{ticket}`", parse_mode="Markdown")

print("🛰 ربات با منوی شیشه‌ای فعال شد...")
bot.infinity_polling()
