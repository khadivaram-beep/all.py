import requests
import time
import sqlite3
import random
import string
from datetime import datetime

# ۱. تنظیمات بازو
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
ADMIN_ID = 802549012  # <--- آیدی عددی خودت رو اینجا بذار

def init_db():
    conn = sqlite3.connect('warehouse_public.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (track_id TEXT PRIMARY KEY, name TEXT, brand TEXT, 
                       price INTEGER, year TEXT, user_id INTEGER, reg_date TEXT)''')
    conn.commit()
    conn.close()

init_db()
user_steps = {}

def send_msg(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=data)

def generate_track_id():
    return ''.join(random.choices(string.digits, k=6))

def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول جدید", "callback_data": "add"}],
            [{"text": "📈 آمار کل انبار", "callback_data": "stats"}, {"text": "🗑 حذف با کد رهگیری", "callback_data": "delete"}]
        ]
    }

def get_updates(offset=None):
    try:
        return requests.get(f"{BASE_URL}/getUpdates", params={'offset': offset, 'timeout': 20}).json()
    except: return None

print("🚀 ربات عمومی انبارداری با کد رهگیری فعال شد...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            
            # استخراج اطلاعات کاربر برای گزارش به مدیر
            user_info = update.get("callback_query", update.get("message", {})).get("from", {})
            u_id = user_info.get("id")
            u_name = user_info.get("first_name", "Unknown")

            # الف) مدیریت کلیک دکمه‌ها
            if "callback_query" in update:
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]
                
                # گزارش مشاهده به مدیر
                send_msg(ADMIN_ID, f"👁‍🗨 گزارش: کاربر {u_name} ({u_id}) روی دکمه {data} کلیک کرد.")

                if data == "add":
                    user_steps[chat_id] = {"step": "name"}
                    send_msg(chat_id, "🛒 نام کالا را وارد کنید:")
                
                elif data == "delete":
                    user_steps[chat_id] = {"step": "deleting"}
                    send_msg(chat_id, "🗑 لطفاً **کد رهگیری ۶ رقمی** کالا را ارسال کنید:")

                elif data == "stats":
                    conn = sqlite3.connect('warehouse_public.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*), SUM(price) FROM inventory")
                    count, total = cursor.fetchone()
                    conn.close()
                    send_msg(chat_id, f"📊 آمار کل:\nتعداد: {count}\nارزش: {total or 0}", reply_markup=main_menu())

            # ب) مدیریت پیام‌های متنی
            elif "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]

                if text in ["/start", "سلام"]:
                    send_msg(chat_id, f"سلام {u_name}! به انبارداری عمومی خوش آمدی:", reply_markup=main_menu())
                
                elif chat_id in user_steps:
                    step = user_steps[chat_id]["step"]
                    
                    if step == "deleting":
                        conn = sqlite3.connect('warehouse_public.db')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM inventory WHERE track_id = ?", (text,))
                        if cursor.rowcount > 0:
                            conn.commit()
                            send_msg(chat_id, "✅ کالا با موفقیت حذف شد.", reply_markup=main_menu())
                            send_msg(ADMIN_ID, f"🗑 هشدار مدیر: کالا با کد {text} توسط کاربر {u_id} حذف شد.")
                        else:
                            send_msg(chat_id, "❌ کد رهگیری معتبر نیست.", reply_markup=main_menu())
                        conn.close()
                        del user_steps[chat_id]

                    elif step == "name":
                        user_steps[chat_id].update({"name": text, "step": "brand"})
                        send_msg(chat_id, "🏳️ نام برند:")
                    elif step == "brand":
                        user_steps[chat_id].update({"brand": text, "step": "price"})
                        send_msg(chat_id, "💰 قیمت (فقط عدد):")
                    elif step == "price":
                        user_steps[chat_id].update({"price": text, "step": "year"})
                        send_msg(chat_id, "📅 سال تولید:")
                    elif step == "year":
                        track = generate_track_id()
                        reg_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # ذخیره در دیتابیس
                        conn = sqlite3.connect('warehouse_public.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                       (track, user_steps[chat_id]['name'], user_steps[chat_id]['brand'], 
                                        int(user_steps[chat_id]['price']), text, chat_id, reg_date))
                        conn.commit(); conn.close()
                        
                        # ارسال کد رهگیری به کاربر
                        send_msg(chat_id, f"✅ ثبت شد!\n🎫 کد رهگیری شما: `{track}`\n(برای حذف کالا در آینده به این کد نیاز دارید)", reply_markup=main_menu())
                        
                        # گزارش کامل به مدیر
                        report = (f"🚀 **ارسال برای مدیر**\n"
                                  f"📦 کالا: {user_steps[chat_id]['name']}\n"
                                  f"🎫 کد: {track}\n"
                                  f"👤 کاربر: {u_name} ({chat_id})\n"
                                  f"⏰ زمان: {reg_date}")
                        send_msg(ADMIN_ID, report)
                        del user_steps[chat_id]

    time.sleep(0.5)
