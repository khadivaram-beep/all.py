import requests
import time
import sqlite3
from datetime import datetime

# -------------------- تنظیمات --------------------
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
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
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: data['reply_markup'] = reply_markup
    try: requests.post(f"{BASE_URL}/sendMessage", json=data, timeout=10)
    except: pass

init_db()
user_steps = {}
last_update_id = None
print("🚀 ربات انبارداری فعال شد. منتظر ورود رمز یا ثبت کالا...")

while True:
    try:
        response = requests.get(f"{BASE_URL}/getUpdates", params={'offset': last_update_id, 'timeout': 20})
        updates = response.json()
        
        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
                
                # --- مدیریت دکمه‌ها ---
                if "callback_query" in update:
                    chat_id = update["callback_query"]["message"]["chat"]["id"]
                    data = update["callback_query"]["data"]
                    
                    if data == "add_prod":
                        user_steps[chat_id] = {"step": "name"}
                        send_msg(chat_id, "🛒 نام کالا را وارد کنید:")
                    elif data == "admin_panel":
                        send_msg(chat_id, "🔐 رمز عبور مدیریت را وارد کنید:")

                # --- مدیریت متن‌ها ---
                elif "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = str(update["message"]["text"])
                    u_info = update["message"]["from"]

                    # ۱. بررسی رمز عبور و نمایش آمار در همان لحظه
                    if text == ADMIN_PASSWORD:
                        conn = sqlite3.connect('warehouse_final.db')
                        cur = conn.cursor()
                        # گرفتن آمار کل
                        count = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
                        # گرفتن ۵ ثبت آخر با جزئیات ریز
                        last_items = cur.execute("SELECT name, brand, price, user_name FROM products ORDER BY id DESC LIMIT 5").fetchall()
                        conn.close()
                        
                        report = f"📊 **پنل مدیریت مرکزی**\n\n"
                        report += f"📦 تعداد کل کالاها: {count}\n"
                        report += "🔍 **آخرین ورودی‌ها:**\n"
                        for item in last_items:
                            report += f"▫️ {item[0]} | {item[1]} | {item[2]} (توسط: {item[3]})\n"
                        
                        send_msg(chat_id, report) # آمار همینجا نمایش داده می‌شود
                        continue

                    if text in ["/start", "سلام"]:
                        markup = {
                            "inline_keyboard": [
                                [{"text": "➕ ثبت محصول جدید", "callback_data": "add_prod"}],
                                [{"text": "📊 آمار و جزئیات (رمز)", "callback_data": "admin_panel"}]
                            ]
                        }
                        send_msg(chat_id, "خوش آمدید! گزینه مورد نظر را انتخاب کنید:", reply_markup=markup)
                    
                    # ۲. فرآیند ثبت محصول
                    elif chat_id in user_steps:
                        step = user_steps[chat_id]["step"]
                        if step == "name":
                            user_steps[chat_id].update({"name": text, "step": "brand"})
                            send_msg(chat_id, "🏳️ نام برند:")
                        elif step == "brand":
                            user_steps[chat_id].update({"brand": text, "step": "price"})
                            send_msg(chat_id, "💰 قیمت:")
                        elif step == "price":
                            user_steps[chat_id].update({"price": text, "step": "year"})
                            send_msg(chat_id, "📅 سال تولید:")
                        elif step == "year":
                            d = user_steps[chat_id]
                            now = datetime.now().strftime("%Y-%m-%d %H:%M")
                            
                            conn = sqlite3.connect('warehouse_final.db')
                            cur = conn.cursor()
                            cur.execute("INSERT INTO products (name,brand,price,year,user_id,user_name,reg_date) VALUES (?,?,?,?,?,?,?)",
                                        (d['name'], d['brand'], d['price'], text, chat_id, u_info.get("first_name"), now))
                            conn.commit(); conn.close()
                            
                            send_msg(chat_id, "✅ محصول با موفقیت ثبت شد.")
                            del user_steps[chat_id]

    except Exception as e:
        print(f"❌ خطا: {e}")
        time.sleep(2)
