import json
import os
import platform
from pathlib import Path
from tkinter import messagebox


class DataManager:
    def __init__(self):
        # =============================
        # 📂 تحديد المجلد الآمن للبيانات
        # =============================
        app_name = "EuroTools"

        if platform.system() == "Windows":
            base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / app_name / "data"
        else:
            base_dir = Path.home() / ".local" / "share" / app_name / "data"

        base_dir.mkdir(parents=True, exist_ok=True)
        self.safe_data_dir = base_dir

        self.DATABASE_FILE = str(base_dir / "tools_data.json")
        self.LISTS_FILE = str(base_dir / "lists_data.json")
        self.SYNC_FILE = str(base_dir / "my-tools-sync.json")
        self.ITEMS_FORM = str(base_dir / "items_data.json")
        self.SETTING = str(base_dir / "app_settings.json")
        #self.CREDENTIALS_FILE = str(base_dir / "credentials.json")


        # ✅ تأكد من وجود الملفات أو أنشئها
        self.ensure_data_files_exist()
        # # from sync.sync_items_form import SyncManager_form

        # # self.sync_manager = SyncManager_form(creds_path=self.SYNC_FILE)

    # =============================
    # 🧩 إنشاء الملفات إن لم تكن موجودة
    # =============================
    def ensure_data_files_exist(self):
        """يتأكد من وجود ملفات JSON المطلوبة ويُنشئها عند الحاجة"""

        init_flag = self.safe_data_dir / ".euro"

        # 🔹 أول تشغيل: احذف كل الملفات القديمة ثم أنشئها من الصفر
        if not init_flag.exists():
            try:
                for file in os.listdir(self.safe_data_dir):
                    file_path = os.path.join(self.safe_data_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print("🧹 تم حذف جميع ملفات البيانات القديمة (تهيئة أولى).")
            except Exception as e:
                print(f"⚠️ فشل حذف بعض الملفات القديمة: {e}")

                

        if not os.path.exists(self.DATABASE_FILE):
            with open(self.DATABASE_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        if not os.path.exists(self.LISTS_FILE):
            with open(self.LISTS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        if not os.path.exists(self.ITEMS_FORM):
            with open(self.ITEMS_FORM, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        if not os.path.exists(self.SETTING):
            with open(self.SETTING, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        # 🔹 ملف المزامنة
        if not os.path.exists(self.SYNC_FILE):
            data = {
            "type": "",
            "project_id": "",
            "private_key_id": "",
            "private_key": "",
            "client_email": "",
            "client_id": "",
            "auth_uri": "",
            "token_uri": "",
            "auth_provider_x509_cert_url": "",
            "client_x509_cert_url": "",
            "universe_domain": ""
            }
            with open(self.SYNC_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        if not init_flag.exists():
            with open(init_flag, "w", encoding="utf-8") as flag_file:
                flag_file.write("euro")
            #print("✅ تم إنشاء ملف التهيئة (.initialized)")


    # =============================
    # 🧠 دوال التعامل مع الملفات
    # =============================

    def load_data(self, file_name):
        """تحميل البيانات من ملف JSON بشكل آمن مع إصلاح الملفات الفارغة أو التالفة"""
        try:
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                    # 🔹 الملف موجود لكن فاضي → نعيد إنشاؤه
                    if not content:
                        default_value = [] if "tools" in file_name else {}
                        self.save_data(file_name, default_value)
                        return default_value

                    # 🔹 نحاول تحميل JSON عادي
                    return json.loads(content)

            # 🔹 الملف مش موجود أساسًا
            default_value = [] if "tools" in file_name else {}
            self.save_data(file_name, default_value)
            return default_value

        except (FileNotFoundError, json.JSONDecodeError) as e:
            default_value = [] if "tools" in file_name else {}
            self.save_data(file_name, default_value)
            return default_value


    def save_data(self, file_name, data):
        """حفظ البيانات إلى ملف JSON داخل المجلد الآمن"""
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            return True
        except Exception as e:
            messagebox.showerror("Error", f"⚠️ Failed to save data to {file_name}:\n{str(e)}")
            return False
        

    # =============================
    # 📦 دوال خاصة بالأدوات والقوائم
    # =============================

    def load_tools(self):
        return self.load_data(self.DATABASE_FILE)

    def save_tools(self, data):
        return self.save_data(self.DATABASE_FILE, data)

    def load_lists(self):
        return self.load_data(self.LISTS_FILE)

    def save_lists(self, data):
        return self.save_data(self.LISTS_FILE, data)
    
    # def load_data_from_google(self, local_path):
    #     self.sync_thread = threading.Thread(target=self.sync_manager.download_from_google, args=(local_path,))
    #     self.sync_thread.start()