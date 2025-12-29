import requests
import time
import sqlite3
from datetime import datetime

# ۱. تنظیمات اتصال
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

# ۲. ایجاد دیتابیس
def init_db():
    conn = sqlite3.connect('warehouse_vip.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, brand TEXT, price TEXT, year TEXT, 
                       user_id INTEGER, reg_date TEXT)''')
    conn.commit()
    conn.close()

init_db()
user_steps = {}

def send_msg(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    try:
        r = requests.post(f"{BASE_URL}/sendMessage", json=data)
        return r.json()
    except Exception as e:
        print(f"❌ خطا در ارسال: {e}")

def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول جدید", "callback_data": "add"}],
            [{"text": "📈 مشاهده آمار کل انبار", "callback_data": "stats"}]
        ]
    }

def get_updates(offset=None):
    try:
        return requests.get(f"{BASE_URL}/getUpdates", params={'offset': offset, 'timeout': 20}).json()
    except: return None

print("🛰 سامانه عیب‌یاب فعال شد. پیام بده علیرضا...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            
            # مدیریت دکمه‌ها
            if "callback_query" in update:
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]
                
                if data == "add":
                    user_steps[chat_id] = {"step": "name"}
                    send_msg(chat_id, "🛒 نام کالا را ارسال کنید:")
                
                elif data == "stats":
                    conn = sqlite3.connect('warehouse_vip.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM inventory")
                    count = cursor.fetchone()[0]
                    conn.close()
                    send_msg(chat_id, f"📊 تعداد کل کالاهای ثبت شده: {count}", reply_markup=main_menu())

            # مدیریت پیام‌های متنی
            elif "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                
                # این خط خیلی مهمه؛ آیدی عددی تو رو توی ترمینال چاپ می‌کنه
                print(f"✅ پیام از آیدی [{chat_id}] رسید: {text}")

                if text in ["/start", "سلام"]:
                    send_msg(chat_id, "سلام! سیستم آماده است. روی دکمه زیر بزن:", reply_markup=main_menu())
                
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
                        name = user_steps[chat_id]['name']
                        brand = user_steps[chat_id]['brand']
                        price = user_steps[chat_id]['price']
                        reg_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # ذخیره در دیتابیس
                        conn = sqlite3.connect('warehouse_vip.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO inventory (name, brand, price, year, user_id, reg_date) VALUES (?, ?, ?, ?, ?, ?)", 
                                       (name, brand, price, text, chat_id, reg_date))
                        conn.commit(); conn.close()
                        
                        send_msg(chat_id, f"✅ ثبت شد!\n📦 {name}\n📅 {reg_date}", reply_markup=main_menu())
                        
                        # گزارش به خودت (فعلاً به همین chat_id می‌فرستیم تا مطمئن بشیم کار می‌کنه)
                        report = f"🚀 گزارش مدیر:\nکالا: {name}\nثبت کننده: {chat_id}"
                        send_msg(chat_id, report) 
                        
                        del user_steps[chat_id]

    time.sleep(0.5)
