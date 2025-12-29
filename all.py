import requests
import time
import sqlite3
from datetime import datetime

# ۱. تنظیمات (توکن و آیدی مدیر)
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
ADMIN_ID = 0  # <--- آیدی عددی خودت رو اینجا بذار (مثلاً 198273645)
ADMIN_PASSWORD = "1109"

def init_db():
    try:
        conn = sqlite3.connect('warehouse_final.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           name TEXT, brand TEXT, price TEXT, year TEXT, 
                           u_id INTEGER, u_name TEXT, reg_date TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ خطای دیتابیس: {e}")

init_db()
user_steps = {}

def send_msg(chat_id, text, reply_markup=None):
    if chat_id == 0: return
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: data['reply_markup'] = reply_markup
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=data, timeout=5)
    except Exception as e:
        print(f"⚠️ خطای ارسال پیام: {e}")

def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول جدید", "callback_data": "add"}],
            [{"text": "📊 پنل مدیریت (رمز)", "callback_data": "ask_pass"}]
        ]
    }

def get_updates(offset=None):
    try:
        return requests.get(f"{BASE_URL}/getUpdates", params={'offset': offset, 'timeout': 10}).json()
    except:
        return None

print("💎 ربات ضد ضربه و پایدار فعال شد. (CTRL+C برای خروج)")

last_update_id = None

# حلقه اصلی با محافظ ضد کرش
while True:
    try:
        updates = get_updates(last_update_id)
        
        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
                
                # --- بخش دکمه‌ها ---
                if "callback_query" in update:
                    chat_id = update["callback_query"]["message"]["chat"]["id"]
                    data = update["callback_query"]["data"]
                    
                    # اولویت‌بندی: اگر در حال ثبت است، اجازه کار دیگر نده
                    if chat_id in user_steps and data != "ask_pass":
                        send_msg(chat_id, "⚠️ لطفاً کار فعلی (ثبت محصول) را تمام کنید.")
                        continue

                    if data == "add":
                        user_steps[chat_id] = {"step": "name"}
                        send_msg(chat_id, "🛒 نام محصول را وارد کنید:")
                    elif data == "ask_pass":
                        send_msg(chat_id, "🔐 رمز عبور مدیریت را وارد کنید:")

                # --- بخش پیام متنی ---
                elif "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = str(update["message"]["text"]) # تبدیل به رشته برای جلوگیری از ارور
                    user_info = update["message"]["from"]
                    
                    print(f"📩 پیام جدید از {chat_id}: {text}")

                    # ۱. بررسی رمز عبور (ارسال آمار به PV)
                    if text == ADMIN_PASSWORD:
                        conn = sqlite3.connect('warehouse_final.db')
                        cursor = conn.cursor()
                        count = cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
                        conn.close()
                        
                        report_pv = (f"📑 **گزارش محرمانه سیستم**\n"
                                     f"📦 موجودی کل انبار: {count} قلم\n"
                                     f"⏰ زمان سرور: {datetime.now().strftime('%H:%M:%S')}")
                        
                        send_msg(ADMIN_ID, report_pv)
                        send_msg(chat_id, "✅ ارسال شد.")
                        continue

                    # ۲. دستورات شروع
                    if text in ["/start", "سلام"]:
                        send_msg(chat_id, "منوی انبارداری:", reply_markup=main_menu())
                    
                    # ۳. مراحل ثبت کالا
                    elif chat_id in user_steps:
                        step = user_steps[chat_id]["step"]
                        
                        if step == "name":
                            user_steps[chat_id].update({"name": text, "step": "brand"})
                            send_msg(chat_id, "🏳️ برند محصول:")
                        
                        elif step ==
