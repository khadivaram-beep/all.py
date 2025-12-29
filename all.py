import requests
import time
import sqlite3
from datetime import datetime

# ۱. تنظیمات اختصاصی
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0" # توکن خودت رو اینجا چک کن
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
ADMIN_ID = 0  # !!! خیلی مهم: آیدی عددی خودت را اینجا بگذار تا گزارش‌ها به PV تو بیاید !!!
ADMIN_PASSWORD = "1109"

def init_db():
    conn = sqlite3.connect('warehouse_secure.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, brand TEXT, price TEXT, year TEXT, 
                       u_id INTEGER, u_name TEXT, reg_date TEXT)''')
    conn.commit()
    conn.close()

init_db()
user_steps = {}

def send_msg(chat_id, text, reply_markup=None):
    if chat_id == 0: return
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: data['reply_markup'] = reply_markup
    try: requests.post(f"{BASE_URL}/sendMessage", json=data)
    except: pass

def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول جدید", "callback_data": "add"}],
            [{"text": "📊 استعلام آمار (رمز)", "callback_data": "ask_pass"}]
        ]
    }

def get_updates(offset=None):
    try: return requests.get(f"{BASE_URL}/getUpdates", params={'offset': offset, 'timeout': 20}).json()
    except: return None

print("🕵️‍♂️ سامانه مانیتورینگ مستقیم PV فعال شد...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            
            if "callback_query" in update:
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]
                
                if chat_id in user_steps and data != "ask_pass":
                    send_msg(chat_id, "⚠️ لطفاً ابتدا فرآیند ثبت فعلی را تکمیل کنید.")
                    continue

                if data == "add":
                    user_steps[chat_id] = {"step": "name"}
                    send_msg(chat_id, "🛒 نام محصول را وارد کنید:")
                elif data == "ask_pass":
                    send_msg(chat_id, "🔐 رمز عبور مدیریت را وارد کنید:")

            elif "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                user_info = update["message"]["from"]

                # الف) چک کردن رمز و ارسال آمار "فقط به پی‌وی مدیر"
                if text == ADMIN_PASSWORD:
                    conn = sqlite3.connect('warehouse_secure.db')
                    cursor = conn.cursor()
                    count = cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
                    conn.close()
                    
                    report_pv = (f"📑 **گزارش محرمانه کل انبار**\n"
                                 f"👤 مدیر عزیز، آمار لحظه‌ای دیتابیس:\n"
                                 f"📦 تعداد کل کالاها: {count}\n"
                                 f"⏰ ساعت گزارش: {datetime.now().strftime('%H:%M:%S')}")
                    
                    # اینجا جادوی کد است: ارسال فقط به ADMIN_ID (پی‌وی تو)
                    send_msg(ADMIN_ID, report_pv)
                    send_msg(chat_id, "✅ گزارش با موفقیت به پی‌وی مدیریت ارسال شد.")
                    continue

                if text in ["/start", "سلام"]:
                    send_msg(chat_id, "خوش آمدید. لطفاً انتخاب کنید:", reply_markup=main_menu())
                
                elif chat_id in user_steps:
                    step = user_steps[chat_id]["step"]
                    if step == "name":
                        user_steps[chat_id].update({"name": text, "step": "brand"})
                        send_msg(chat_id, "🏳️ برند محصول:")
                    elif step == "brand":
                        user_steps[chat_id].update({"brand": text, "step": "price"})
                        send_msg(chat_id, "💰 قیمت محصول:")
                    elif step == "price":
                        user_steps[chat_id].update({"price": text, "step": "year"})
                        send_msg(chat_id, "📅 سال تولید:")
                    elif step == "year":
                        now = datetime.now()
                        name, brand, price = user_steps[chat_id]['name'], user_steps[chat_id]['brand'], user_steps[chat_id]['price']
                        reg_date = now.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # ذخیره در دیتابیس
                        conn = sqlite3.connect('warehouse_secure.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO inventory (name, brand, price, year, u_id, u_name, reg_date) VALUES (?,?,?,?,?,?,?)", 
                                       (name, brand, price, text, chat_id, user_info.get("first_name"), reg_date))
                        db_id = cursor.lastrowid
                        conn.commit(); conn.close()
                        
                        send_msg(chat_id, "✅ اطلاعات در دیتابیس ذخیره شد.", reply_markup=main_menu())
                        
                        # 📢 ارسال گزارش ریزبینانه "فقط به پی‌وی مدیر"
                        admin_report = (
                            f"🕵️‍♂️ **گزارش ثبت کالای جدید (PV)**\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"🆔 شناسه: `{db_id}`\n"
                            f"📦 کالا: {name}\n"
                            f"🏳️ برند: {brand}\n"
                            f"💰 قیمت: {price}\n"
                            f"📅 سال: {text}\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"👤 فرستنده: {user_info.get('first_name')} | `{chat_id}`\n"
                            f"⏰ زمان: {reg_date}"
                        )
                        send_msg(ADMIN_ID, admin_report)
                        del user_steps[chat_id]

    time.sleep(0.5)
