import os
import json
import time
import requests
import threading
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from data_manager import DataManager


class HistoryManager:
        
    logged_in_user: str = None

    def __init__(self, creds_path=None, sheet_name="My Tools Sync"):
        # 🔹 تهيئة DataManager للحصول على المسار الآمن
        self.dm = DataManager()
        self.local_cache_path = os.path.join(self.dm.safe_data_dir, "history_cache.json")

        self.creds_path = creds_path or self.dm.SYNC_FILE
        self.sheet_name = sheet_name
        self.sheet = None

        # تشغيل الاتصال في خيط منفصل لتجنب تأخير الواجهة
        threading.Thread(target=self._connect_to_sheet, daemon=True).start()

        # بدء المزامنة التلقائية بعد التشغيل
        self._start_auto_sync_thread()


    # ===============================
    # 🔹 الاتصال بـ Google Sheets
    # ===============================
    def _connect_to_sheet(self):
        try:
            creds = Credentials.from_service_account_file(
                self.creds_path,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
            client = gspread.authorize(creds)
            self.sheet = client.open(self.sheet_name).worksheet("History")
            #print("✅ تم الاتصال بنجاح بـ Google Sheets.")
        except Exception as e:
            print(f"⚠️ فشل الاتصال بـ Google Sheets: {e}")
            self.sheet = None

    # ===============================
    # 🌐 فحص الاتصال بالإنترنت
    # ===============================
    def check_internet(self, timeout=3):
        try:
            requests.get("https://www.google.com", timeout=timeout)
            return True
        except:
            return False

    # ===============================
    # 📝 تسجيل عملية جديدة
    # ===============================
    def log_action(self, user, action, item, details="", status="✅ Success"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [user, action, item, details, status, timestamp]

        if self.check_internet() and self.sheet:
            try:
                self.sheet.append_row(row)
                #print(f"[History Logged ✅] {row}")
            except Exception as e:
                print(f"⚠️ فشل الإرسال أونلاين، جاري الحفظ محليًا: {e}")
                self._save_locally(row)
        else:
            print("📴 لا يوجد اتصال بالإنترنت، تم الحفظ محليًا.")
            self._save_locally(row)

    # ===============================
    # 💾 حفظ السجل محليًا
    # ===============================
    def _save_locally(self, row):
        try:
            cache = []
            if os.path.exists(self.local_cache_path):
                with open(self.local_cache_path, "r", encoding="utf-8") as f:
                    cache = json.load(f)

            cache.append(row)

            with open(self.local_cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)

            print(f"💾 تم حفظ العملية مؤقتًا في {self.local_cache_path}")
        except Exception as e:
            print(f"⚠️ خطأ أثناء الحفظ المحلي: {e}")

    # ===============================
    # 🔁 مزامنة السجلات المحلية
    # ===============================
    def sync_local_cache(self):
        if not os.path.exists(self.local_cache_path):
            return

        try:
            with open(self.local_cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)

            if not cache:
                return

            print(f"🔁 جاري رفع {len(cache)} سجل محفوظ...")
            for row in cache:
                try:
                    if not self.sheet:
                        self._connect_to_sheet()
                    if self.sheet:
                        self.sheet.append_row(row)
                except Exception as e:
                    print(f"⚠️ فشل إرسال سجل واحد: {e}")
                    return

            os.remove(self.local_cache_path)
            print("✅ تمت مزامنة جميع السجلات المحلية بنجاح!")
        except Exception as e:
            print(f"⚠️ فشل أثناء المزامنة: {e}")

    # ===============================
    # 🔄 تشغيل حلقة المزامنة التلقائية
    # ===============================
    def _start_auto_sync_thread(self):
        def auto_sync_loop():
            while True:
                if self.check_internet():
                    self.sync_local_cache()
                time.sleep(10)  # يفحص كل 10 ثواني

        threading.Thread(target=auto_sync_loop, daemon=True).start()
