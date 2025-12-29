import requests
import time
import sqlite3

# ۱. تنظیمات
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

# !!! علیرضا جان، بعد از اولین پیام، آیدی عددی که در ترمینال چاپ میشه رو جای صفر بذار !!!
ADMIN_ID = 0  

def init_db():
    conn = sqlite3.connect('warehouse.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, brand TEXT, price INTEGER, year TEXT)''')
    conn.commit()
    conn.close()

init_db()
user_steps = {}

def send_msg(chat_id, text, reply_markup=None):
    if chat_id == 0: return # جلوگیری از خطا قبل از تنظیم آیدی مدیر
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=data)
    except:
        print("❌ خطا در ارسال پیام")

def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول", "callback_data": "add"}, {"text": "🔍 جستجوی کالا", "callback_data": "search"}],
            [{"text": "📋 لیست کل انبار", "callback_data": "view_all"}],
            [{"text": "📈 آمار کل (BI)", "callback_data": "stats"}]
        ]
    }

def get_updates(offset=None):
    try:
        return requests.get(f"{BASE_URL}/getUpdates", params={'offset': offset, 'timeout': 20}).json()
    except: return None

print("💎 سامانه انبارداری با قابلیت گزارش به مدیریت فعال شد...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            
            # پیدا کردن آیدی عددی علیرضا (مدیر)
            current_chat_id = None
            current_user = ""

            if "callback_query" in update:
                current_chat_id = update["callback_query"]["message"]["chat"]["id"]
                current_user = update["callback_query"]["from"].get("username", "بدون آیدی")
                data = update["callback_query"]["data"]
                
                # چاپ آیدی در ترمینال برای اینکه علیرضا بتونه کپی کنه
                print(f"🆔 آیدی کاربر {current_user}: {current_chat_id}")

                if data == "add":
                    user_steps[current_chat_id] = {"step": "name"}
                    send_msg(current_chat_id, "🛒 نام کالا را وارد کنید:")
                
                elif data == "stats":
                    conn = sqlite3.connect('warehouse.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*), SUM(price) FROM inventory")
                    count, total_price = cursor.fetchone()
                    conn.close()
                    msg = f"📊 گزارش مدیریتی:\nتعداد: {count}\nارزش: {total_price or 0}"
                    send_msg(current_chat_id, msg, reply_markup=main_menu())

            elif "message" in update and "text" in update["message"]:
                current_chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                
                print(f"🆔 آیدی کاربر: {current_chat_id} | متن: {text}")

                if text in ["/start", "سلام"]:
                    send_msg(current_chat_id, "سلام علیرضا! پنل آماده است:", reply_markup=main_menu())
                
                elif current_chat_id in user_steps:
                    step = user_steps[current_chat_id]["step"]
                    if step == "name":
                        user_steps[current_chat_id].update({"name": text, "step": "brand"})
                        send_msg(current_chat_id, "🏳️ برند:")
                    elif step == "brand":
                        user_steps[current_chat_id].update({"brand": text, "step": "price"})
                        send_msg(current_chat_id, "💰 قیمت:")
                    elif step == "price":
                        user_steps[current_chat_id].update({"price": text, "step": "year"})
                        send_msg(current_chat_id, "📅 سال تولید:")
                    elif step == "year":
                        name = user_steps[current_chat_id]['name']
                        brand = user_steps[current_chat_id]['brand']
                        price = user_steps[current_chat_id]['price']
                        year = text
                        
                        # ذخیره در دیتابیس
                        conn = sqlite3.connect('warehouse.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO inventory (name, brand, price, year) VALUES (?, ?, ?, ?)", 
                                       (name, brand, int(price), year))
                        conn.commit(); conn.close()
                        
                        # ارسال تاییدیه به کاربر
                        send_msg(current_chat_id, "✅ در دیتابیس ثبت شد.", reply_markup=main_menu())
                        
                        # 📢 ارسال برای مدیر (@khadivaram)
                        report = (f"🚀 **ارسال برای مدیر**\n\n"
                                  f"📦 محصول جدید ثبت شد:\n"
                                  f"👤 توسط: {current_chat_id}\n"
                                  f"🏷 نام: {name}\n"
                                  f"🏳️ برند: {brand}\n"
                                  f"💰 قیمت: {price}\n"
                                  f"📅 سال: {year}")
                        send_msg(ADMIN_ID, report)
                        
                        del user_steps[current_chat_id]

    time.sleep(0.5)
