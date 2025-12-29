import requests
import time

# ۱. اطلاعات بازو
BALE_TOKEN = "802549012:2SglERgmkafn0HTTh7w8fT304wREI_LUCFs"
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {'offset': offset, 'timeout': 30}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except:
        return None

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=data)

print("🛰 در حال پایش پیام‌ها در بله...")

last_update_id = None
while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                user_text = update["message"]["text"]
                print(f"📥 پیام رسید: {user_text}")

                if user_text == "سلام":
                    send_message(chat_id, "علیک! علیرضا جان، الان دیگه صداتو شنیدم. نقل مکان به بله نهایی شد! ✅")
                else:
                    send_message(chat_id, "پیام دریافت شد، منتظر دستور بعدی هستم.")
    
    time.sleep(1) # برای جلوگیری از فشار به سرور
