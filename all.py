import requests
import time
import sqlite3
from datetime import datetime

# -------------------- تنظیمات اختصاصی علیرضا --------------------
TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"
ADMIN_ID = 1410727630 
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
    url = f"{BASE_URL}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    try: requests.post(url, json=payload, timeout=10)
    except: pass

init_db()
user_steps = {}
last_update_id = None

print("---------------------------------------")
print("✅ سیستم انبارداری آپدیت شد.")
print("🚀 ربات علیرضا آنلاین است...")
print("---------------------------------------")

while True:
    try:
        response = requests.get(f"{BASE_URL}/getUpdates", params={'offset': last_update_id, 'timeout': 10})
        if response.status_code == 200:
            updates = response.json()
            if updates.get("ok"):
                for update in updates.get("result", []):
                    last_update_id = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = str(update["message"]["text"]).strip()
                        u_name = update["message"]["from"].get("first_name", "کاربر")

                        if text == ADMIN_PASSWORD:
                            send_msg(chat_id, "🔓 وارد پنل مدیریت شدید.")
                            continue

                        if text == "/start" or text == "سلام":
                            markup = {
                                "inline_keyboard": [
                                    [{"text": "➕ ثبت کالا", "callback_data": "add"}],
                                    [{"text": "📦 موجودی انبار", "callback_data": "inventory"}]
                                ]
                            }
                            send_msg(chat_id, f"سلام {u_name}!\nیکی از گزینه‌ها را انتخاب کنید:", reply_markup=markup)
                            continue

                        # فرآیند ثبت محصول
                        if chat_id in user_steps:
                            step = user_steps[chat_id]["step"]
                            if step == "name":
                                user_steps[chat_id].update({"name": text, "step": "brand"})
                                send_msg(chat_id, "🏳️ نام برند؟")
                            elif step == "brand":
                                user_steps[chat_id].update({"brand": text, "step": "price"})
                                send_msg(chat_id, "💰 قیمت؟")
                            elif step == "price":
                                user_steps[chat_id].update({"price": text, "step": "year"})
                                send_msg(chat_id, "📅 سال تولید؟")
                            elif step == "year":
                                d = user_steps[chat_id]
                                now_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                                conn = sqlite3.connect('warehouse_final.db')
                                conn.execute("INSERT INTO products (name,brand,price,year,user_id,user_name,reg_date) VALUES (?,?,?,?,?,?,?)",
                                             (d['name'], d['brand'], d['price'], text, chat_id, u_name, now_date))
                                conn.commit(); conn.close()
                                send_msg(chat_id, "✅ محصول با موفقیت ثبت شد.")
                                del user_steps[chat_id]

                    elif "callback_query" in update:
                        chat_id = update["callback_query"]["message"]["chat"]["id"]
                        data = update["callback_query"]["data"]
                        
                        if data == "add":
                            user_steps[chat_id] = {"step": "name"}
                            send_msg(chat_id, "🛒 نام کالا؟")
                            
                        elif data == "inventory":
                            conn = sqlite3.connect('warehouse_final.db')
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM products")
                            rows = cursor.fetchall()
                            conn.close()
                            
                            if not rows:
                                send_msg(chat_id, "📭 انبار خالی است!")
                            else:
                                report = "📦 **لیست موجودی انبار:**\n\n"
                                for row in rows:
                                    report += (f"🔹 **کالا:** {row[1]}\n"
                                               f"🏳️ **برند:** {row[2]}\n"
                                               f"💰 **قیمت:** {row[3]}\n"
                                               f"📅 **سال:** {row[4]}\n"
                                               f"👤 **ثبت‌کننده:** {row[6]}\n"
                                               f"🕒 **تاریخ:** {row[7]}\n"
                                               f"------------------\n")
                                
                                # ارسال برای کاربر
                                send_msg(chat_id, report)
                                # ارسال به پی‌وی ادمین (علیرضا)
                                if chat_id != ADMIN_ID:
                                    send_msg(ADMIN_ID, f"📢 گزارش موجودی توسط {u_name} درخواست شد:\n\n" + report)
        time.sleep(1)
    except Exception as e:
        print(f"خطا: {e}")
        time.sleep(2)
