import requests
import time
import sqlite3
from datetime import datetime

# -------------------- تنظیمات جدید علیرضا --------------------
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
    payload = {'chat_id': chat_id, 'text': text}
    if reply_markup:
        payload['reply_markup'] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

init_db()
user_steps = {}
last_update_id = None

print("---------------------------------------")
print("✅ دیتابیس آماده شد.")
print("🚀 ربات @Next_Gen_bot در حال روشن شدن...")

# تست اتصال اولیه
try:
    test_res = requests.get(f"{BASE_URL}/getMe", timeout=10)
    if test_res.status_code == 200:
        bot_name = test_res.json()['result']['first_name']
        print(f"✨ اتصال برقرار شد! ربات '{bot_name}' فعال است.")
    else:
        print(f"❌ خطا! کد وضعیت: {test_res.status_code}")
except Exception as e:
    print(f"❌ خطای اتصال به سرور بله: {e}")

print("📡 در حال دریافت پیام‌ها...")
print("---------------------------------------")

while True:
    try:
        get_url = f"{BASE_URL}/getUpdates"
        params = {'offset': last_update_id, 'timeout': 15}
        response = requests.get(get_url, params=params, timeout=20)
        
        if response.status_code == 200:
            updates = response.json()
            if updates.get("ok"):
                for update in updates.get("result", []):
                    last_update_id = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = str(update["message"]["text"]).strip()
                        u_info = update["message"]["from"]
                        u_name = u_info.get("first_name", "کاربر")
                        
                        print(f"📩 پیام از {u_name}: {text}")

                        # پنل مدیریت با رمز 1109
                        if text == ADMIN_PASSWORD:
                            conn = sqlite3.connect('warehouse_final.db')
                            count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
                            conn.close()
                            send_msg(chat_id, f"📊 گزارش انبارداری\n\n📦 تعداد کل کالاهای ثبت شده: {count}\n👤 مدیر گرامی: {u_name}")
                            continue

                        # دستور شروع
                        if text == "/start":
                            markup = {
                                "inline_keyboard": [[{"text": "➕ ثبت محصول جدید", "callback_data": "add_item"}]]
                            }
                            send_msg(chat_id, f"سلام {u_name} عزیز!\nبه بازوی مدیریت انبار خوش آمدید.\nبرای ثبت کالا از دکمه زیر استفاده کنید:", reply_markup=markup)
                            continue

                        # فرآیند ثبت محصول
                        if chat_id in user_steps:
                            step = user_steps[chat_id]["step"]
                            if step == "name":
                                user_steps[chat_id].update({"name": text, "step": "brand"})
                                send_msg(chat_id, "🏳️ نام برند کالا را وارد کنید:")
                            elif step == "brand":
                                user_steps[chat_id].update({"brand": text, "step": "price"})
                                send_msg(chat_id, "💰 قیمت کالا را وارد کنید:")
                            elif step == "price":
                                user_steps[chat_id].update({"price": text, "step": "year"})
                                send_msg(chat_id, "📅 سال تولید یا مدل کالا:")
                            elif step == "year":
                                d = user_steps[chat_id]
                                now_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                                
                                # ذخیره در دیتابیس
                                conn = sqlite3.connect('warehouse_final.db')
                                cur = conn.cursor()
                                cur.execute("INSERT INTO products (name, brand, price, year, user_id, user_name, reg_date) VALUES (?,?,?,?,?,?,?)",
                                             (d['name'], d['brand'], d['price'], text, chat_id, u_name, now_date))
                                db_id = cur.lastrowid
                                conn.commit()
                                conn.close()
                                
                                send_msg(chat_id, f"✅ محصول با موفقیت ثبت شد.\n🆔 کد رهگیری: {db_id}")
                                
                                # ارسال گزارش مستقیم برای شما (ادمین)
                                report = (f"🔔 **گزارش ثبت کالای جدید**\n\n"
                                          f"📦 کالا: {d['name']}\n"
                                          f"🏳️ برند: {d['brand']}\n"
                                          f"💰 قیمت: {d['price']}\n"
                                          f"👤 ثبت‌کننده: {u_name}\n"
                                          f"📅 تاریخ: {now_date}")
                                send_msg(ADMIN_ID, report)
                                
                                del user_steps[chat_id]

                    elif "callback_query" in update:
                        chat_id = update["callback_query"]["message"]["chat"]["id"]
                        data = update["callback_query"]["data"]
                        if data == "add_item":
                            user_steps[chat_id] = {"step": "name"}
                            send_msg(chat_id, "🛒 نام کالا را وارد کنید:")

        else:
            print(f"⚠️ خطای سرور: {response.status_code}")
            time.sleep(5)

    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        time.sleep(2)
