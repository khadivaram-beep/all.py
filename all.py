import requests
import time
import sqlite3
import random
import string
from datetime import datetime

# --- بخش ۱: پیکربندی و متغیرهای حیاتی سیستم ---
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs" # توکن اتصال به بازوی بله
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}" # آدرس پایه برای فراخوانی متدها
ADMIN_ID = 802549012  # آیدی مدیر جهت دریافت گزارشات فوق محرمانه
ADMIN_PASSWORD = "1109" # رمز عبور ورود به پنل مدیریت دیتابیس

# --- بخش ۲: مدیریت پایگاه داده (SQLite) ---
def init_db():
    conn = sqlite3.connect('warehouse_secure.db') # اتصال به فایل دیتابیس
    cursor = conn.cursor()
    # ایجاد جدول انبار: ذخیره مشخصات کالا، کاربر ثبت‌کننده و کد رهگیری
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (track_id TEXT PRIMARY KEY, name TEXT, brand TEXT, 
                       price INTEGER, year TEXT, user_id INTEGER, reg_date TEXT)''')
    # ایجاد جدول لاگ: ثبت تاریخچه تمام استعلامات و فعالیت‌های کاربران
    cursor.execute('''CREATE TABLE IF NOT EXISTS activity_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       user_id INTEGER, user_name TEXT, action TEXT, log_date TEXT)''')
    conn.commit()
    conn.close()

init_db() # اجرای تابع برای اطمینان از وجود جداول در ابتدای کار
user_steps = {} # حافظه موقت (State Machine) برای مدیریت مراحل ثبت کالا بدون هنگ کردن

# --- بخش ۳: توابع کمکی ربات ---
def send_msg(chat_id, text, reply_markup=None):
    # تابع ارسال پیام که از متد sendMessage بله استفاده می‌کند
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=data)

def log_activity(u_id, u_name, action):
    # تابع ثبت وقایع: هر فعالیتی هم در دیتابیس ذخیره شده و هم به مدیر گزارش می‌شود
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect('warehouse_secure.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activity_logs (user_id, user_name, action, log_date) VALUES (?, ?, ?, ?)", 
                   (u_id, u_name, action, now))
    conn.commit()
    conn.close()
    # ارسال گزارش زنده (Real-time Monitoring) برای مدیر
    report = f"🕵️ گزارش: {u_name} ({u_id}) -> {action} در {now}"
    send_msg(ADMIN_ID, report)

def main_menu():
    # طراحی منوی شیشه‌ای (Inline Keyboard) برای سهولت کاربری
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول جدید", "callback_data": "add"}],
            [{"text": "📈 آمار کل انبار", "callback_data": "stats"}],
            [{"text": "🗑 حذف کالا", "callback_data": "delete"}, {"text": "🛡 پنل مدیریت", "callback_data": "admin_panel"}]
        ]
    }

# --- بخش ۴: حلقه اصلی پردازش پیام‌ها (Polling) ---
print("💎 سیستم انبارداری VIP با موفقیت ران شد...")
last_update_id = None
while True:
    updates = requests.get(f"{BASE_URL}/getUpdates", params={'offset': last_update_id, 'timeout': 20}).json()
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            user_info = update.get("callback_query", update.get("message", {})).get("from", {})
            u_id, u_name = user_info.get("id"), user_info.get("first_name", "کاربر")

            # --- مدیریت کلیک بر روی دکمه‌ها (Callback Queries) ---
            if "callback_query" in update:
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]

                if data == "stats":
                    # پردازش داده‌های دیتابیس برای نمایش آمار تجمعی (تعداد، برندها و جمع قیمت)
                    log_activity(u_id, u_name, "مشاهده آمار کل")
                    conn = sqlite3.connect('warehouse_secure.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*), SUM(price), GROUP_CONCAT(DISTINCT brand) FROM inventory")
                    count, total, brands = cursor.fetchone()
                    conn.close()
                    res = f"📊 آمار انبار:\n📦 تعداد: {count}\n🏳️ برندها: {brands}\n💰 ارزش کل: {total or 0}"
                    send_msg(chat_id, res, reply_markup=main_menu())

                elif data == "add":
                    # شروع فرآیند گام‌به‌گام ثبت کالا در دیتابیس
                    user_steps[chat_id] = {"step": "name"}
                    send_msg(chat_id, "🛒 نام کالا را ارسال کنید:")

                elif data == "admin_panel":
                    # ورود به بخش امنیتی با فعال‌سازی گام احراز هویت
                    user_steps[chat_id] = {"step": "auth"}
                    send_msg(chat_id, "🔐 رمز عبور مدیریت را وارد کنید:")

            # --- مدیریت ورودی‌های متنی و منطق دیتابیس (Message Handling) ---
            elif "message" in update and "text" in update["message"]:
                chat_id, text = update["message"]["chat"]["id"], update["message"]["text"]

                if text in ["/start", "سلام"]:
                    send_msg(chat_id, f"سلام {u_name}! منوی مدیریت آماده است:", reply_markup=main_menu())
                
                elif chat_id in user_steps:
                    step = user_steps[chat_id]["step"]

                    if step == "auth": # بررسی رمز عبور (Authentication)
                        if text == ADMIN_PASSWORD:
                            send_msg(chat_id, "✅ تایید شد. گزارشات برای @khadivaram ارسال و در دیتابیس ثبت شد.")
                            log_activity(u_id, u_name, "ورود موفق به پنل مدیریت")
                        else:
                            send_msg(chat_id, "❌ رمز اشتباه! دسترسی مسدود شد.")
                        del user_steps[chat_id]

                    elif step == "name":
                        user_steps[chat_id].update({"name": text, "step": "brand"})
                        send_msg(chat_id, "🏳️ نام برند:")

                    elif step == "brand":
                        user_steps[chat_id].update({"brand": text, "step": "price"})
                        send_msg(chat_id, "💰 قیمت را به عدد وارد کنید:")

                    elif step == "price":
                        user_steps[chat_id].update({"price": text, "step": "year"})
                        send_msg(chat_id, "📅 سال تولید:")

                    elif step == "year":
                        # پایان ثبت کالا: تولید کد رهگیری رندوم و ذخیره نهایی در دیتابیس
                        tid = ''.join(random.choices(string.digits, k=6))
                        now = datetime.now().strftime("%Y-%m-%d %H:%M")
                        conn = sqlite3.connect('warehouse_secure.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?,?)", 
                                       (tid, user_steps[chat_id]['name'], user_steps[chat_id]['brand'], 
                                        int(user_steps[chat_id]['price']), text, chat_id, now))
                        conn.commit(); conn.close()
                        send_msg(chat_id, f"✅ کالا با کد رهگیری {tid} ثبت شد.", reply_markup=main_menu())
                        log_activity(u_id, u_name, f"ثبت کالا (کد: {tid})")
                        del user_steps[chat_id]

    time.sleep(0.5) # وقفه کوتاه برای جلوگیری از فشار به پردازنده سرور
