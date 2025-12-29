import requests
import time
import os

# ================= تنظیمات =================
# توکن خودت رو دقیقاً بین دو کوتیشن قرار بده
TOKEN = "YOUR_TOKEN_HERE" 
URL = "https://api.example.com" # آدرس اصلی رو اینجا بنویس
# ==========================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("-----------------------------------------")
    print("   برنامه در حال اجراست (نسخه اصلاح شده)   ")
    print("-----------------------------------------")

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    while True:
        try:
            # ارسال درخواست به سرور
            response = requests.get(URL, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ اتصال موفق در ساعت: {time.strftime('%H:%M:%S')}")
                # اینجا اگه قراره دیتای خاصی چاپ بشه اضافه کن:
                # print(response.json()) 
            
            elif response.status_code == 404:
                print(f"❌ خطا 404: آدرس پیدا نشد. یا توکن اشتباهه یا آدرس URL.")
            
            elif response.status_code == 401:
                print(f"❌ خطا 401: توکن منقضی شده یا دسترسی ندارید.")
            
            else:
                print(f"⚠️ خطای کد {response.status_code}: سرور پاسخگو نیست.")

            # وقفه برای جلوگیری از بلاک شدن (بدون حروف اضافی فارسی)
            time.sleep(2)

        except requests.exceptions.ConnectionError:
            print("🌐 خطا: اینترنت قطع است یا سرور در دسترس نیست.")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n🛑 برنامه توسط کاربر متوقف شد. خروج...")
            break
            
        except Exception as e:
            print(f"⚠️ خطای غیرمنتظره: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
