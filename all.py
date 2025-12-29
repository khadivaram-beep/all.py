import requests
import time

# تنظیمات اصلی
TOKEN = "8396499160:AAGbLexQ8M4KAc8DTubq5art5ImFSHeFQn0"
BASE_URL = "https://tapi.bale.ai/bot" + TOKEN  # ترکیب دستی برای امنیت بیشتر

def test_connection():
    try:
        r = requests.get(f"{BASE_URL}/getMe", timeout=10)
        if r.status_code == 200:
            print(f"✅ اتصال برقرار شد! نام ربات: {r.json()['result']['first_name']}")
            return True
        else:
            print(f"❌ خطا! کد {r.status_code}. احتمالا توکن اشتباه است.")
            return False
    except:
        print("❌ سرور بله در دسترس نیست.")
        return False

if test_connection():
    last_id = None
    print("🛰️ ربات علیرضا در حال پایش پیام‌ها...")
    while True:
        try:
            res = requests.get(f"{BASE_URL}/getUpdates", params={'offset': last_id, 'timeout': 5})
            if res.status_code == 200:
                updates = res.json().get("result", [])
                for update in updates:
                    last_id = update["update_id"] + 1
                    if "message" in update:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"].get("text", "")
                        print(f"📩 پیام رسید از {chat_id}: {text}")
                        
                        # پاسخ ساده برای تست
                        requests.post(f"{BASE_URL}/sendMessage", json={'chat_id': chat_id, 'text': "کد سالمه علیرضا! پیام رسید."})
            time.sleep(1)
        except:
            pass
