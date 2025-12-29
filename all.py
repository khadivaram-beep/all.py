import requests
import time
import sqlite3

# ۱. پیکربندی بازو
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

# ۲. ایجاد دیتابیس مرکزی انبار
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    # ایجاد جدول کالاها: نام کالا، تعداد، و قیمت
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT UNIQUE, 
                       quantity INTEGER, 
                       price TEXT)''')
    conn.commit()
    conn.close()

init_db()

def send_msg(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={'chat_id': chat_id, 'text': text})

def get_updates(offset=None):
    try:
        response = requests.get(f"{BASE_URL}/getUpdates", params={'offset': offset, 'timeout': 20})
        return response.json()
    except: return None

print("📦 سامانه انبارداری Next-Gen در بله فعال شد...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                msg = update["message"]["text"]

                # الف) راهنمای سیستم
                if msg == "/start" or msg == "سلام":
                    guide = (
                        "🏪 **به سامانه مدیریت کالا خوش آمدید**\n\n"
                        "🔹 **ثبت/ویرایش کالا:**\n`ثبت [نام] [تعداد] [قیمت]`\n"
                        "مثال: `ثبت لپتاپ 5 45میلیون`\n\n"
                        "🔹 **استعلام موجودی:**\n`موجودی [نام کالا]`\n"
                        "مثال: `موجودی لپتاپ`\n\n"
                        "🔹 **لیست کل انبار:**\nبنویسید: `لیست`"
                    )
                    send_msg(chat_id, guide)

                # ب) ثبت کالا در دیتابیس (نبوغ در ذخیره‌سازی)
                elif msg.startswith("ثبت"):
                    try:
                        parts = msg.split()
                        name = parts[1]
                        qty = int(parts[2])
                        price = parts[3]
                        
                        conn = sqlite3.connect('inventory.db')
                        cursor = conn.cursor()
                        # استفاده از INSERT OR REPLACE برای آپدیت خودکار کالاها
                        cursor.execute("INSERT OR REPLACE INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                                       (name, qty, price))
                        conn.commit()
                        conn.close()
                        send_msg(chat_id, f"✅ کالا با موفقیت ثبت/بروزرسانی شد:\n📦 نام: {name}\n🔢 تعداد: {qty}\n💰 قیمت: {price}")
                    except:
                        send_msg(chat_id, "❌ فرمت اشتباه! مثال:\nثبت موبایل 10 20میلیون")

                # ج) استعلام از دیتابیس (بخش اصلی قدرت ربات)
                elif msg.startswith("موجودی"):
                    target = msg.replace("موجودی", "").strip()
                    conn = sqlite3.connect('inventory.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT quantity, price FROM products WHERE name = ?", (target,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        status = "🟢 موجود" if result[0] > 0 else "🔴 ناموجود"
                        send_msg(chat_id, f"🔍 نتیجه استعلام {target}:\n\nوضعیت: {status}\nتعداد: {result[0]}\nقیمت: {result[1]}")
                    else:
                        send_msg(chat_id, f"❓ کالای «{target}» در دیتابیس انبار پیدا نشد.")

                # د) مشاهده کل انبار
                elif msg == "لیست":
                    conn = sqlite3.connect('inventory.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, quantity FROM products")
                    all_items = cursor.fetchall()
                    conn.close()
                    
                    if all_items:
                        report = "📋 لیست کل موجودی انبار:\n\n"
                        for item in all_items:
                            report += f"🔸 {item[0]}: {item[1]} عدد\n"
                        send_msg(chat_id, report)
                    else:
                        send_msg(chat_id, "📦 انبار در حال حاضر خالی است.")

    time.sleep(0.5)
