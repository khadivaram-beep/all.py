import requests
import time
import sqlite3

# ۱. تنظیمات اتصال به بله
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

# ۲. ایجاد دیتابیس پیشرفته
def init_db():
    conn = sqlite3.connect('warehouse.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, brand TEXT, price TEXT, year TEXT)''')
    conn.commit()
    conn.close()

init_db()

# حافظه موقت برای مراحل ثبت کالا
user_steps = {}

def send_msg(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup:
        data['reply_markup'] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=data)

# ساخت دکمه‌های اصلی
def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ ثبت محصول جدید", "callback_data": "add_product"}],
            [{"text": "📋 استعلام کل موجودی", "callback_data": "view_all"}]
        ]
    }

def get_updates(offset=None):
    try:
        response = requests.get(f"{BASE_URL}/getUpdates", params={'offset': offset, 'timeout': 20})
        return response.json()
    except: return None

print("🚀 سامانه انبارداری با منوی شیشه‌ای فعال شد...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            
            # مدیریت کلیک روی دکمه‌ها
            if "callback_query" in update:
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]
                
                if data == "add_product":
                    user_steps[chat_id] = {"step": "name"}
                    send_msg(chat_id, "🛒 لطفاً **نام کالا** را ارسال کنید:")
                
                elif data == "view_all":
                    conn = sqlite3.connect('warehouse.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, brand, price, year FROM inventory")
                    rows = cursor.fetchall()
                    conn.close()
                    
                    if rows:
                        res = "📋 **لیست کامل موجودی انبار:**\n\n"
                        for row in rows:
                            res += f"📦 کالا: {row[0]}\n🏳️ برند: {row[1]}\n💰 قیمت: {row[2]}\n📅 سال: {row[3]}\n\n"
                        send_msg(chat_id, res, reply_markup=main_menu())
                    else:
                        send_msg(chat_id, "❌ انبار خالی است!", reply_markup=main_menu())

            # مدیریت پیام‌های متنی (مراحل ثبت)
            elif "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]

                if text == "/start" or text == "سلام":
                    send_msg(chat_id, "سلام علیرضا! به پنل مدیریت انبار خوش آمدی. یکی از گزینه‌ها را انتخاب کن:", reply_markup=main_menu())
                
                elif chat_id in user_steps:
                    step = user_steps[chat_id]["step"]
                    
                    if step == "name":
                        user_steps[chat_id]["name"] = text
                        user_steps[chat_id]["step"] = "brand"
                        send_msg(chat_id, "🏳️ حالا **نام برند** را بفرست:")
                    
                    elif step == "brand":
                        user_steps[chat_id]["brand"] = text
                        user_steps[chat_id]["step"] = "price"
                        send_msg(chat_id, "💰 **قیمت** را وارد کن:")
                    
                    elif step == "price":
                        user_steps[chat_id]["price"] = text
                        user_steps[chat_id]["step"] = "year"
                        send_msg(chat_id, "📅 **سال تولید** را بفرست:")
                    
                    elif step == "year":
                        name = user_steps[chat_id]["name"]
                        brand = user_steps[chat_id]["brand"]
                        price = user_steps[chat_id]["price"]
                        year = text
                        
                        # ذخیره نهایی در دیتابیس
                        conn = sqlite3.connect('warehouse.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO inventory (name, brand, price, year) VALUES (?, ?, ?, ?)", 
                                       (name, brand, price, year))
                        conn.commit()
                        conn.close()
                        
                        del user_steps[chat_id] # پاک کردن حافظه موقت
                        send_msg(chat_id, f"✅ محصول با موفقیت در دیتابیس ثبت شد!\n📦 {name} - {brand}", reply_markup=main_menu())

    time.sleep(0.5)
