import requests
import time
import sqlite3
from datetime import datetime

# -------------------- تنظیمات --------------------
# توکن و آدرس دقیق بله
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
ADMIN_ID = 1410727630 
ADMIN_PASSWORD = "1109"
# ------------------------------------------------

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
    url = f"{BASE_URL}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

init_db()
user_steps = {}
last_update_id = None

print("✅ دیتابیس اوکی شد.")
print("🚀 ربات علیرضا روشن شد... (تست کن)")

while True:
    try:
        # متد دریافت پیام
        get_url = f"{BASE_URL}/getUpdates"
        response = requests.get(get_url, params={'offset': last_update_id, 'timeout': 10})
        
        if response.status_code == 200:
            updates = response.json()
            if updates.get("ok"):
                for update in updates.get("result", []):
                    last_update_id = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = str(update["message"]["text"]).strip()
                        u_name = update["message"]["from"].get("first_name", "کاربر")
                        
                        print(f"📩 پیام رسید: {text}")

                        # بخش ادمین
                        if text == ADMIN_PASSWORD:
                            conn = sqlite3.connect('warehouse_final.db')
                            count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
                            conn.close()
                            send_msg(chat_id, f"📊 آمار انبار شما:\nتعداد کل: {count}")
                            continue

                        # منوی شروع
                        if text == "/start":
                            markup = {"inline_keyboard": [[{"text": "➕ ثبت کالا", "callback_data": "add"}]]}
                            send_msg(chat_id, "سلام! برای ثبت محصول دکمه رو بزن:", reply_markup=markup)
                            continue

                        # فرآیند ثبت
                        if chat_id in user_steps:
                            step = user_steps[chat_id]["step"]
                            if step == "name":
                                user_steps[chat_id].update({"name": text, "step": "brand"})
                                send_msg(chat_id, "نام برند؟")
                            elif step == "brand":
                                user_steps[chat_id].update({"brand": text, "step": "price"})
                                send_msg(chat_id, "قیمت؟")
                            elif step == "price":
                                user_steps[chat_id].update({"price": text, "step": "year"})
                                send_msg(chat_id, "سال تولید؟")
                            elif step == "year":
                                d = user_steps[chat_id]
                                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                                
                                conn = sqlite3.connect('warehouse_final.db')
                                conn.execute("INSERT INTO products (name, brand, price, year, user_id, user_name, reg_date) VALUES (?,?,?,?,?,?,?)",
                                             (d['name'], d['brand'], d['price'], text, chat_id, u_name, now))
                                conn.commit()
                                conn.close()
                                
                                send_msg(chat_id, "✅ با موفقیت ثبت شد.")
                                # ارسال گزارش به خودت
                                send_msg(ADMIN_ID, f"🚀 کالا جدید:\n📦 {d['name']}\n👤 ثبت توسط: {u_name}")
                                del user_steps[chat_id]

                    elif "callback_query" in update:
                        chat_id = update["callback_query"]["message"]["chat"]["id"]
                        if update["callback_query"]["data"] == "add":
                            user_steps[chat_id] = {"step": "name"}
                            send_msg(chat_id, "نام کالا رو بنویس:")

        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            time.sleep(5)

    except Exception as e:
        print(f"⚠️ خطای موقت: {e}")
        time.sleep(2)
