import telebot
from telebot import types
import sqlite3
import uuid
from datetime import datetime

# ۱. پیکربندی
TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
bot = telebot.TeleBot(TOKEN)

# ۲. ایجاد دیتابیس استراتژیک مدیریت بحران
def init_crisis_db():
    conn = sqlite3.connect('crisis_management.db')
    cursor = conn.cursor()
    # جدول گزارش‌ها: شامل مختصات جغرافیایی، نوع وضعیت و کد پیگیری
    cursor.execute('''CREATE TABLE IF NOT EXISTS reports 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       ticket_id TEXT,
                       user_id INTEGER, 
                       category TEXT, 
                       latitude REAL, 
                       longitude REAL, 
                       status TEXT,
                       timestamp TEXT)''')
    conn.commit()
    conn.close()

init_crisis_db()

# ۳. طراحی منوی فرماندهی
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🚨 اعلام وضعیت بحرانی", request_location=True) # ارسال مستقیم لوکیشن
    btn2 = types.KeyboardButton("📦 لیست منابع موجود")
    btn3 = types.KeyboardButton("🔍 پیگیری وضعیت گزارش")
    btn4 = types.KeyboardButton("📞 تماس با ستاد مرکزی")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start_system(message):
    welcome_text = (
        f"🏛 **سامانه مرکزی مدیریت بحران و توزیع منابع**\n\n"
        f"جناب {message.from_user.first_name}، هویت شما به عنوان شهروند/امدادگر در شبکه ثبت شد.\n"
        f"جهت ارسال گزارش سریع، دکمه 'اعلام وضعیت بحرانی' را بزنید."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

# ۴. دریافت لوکیشن و شروع ثبت گزارش (نبوغ در مدیریت داده مکان‌محور)
@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    user_id = message.from_user.id
    
    # منوی انتخاب نوع بحران
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💊 نیاز دارویی", callback_data=f"crisis_medical_{lat}_{lon}"),
        types.InlineKeyboardButton("🍎 جیره غذایی", callback_data=f"crisis_food_{lat}_{lon}"),
        types.InlineKeyboardButton("🚒 امداد و نجات", callback_data=f"crisis_rescue_{lat}_{lon}"),
        types.InlineKeyboardButton("⚠️ تخریب زیرساخت", callback_data=f"crisis_infra_{lat}_{lon}")
    )
    
    bot.send_message(message.chat.id, "📍 موقعیت شما با دقت نظامی ثبت شد.\nنوع بحران را انتخاب کنید:", reply_markup=markup)

# ۵. پردازش نهایی و ذخیره در دیتابیس با کد رهگیری اختصاصی
@bot.callback_query_handler(func=lambda call: call.data.startswith('crisis_'))
def finalize_report(call):
    data = call.data.split('_')
    category = data[1]
    lat = data[2]
    lon = data[3]
    ticket_id = str(uuid.uuid4())[:8].upper() # تولید کد رهگیری منحصربه‌فرد
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ذخیره در دیتابیس
    conn = sqlite3.connect('crisis_management.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reports (ticket_id, user_id, category, latitude, longitude, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (ticket_id, call.from_user.id, category, lat, lon, "در انتظار بررسی", time_now))
    conn.commit()
    conn.close()

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=f"✅ **گزارش با موفقیت ثبت شد.**\n\n"
                               f"🎫 کد رهگیری: `{ticket_id}`\n"
                               f"🗂 دسته‌بندی: {category}\n"
                               f"⏰ زمان ثبت: {time_now}\n\n"
                               f"تیم‌های امدادی بر اساس اولویت جغرافیایی اعزام خواهند شد.", parse_mode="Markdown")

print("🛰 سامانه مدیریت بحران در حال پایش شبکه...")
bot.infinity_polling()
