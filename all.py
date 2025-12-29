import requests
import time
import sqlite3
from datetime import datetime

# ۱. تنظیمات اتصال
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
# آیدی عددی خودت رو بعد از تست اول اینجا جایگزین کن
ADMIN_ID = 0 

def init_db():
    conn = sqlite3.connect('warehouse_vip.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, brand TEXT, price INTEGER, year TEXT, 
                       user_id INTEGER, reg_date TEXT)''')
    conn.commit()
    conn.close()

init_db()
user_steps = {}

def send_msg(chat_id, text, reply_markup=None):
    if chat_id == 0: return
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup: data['reply_markup'] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=data)

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

print("🚀 سامانه VIP بله با اولویت‌بندی دکمه‌ها فعال شد...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            
            # ۱. مدیریت دکمه‌ها (Callback)
            if "callback_query" in update:
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]
                
                # جلوگیری از تداخل: اگر در حال ثبت است، دکمه آمار کار نکند
                if chat_id in user_steps:
                    send_msg(chat_id, "⚠️ شما در حال ثبت یک کالا هستید. لطفاً ابتدا مراحل را تمام کنید.")
                    continue

                if data == "add":
                    user_steps[chat_id] = {"step": "name"}
                    send_msg(chat_id, "🛒 نام کالا را ارسال کنید:")
                
                elif data == "stats":
                    conn = sqlite3.connect('warehouse_vip.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*), SUM(price) FROM inventory")
                    count, total_price = cursor.fetchone()
                    conn.close()
                    send_msg(chat_id, f"📊 **گزارش انبار:**\n\n🔹 تعداد کالا: {count}\n💰 ارزش کل: {total_price or 0}", reply_markup=main_menu())

            # ۲. مدیریت پیام‌ها (تایپ کردن)
            elif "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                
                # چاپ آیدی در ترمینال برای شناسایی مدیر
                print(f"🆔 User ID: {chat_id} | Text: {text}")

                if text in ["/start", "سلام"]:
                    send_msg(chat_id, "سلام علیرضا! سیستم آماده به کار است:", reply_markup=main_menu())
                
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
                        # استخراج اطلاعات برای دیتابیس و گزارش مدیر
                        name = user_steps[chat_id]['name']
                        brand = user_steps[chat_id]['brand']
                        price = user_steps[chat_id]['price']
                        year = text
                        reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # ذخیره در دیتابیس
                        conn = sqlite3.connect('warehouse_vip.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO inventory (name, brand, price, year, user_id, reg_date) VALUES (?, ?, ?, ?, ?, ?)", 
                                       (name, brand, int(price), year, chat_id, reg_date))
                        conn.commit(); conn.close()
                        
                        # تاییدیه به کاربر
                        send_msg(chat_id, "✅ کالا با موفقیت ثبت شد.", reply_markup=main_menu())
                        
                        # 📢 ارسال گزارش فوق محرمانه برای مدیر (@khadivaram)
                        report = (f"🚀 **ارسال برای مدیر**\n"
                                  f"--------------------------\n"
                                  f"📦 **کالای جدید:** {name}\n"
                                  f"🏳️ **برند:** {brand}\n"
                                  f"💰 **قیمت:** {price}\n"
                                  f"📅 **سال تولید:** {year}\n"
                                  f"--------------------------\n"
                                  f"👤 **آیدی ثبت‌کننده:** `{chat_id}`\n"
                                  f"⏰ **تاریخ ثبت:** {reg_date}\n"
                                  f"🔐 **نوع کالا:** خصوصی/سیستمی")
                        send_msg(ADMIN_ID, report)
                        
                        del user_steps[chat_id]

    time.sleep(0.5)
