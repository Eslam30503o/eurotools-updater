import os
import json
import time
import threading
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import requests
import customtkinter as ctk


class SyncManager_form:
    def __init__(self, creds_path, sheet_name="My Tools Sync", filter_callback=None , ui_root=None ):
        self.creds_path = creds_path
        self.sheet_name = sheet_name
        self.filter_callback = filter_callback  # <-- هنا نحتفظ بالدالة
        self.ui_root = ui_root
        self.sheet = None

        # 🔹 مجلد التخزين المحلي
        base_dir = os.path.join(os.getenv("LOCALAPPDATA") or os.path.expanduser("~/.local/share"), "EuroTools", "data")
        os.makedirs(base_dir, exist_ok=True)
        self.local_cache_path = os.path.join(base_dir, "sync_cache.json")
        self.local_data_path = os.path.join(base_dir, "items_data.json")  # ✅ السطر المهم المفقود

        # اتصال أولي بـ Google Sheets
        self._connect_to_sheet()

        threading.Thread(
            target=self._download_data_in_background,
            daemon=True
        ).start()

        # تشغيل مزامنة تلقائية في الخلفية
        #self._start_auto_sync_thread()


    # ===============================
    # 🌐 فحص الاتصال بالإنترنت
    # ===============================
    def check_internet(self):
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

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
            self.sheet = client.open(self.sheet_name).worksheet("Items_form")
            #print("✅ تم الاتصال بـ Google Sheets.")
        except Exception as e:
            print(f"⚠️ فشل الاتصال بـ Google Sheets: {e}")
            self.sheet = None


    def _download_data_in_background(self):
        from ui.items_form import DynamicFormApp
        if self.check_internet():
            success = self.download_from_google(self.local_data_path)
            if success:
                if self.filter_callback:
                    self.ui_root.after(0, self.filter_callback)
            else:
                print("⚠️ فشل تحميل البيانات من Google Sheets.")
        else:
            print("📴 لا يوجد إنترنت - سيتم استخدام النسخة المحلية إن وجدت.")


    def delete_item_from_google(self, item_name):
        """🗑️ حذف منتج بالكامل من Google Sheets"""
        try:
            if not self.sheet:
                self._connect_to_sheet()
            if not self.sheet:
                print("⚠️ لا يمكن الاتصال بـ Google Sheets لحذف المنتج.")
                return False

            records = self.sheet.get_all_records()
            for idx, record in enumerate(records, start=2):  # الصف الأول للعناوين
                if record.get("Item (English)") == item_name:
                    self.sheet.delete_rows(idx)
                    #print(f"🗑️ تم حذف {item_name} من Google Sheets.")
                    return True

            print(f"⚠️ لم يتم العثور على {item_name} في Google Sheets.")
            return False

        except Exception as e:
            print(f"⚠️ خطأ أثناء حذف المنتج من Google Sheets: {e}")
            return False


    def update_item_in_google(self, item_name, item_data):
        """🔁 تحديث منتج بعد تعديل أو حذف خاصية"""
        try:
            if not self.sheet:
                self._connect_to_sheet()
            if not self.sheet:
                print("⚠️ لا يمكن الاتصال بـ Google Sheets لتحديث المنتج.")
                return False

            existing_data = self.sheet.get_all_records()
            for idx, record in enumerate(existing_data, start=2):
                if record.get("Item (English)") == item_name:
                    updated_row = [
                        item_name,
                        item_data.get("arabic_name", ""),
                        json.dumps(item_data.get("properties", []), ensure_ascii=False),
                        item_data.get("code_template", ""),
                        item_data.get("code_template_2", ""),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                    self.sheet.update(f"A{idx}:F{idx}", [updated_row])
                    return True

            print(f"⚠️ لم يتم العثور على {item_name} في Google Sheets.")
            return False

        except Exception as e:
            print(f"⚠️ فشل تحديث المنتج في Google Sheets: {e}")
            return False



    # ===============================
    # 💾 حفظ محلي + رفع لحظي (أو كاش)
    # ===============================


    def save_file(self, items_data, local_path):
        """حفظ البيانات محليًا فقط"""
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(items_data, f, ensure_ascii=False, indent=2)
            #print(f"💾 تم الحفظ محليًا في: {local_path}")
            return True
        except Exception as e:
            print(f"⚠️ فشل الحفظ المحلي: {e}")
            return False

    def upload_file(self, items_data):
        """رفع البيانات إلى جوجل أو حفظها مؤقتًا"""
        data_snapshot = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": items_data
        }

        def upload_task():
            if self.check_internet():
                success = self.upload_to_google(data_snapshot)
                if not success:
                    self._save_to_cache(data_snapshot)
            else:
                print("📴 لا يوجد إنترنت - حفظ التغيير مؤقتًا.")
                self._save_to_cache(data_snapshot)

        threading.Thread(target=upload_task, daemon=True).start()


    # ===============================
    # ☁️ رفع البيانات إلى Google Sheets
    # ===============================
    def upload_to_google(self, data_snapshot):
        try:
            if not self.sheet:
                self._connect_to_sheet()
            if not self.sheet:
                return False

            existing_data = self.sheet.get_all_records()
            existing_names = {row["Item (English)"]: idx+2 for idx, row in enumerate(existing_data)}  # +2 لأن الصف الأول للعناوين

            # تجهيز التحديثات الجديدة
            batch_updates = []
            new_items = data_snapshot["items"]

            for name, data in new_items.items():
                arabic_name = data.get("arabic_name", "")
                properties = json.dumps(data.get("properties", []), ensure_ascii=False)
                code_template = data.get("code_template", "")
                code_template_2 = data.get("code_template_2", "")
                updated_at = data_snapshot["timestamp"]

                row_data = [name, arabic_name, properties, code_template,code_template_2, updated_at]

                if name in existing_names:
                    row_index = existing_names[name]
                    batch_updates.append({
                        'range': f"A{row_index}:F{row_index}",
                        'values': [row_data]
                    })
                else:
                    # العنصر جديد → أضفه لاحقًا باستخدام append
                    self.sheet.append_row(row_data)

            # إرسال جميع التحديثات دفعة واحدة
            if batch_updates:
                self.sheet.batch_update(batch_updates)

            #print("☁️✅ تم تحديث البيانات في Google Sheets باستخدام batch update.")
            return True

        except Exception as e:
            print(f"⚠️ فشل رفع البيانات إلى Google Sheets: {e}")
            return False

    def download_from_google(self, local_path):
        """
        📥 تحميل البيانات من Google Sheets وحفظها محليًا.
        """
        try:
            if not self.sheet:
                self._connect_to_sheet()
            if not self.sheet:
                print("⚠️ لا يمكن الاتصال بـ Google Sheets.")
                return False

            # جلب كل البيانات من الشيت (كقوائم)
            rows = self.sheet.get_all_values()
            if not rows or len(rows) < 2:
                print("⚠️ لا توجد بيانات في Google Sheets.")
                return False

            headers = rows[0]
            data_rows = rows[1:]
            items = {}

            # تحويل كل صف إلى عنصر
            for row in data_rows:
                try:
                    name = row[0]
                    arabic_name = row[1] if len(row) > 1 else ""
                    properties = json.loads(row[2]) if len(row) > 2 and row[2] else []
                    code_template = row[3] if len(row) > 3 else ""
                    code_template_2 = row[4] if len(row) > 4 else ""
                    updated_at = row[5] if len(row) > 5 else ""
                    items[name] = {
                        "arabic_name": arabic_name,
                        "properties": properties,
                        "code_template": code_template,
                        "code_template_2": code_template_2,
                        "updated_at": updated_at
                    }
                except Exception as e:
                    print(f"⚠️ خطأ في قراءة صف: {e}")

            # حفظ محليًا كـ JSON
            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)

            #print(f"📥✅ تم تحميل البيانات من Google Sheets وحفظها في: {local_path}")
            return True

        except Exception as e:
            print(f"⚠️ فشل تحميل البيانات من Google Sheets: {e}")
            return False

    # ===============================
    # 💾 حفظ مؤقت في كاش
    # ===============================
    def _save_to_cache(self, snapshot):
        try:
            cache = []
            if os.path.exists(self.local_cache_path):
                with open(self.local_cache_path, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            cache.append(snapshot)
            with open(self.local_cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            #print("💾 تم حفظ نسخة مؤقتة من التعديل في الكاش.")
        except Exception as e:
            print(f"⚠️ فشل أثناء الحفظ المؤقت: {e}")

    # ===============================
    # 🔁 مزامنة الكاش (عند رجوع الإنترنت)
    # ===============================
    def sync_cache(self):
        if not os.path.exists(self.local_cache_path):
            return

        try:
            with open(self.local_cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)

            if not cache:
                return

            #print(f"🔁 مزامنة {len(cache)} تعديل مؤجل...")
            for snapshot in cache:
                self.upload_to_google(snapshot)

            os.remove(self.local_cache_path)
            #print("✅ تمت مزامنة جميع البيانات المؤقتة بنجاح.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء المزامنة: {e}")
