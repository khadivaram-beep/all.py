import requests
import time
import sqlite3
import random
import string
from datetime import datetime

# --- تنظیمات اصلی ---
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0" # توکن جدید شما
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
ADMIN_ID = None  # این متغیر بعد از اولین پیام شما خودکار پر می‌شود
ADMIN_PASSWORD = "1109"

# --- ایجاد ساختار دیتابیس (حافظه دائمی سیستم) ---
def init_db():
    conn = sqlite3.connect('warehouse_final.db')
    cursor = conn.cursor()
    # جدول محصولات انبار
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (track_id TEXT PRIMARY KEY, name TEXT, brand TEXT, 
                       price INTEGER, year TEXT, user_id INTEGER, reg_date TEXT)''')
    # جدول گزارشات امنیتی مدیر
    cursor.execute('''CREATE TABLE IF NOT EXISTS activity_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       user_id INTEGER, user_name TEXT, action TEXT, log_date TEXT)''')
    conn.commit()
    conn.close()

init_db()
user_steps = {}

# --- تابع ارسال پیام با سیستم عیب‌یاب ---
def send_msg(chat_id, text, reply_markup=None):
    if not chat_id: return
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    res = requests.post(f"{BASE_URL}/sendMessage", json=data).json()
    if not res.get("ok"):
        print(f"❌ خطا در ارسال: {res.get('description')}")

# --- ثبت وقایع و ارسال مستقیم به مدیر ---
def log_activity(u_id, u_name, action):
    global ADMIN_ID
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect('warehouse_final.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activity_logs (user_id, user_name, action, log_date) VALUES (?, ?, ?, ?)", 
                   (u_id, u_name, action, now))
    conn.commit()
    conn.close()
    
    # ارسال گزارش لحظه‌ای برای شما (مدیر)
    if ADMIN_ID:
        report = f"🕵️ **گزارش زنده برای مدیر**\n👤 کاربر: {u_name}\n⚡️ اقدام: {action}\n⏰ زمان: {now}"
        send_msg(ADMIN_ID, report)

# --- طراحی منوی اصلی (رابط کاربری) ---
def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول جدید", "callback_data": "add"}],
            [{"text": "📈 آمار کل انبار", "callback_data": "stats"}],
            [{"text": "🗑 حذف کالا", "callback_data": "delete"}, {"text": "🛡 پنل مدیریت", "callback_data": "admin_panel"}]
        ]
    }

# --- حلقه اصلی پردازش (بدون وقفه) ---
print("🚀 ربات با موفقیت فعال شد. علیرضا جان، یک پیام در بله بده تا ادمین ست شود...")
last_update_id = None
while True:
    try:
        updates = requests.get(f"{BASE_URL}/getUpdates", params={'offset': last_update_id, 'timeout': 20}).json()
        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
                
                # استخراج اطلاعات کاربر
                user_info = update.get("callback_query", update.get("message", {})).get("from", {})
                u_id, u_name = user_info.get("id"), user_info.get("first_name", "کاربر")
                
                # ست کردن خودکار آیدی مدیر در اولین پیام
                if ADMIN_ID is None:
                    ADMIN_ID = u_id
                    print(f"✅ آیدی مدیر با موفقیت ست شد: {ADMIN_ID}")

                # الف) مدیریت دکمه‌های شیشه‌ای
                if "callback_query" in update:
                    chat_id = update["callback_query"]["message"]["chat"]["id"]
                    data = update["callback_query"]["data"]

                    if data == "stats":
                        log_activity(u_id, u_name, "استعلام آمار کل")
                        conn = sqlite3.connect('warehouse_final.db')
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*), SUM(price), GROUP_CONCAT(DISTINCT brand) FROM inventory")
                        count, total, brands = cursor.fetchone()
                        conn.close()
                        res = f"📊 **وضعیت انبار**\n📦 تعداد: {count}\n🏳️ برندها: {brands or 'خالی'}\n💰 ارزش کل: {total or 0}"
                        send_msg(chat_id, res, reply_markup=main_menu())

                    elif data == "add":
                        user_steps[chat_id] = {"step": "name"}
                        send_msg(chat_id, "🛒 نام کالا را وارد کنید:")

                    elif data == "admin_panel":
                        user_steps[chat_id] = {"step": "auth"}
                        send_msg(chat_id, "🔐 رمز عبور مدیریت را وارد کنید:")

                # ب) مدیریت پیام‌های متنی و مراحل دیتابیس
                elif "message" in update and "text" in update["message"]:
                    chat_id, text = update["message"]["chat"]["id"], update["message"]["text"]

                    if text in ["/start", "سلام"]:
                        send_msg(chat_id, f"سلام {u_name}! خوش آمدی.", reply_markup=main_menu())
                    
                    elif chat_id in user_steps:
                        step = user_steps[chat_id]["step"]

                        if step == "auth":
                            if text == ADMIN_PASSWORD:
                                send_msg(chat_id, "✅ تایید شد. تمام گزارشات استعلام و ثبت برای شما (سازنده) ارسال شد.")
                                log_activity(u_id, u_name, "ورود به پنل مدیریت")
                            else:
                                send_msg(chat_id, "❌ رمز اشتباه!")
                            del user_steps[chat_id]

                        elif step == "name":
                            user_steps[chat_id].update({"name": text, "step": "brand"})
                            send_msg(chat_id, "🏳️ نام برند:")
                        elif step == "brand":
                            user_steps[chat_id].update({"brand": text, "step": "price"})
                            send_msg(chat_id, "💰 قیمت (عدد):")
                        elif step == "price":
                            user_steps[chat_id].update({"price": text, "step": "year"})
                            send_msg(chat_id, "📅 سال تولید:")
                        elif step == "year":
                            tid = ''.join(random.choices(string.digits, k=6))
                            now = datetime.now().strftime("%Y-%m-%d %H:%M")
                            conn = sqlite3.connect('warehouse_final.db')
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?,?)", 
                                           (tid, user_steps[chat_id]['name'], user_steps[chat_id]['brand'], 
                                            int(user_steps[chat_id]['price']), text, chat_id, now))
                            conn.commit(); conn.close()
                            send_msg(chat_id, f"✅ ثبت شد. کد رهگیری: `{tid}`", reply_markup=main_menu())
                            log_activity(u_id, u_name, f"ثبت کالا کد {tid}")
                            del user_steps[chat_id]

    except Exception as e:
        print(f"⚠️ خطای شبکه: {e}")
    time.sleep(0.5)
