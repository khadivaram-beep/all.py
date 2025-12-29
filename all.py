import requests
import time
import sqlite3
from datetime import datetime

# -------------------- تنظیمات --------------------
BALE_TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
ADMIN_ID = 1410727630  # آیدی شما
ADMIN_PASSWORD = "1109"
# ------------------------------------------------

def init_db():
    try:
        conn = sqlite3.connect('warehouse_final.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           name TEXT, brand TEXT, price TEXT, year TEXT, 
                           user_id INTEGER, user_name TEXT, reg_date TEXT)''')
        conn.commit()
        conn.close()
        print("✅ دیتابیس آماده است.")
    except Exception as e:
        print(f"❌ خطای دیتابیس: {e}")

def send_msg(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    try:
        r = requests.post(f"{BASE_URL}/sendMessage", json=data, timeout=10)
        return r.status_code == 200
    except:
        return False

init_db()
user_steps = {}
last_update_id = None

print("---------------------------------------")
print("🚀 ربات علیرضا استارت شد...")
print("📡 در حال گوش دادن به پیام‌ها در بله...")
print("---------------------------------------")

while True:
    try:
        # دریافت پیام‌ها
        response = requests.get(f"{BASE_URL}/getUpdates", params={'offset': last_update_id, 'timeout': 15}, timeout=20)
        
        if response.status_code != 200:
            print(f"⚠️ اخطار: اتصال به بله برقرار نشد (کد {response.status_code})")
            time.sleep(5)
            continue
            
        updates = response.json()
        
        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
                
                # بررسی پیام‌های متنی
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = str(update["message"]["text"]).strip()
                    u_name = update["message"]["from"].get("first_name", "کاربر")
                    
                    print(f"📩 پیام جدید از {u_name}: {text}")

                    # پنل مدیریت با رمز
                    if text == ADMIN_PASSWORD:
                        conn = sqlite3.connect('warehouse_final.db')
                        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
                        conn.close()
                        send_msg(chat_id, f"📊 آمار کل انبار: {count} کالا")
                        continue

                    # شروع
                    if text in ["/start", "سلام"]:
                        markup = {"inline_keyboard": [[{"text": "➕ ثبت محصول جدید", "callback_data": "add"}]]}
                        send_msg(chat_id, "سلام! برای ثبت کالا روی دکمه زیر بزنید:", reply_markup=markup)
                        continue

                    # مراحل ثبت کالا
                    if chat_id in user_steps:
                        step = user_steps[chat_id]["step"]
                        if step == "name":
                            user_steps[chat_id].update({"name": text, "step": "brand"})
                            send_msg(chat_id, "🏳️ نام برند را وارد کنید:")
                        elif step == "brand":
                            user_steps[chat_id].update({"brand": text, "step": "price"})
                            send_msg(chat_id, "💰 قیمت را وارد کنید:")
                        elif step == "price":
                            user_steps[chat_id].update({"price": text, "step": "year"})
                            send_msg(chat_id, "📅 سال تولید را وارد کنید:")
                        elif step == "year":
                            d = user_steps[chat_id]
                            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                            
                            conn = sqlite3.connect('warehouse_final.db')
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO products (name, brand, price, year, user_id, user_name, reg_date) VALUES (?,?,?,?,?,?,?)",
                                           (d['name'], d['brand'], d['price'], text, chat_id, u_name, dt))
                            db_id = cursor.lastrowid
                            conn.commit()
                            conn.close()
                            
                            send_msg(chat_id, "✅ محصول با موفقیت در انبار ثبت شد.")
                            
                            # گزارش به مدیر
                            report = f"🚀 کالا ثبت شد!\n📦 نام: {d['name']}\n🏳️ برند: {d['brand']}\n👤 توسط: {u_name}\n🆔 کد: {db_id}"
                            send_msg(ADMIN_ID, report)
                            del user_steps[chat_id]

                # بررسی دکمه‌های شیشه‌ای
                elif "callback_query" in update:
                    chat_id = update["callback_query"]["message"]["chat"]["id"]
                    data = update["callback_query"]["data"]
                    if data == "add":
                        user_steps[chat_id] = {"step": "name"}
                        send_msg(chat_id, "🛒 نام کالا چیست؟")

    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        time.sleep(3)
