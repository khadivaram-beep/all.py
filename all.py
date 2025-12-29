import requests
import time
import sqlite3
from datetime import datetime

# -------------------- تنظیمات اختصاصی علیرضا --------------------
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
ADMIN_ID = 1410727630  # آیدی شما
ADMIN_PASSWORD = "1109"
# -----------------------------------------------------------

def init_db():
    conn = sqlite3.connect('warehouse_final.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, brand TEXT, price TEXT, year TEXT, 
                       user_id INTEGER, user_name TEXT, reg_date TEXT)''')
    conn.commit()
    conn.close()

def send_msg(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: data['reply_markup'] = reply_markup
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=data, timeout=10)
    except:
        pass

init_db()
user_steps = {}
last_update_id = None
print("🚀 ربات با آیدی مدیریت 1410727630 فعال شد...")

while True:
    try:
        response = requests.get(f"{BASE_URL}/getUpdates", params={'offset': last_update_id, 'timeout': 15})
        updates = response.json()
        
        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
                
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = str(update["message"]["text"])
                    u_name = update["message"]["from"].get("first_name", "کاربر")

                    if text == ADMIN_PASSWORD:
                        conn = sqlite3.connect('warehouse_final.db')
                        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
                        conn.close()
                        msg = f"📊 **پنل مدیریت**\n📦 تعداد کل کالاها: {count}\n⏰ زمان: {datetime.now().strftime('%H:%M')}"
                        send_msg(chat_id, msg)
                        continue

                    if text in ["/start", "سلام"]:
                        markup = {"inline_keyboard": [[{"text": "➕ ثبت محصول", "callback_data": "add"}]]}
                        send_msg(chat_id, "به سامانه انبارداری خوش آمدید:", reply_markup=markup)
                        continue

                    if chat_id in user_steps:
                        step = user_steps[chat_id]["step"]
                        if step == "name":
                            user_steps[chat_id].update({"name": text, "step": "brand"})
                            send_msg(chat_id, "🏳️ نام برند:")
                        elif step == "brand":
                            user_steps[chat_id].update({"brand_name": text, "step": "price"})
                            send_msg(chat_id, "💰 قیمت:")
                        elif step == "price":
                            user_steps[chat_id].update({"price": text, "step": "year"})
                            send_msg(chat_id, "📅 سال تولید:")
                        elif step == "year":
                            d = user_steps[chat_id]
                            reg_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                            
                            conn = sqlite3.connect('warehouse_final.db')
                            cur = conn.cursor()
                            cur.execute("INSERT INTO products (name,brand,price,year,user_id,user_name,reg_date) VALUES (?,?,?,?,?,?,?)",
                                        (d['name'], d['brand_name'], d['price'], text, chat_id, u_name, reg_date))
                            db_id = cur.lastrowid
                            conn.commit(); conn.close()
                            
                            send_msg(chat_id, "✅ محصول با موفقیت ثبت شد.")
                            
                            report = (f"🕵️‍♂️ **ثبت جدید**\n"
                                      f"📦 کالا: {d['name']}\n"
                                      f"🏳️ برند: {d['brand_name']}\n"
                                      f"💰 قیمت: {d['price']}\n"
                                      f"👤 توسط: {u_name}\n"
                                      f"🆔 کد: {db_id}")
                            send_msg(ADMIN_ID, report)
                            del user_steps[chat_id]

                elif "callback_query" in update:
                    chat_id = update["callback_query"]["message"]["chat"]["id"]
                    if update["callback_query"]["data"] == "add":
                        user_steps[chat_id] = {"step": "name"}
                        send_msg(chat_id, "🛒 نام کالا را وارد کنید:")

    except Exception as e:
        print(f"⚠️ خطای شبکه: {e}")
        time.sleep(2)
