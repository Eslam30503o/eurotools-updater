import os
import platform
import socket
import uuid
import threading
import time
from pathlib import Path
from datetime import datetime, timezone
import json
import requests

from .google_init import initialize_google
from .lock_manager import LockManager
from .sync_products import sync_products, download_products
from .sync_lists import sync_lists, download_lists
from .utils import load_json, save_json
from .history_manager import HistoryManager
from ui.history_screen import HistoryScreen

from google_sheets_uploader import GoogleSheetsUploader

class SyncManager:
    def __init__(self, ui_ref=None, auto_sync=True, sync_interval=90, retry_interval=30, app_name="EuroTools"):
        self.ui = ui_ref
        self.auto_sync = auto_sync
        self.sync_interval = sync_interval
        self.retry_interval = retry_interval

        self.connection_stats = {
        'total_attempts': 0,
        'successful_connections': 0,
        'failed_connections': 0,
        'last_success': None,
        'last_failure': None
        }
    
        self.auto_recovery_enabled = True
        self.max_retries = 10  # أقصى عدد محاولات
        self.current_retries = 0
        self.backoff_multiplier = 1.5  # تضاعف وقت الانتظار

        # safe data dir (مثل كودك الأصلي)
        if platform.system() == "Windows":
            base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / app_name / "data"
        else:
            base_dir = Path.home() / ".local" / "share" / app_name / "data"
        base_dir.mkdir(parents=True, exist_ok=True)
        self.safe_data_dir = str(base_dir)

        # ملفات محلية
        self.DATABASE_FILE = os.path.join(self.safe_data_dir, "tools_data.json")
        self.LISTS_FILE = os.path.join(self.safe_data_dir, "lists_data.json")
        self.creds_file = os.path.join(self.safe_data_dir, "my-tools-sync.json")  # ضع ملف الاعتماد هنا
        self.sheet_name = "My Tools Sync"
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        self.client = None
        self.sheet = None
        self.locks_sheet = None
        self.products_sheet = None
        self.lists_sheet = None
        self.history = HistoryManager(
            creds_path=self.creds_file,
            sheet_name=self.sheet_name
        )

        self.is_connected = False
        self.client_id = f"{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6]}"
        self.lock_manager = None

        self.stop_event = threading.Event()
        self.sync_thread = None
        self.sync_lock = threading.Lock()

        


                # ⭐️ محاولة الاتصال أولاً
        try:
            ok = self.initialize_google()
            if ok:
                #self._notify("✅ تم الاتصال بـ Google Sheets (initial).", kind="success")
                
                # ⭐️⭐️ إضافة تهيئة HistoryManager هنا بعد نجاح الاتصال وتعيين self.sheet
                try:
                    history_sheet = self.sheet.worksheet("History")
                    self.history = HistoryManager(history_sheet)
                except Exception:
                    print("⚠️ لم يتم العثور على ورقة History، سيتم التسجيل Offline فقط.")
                
            else:
                self._notify("⚠️ لا يمكن الاتصال بـ Google Sheets الآن — العمل Offline.", kind="warning")
                # ⭐️ لا يزال يجب أن يكون هناك كائن HistoryManager حتى في وضع Offline
                self.history = HistoryManager(creds_path=self.creds_file, sheet_name=self.sheet_name) 

        except Exception as e:
            print("initial connection error:", e)
            self._notify("⚠️ خطأ أثناء محاولة الاتصال الأولية.", kind="warning")
            # ⭐️ تأكد من وجوده في وضع Offline
            self.history = HistoryManager(creds_path=self.creds_file, sheet_name=self.sheet_name)

        if self.auto_sync:
            self.start_auto_sync()

    
    def check_internet_connection(self, timeout=5) -> bool:
        """فحص الاتصال بالإنترنت"""
        try:
            response = requests.get("https://www.google.com", timeout=timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def initialize_google(self) -> bool:

        self.connection_stats['total_attempts'] += 1
    
        try:
            # أضف فحص الإنترنت أولاً
            if not self.check_internet_connection():
                print("🌐 لا يوجد اتصال بالإنترنت")
                return False
            
            client, sheet, locks_sheet, products_sheet, lists_sheet = initialize_google(self.creds_file, self.sheet_name, self.scope)
            self.client = client
            self.sheet = sheet
            self.locks_sheet = locks_sheet
            self.products_sheet = products_sheet
            self.lists_sheet = lists_sheet
            self.lock_manager = LockManager(self.locks_sheet, self.client_id)
            self.is_connected = True
            self.connection_stats['successful_connections'] += 1
            self.connection_stats['last_success'] = datetime.now().isoformat()
            self.current_retries = 0  # إعادة تعيين المحاولات
            return True
        except Exception as e:
            self.is_connected = False
            self.connection_stats['failed_connections'] += 1
            self.connection_stats['last_failure'] = datetime.now().isoformat()
            self.current_retries += 1
        
            return False
    def _smart_retry_delay(self):
        """حساب وقت الانتظار مع الزيادة التدريجية"""
        base_delay = self.retry_interval
        backoff_delay = base_delay * (self.backoff_multiplier ** min(self.current_retries, 5))
        return min(backoff_delay, 300)  # لا تزيد عن 5 دقائق
    
    def _auto_recovery_loop(self):
        """حلقة التعافي التلقائي"""
        print("🚀 بدء نظام التعافي التلقائي")
        
        while not self.stop_event.is_set():
            if not self.is_connected and self.auto_recovery_enabled:
                try:
                    # فحص الاتصال أولاً
                    if self.check_internet_connection():
                        print("🌐 تم اكتشاف اتصال بالإنترنت، محاولة إعادة الاتصال...")
                        
                        if self.initialize_google():
                            self._notify("✅ تم استعادة الاتصال تلقائياً", "success")
                            self.current_retries = 0
                        else:
                            # زيادة وقت الانتظار تدريجياً
                            wait_time = self._smart_retry_delay()
                            print(f"⏳ محاولة {self.current_retries}/{self.max_retries} - الانتظار {wait_time} ثانية")
                            
                            if self.current_retries >= self.max_retries:
                                print("🛑 تجاوز الحد الأقصى للمحاولات")
                                self.auto_recovery_enabled = False
                                self._notify("🛑 توقف التعافي التلقائي", "error")
                            
                            self.stop_event.wait(wait_time)
                    else:
                        # لا يوجد اتصال، انتظر فترة أطول
                        self.stop_event.wait(self.retry_interval * 2)
                        
                except Exception as e:
                    print(f"❌ خطأ في حلقة التعافي: {e}")
                    self.stop_event.wait(self.retry_interval)
            else:
                # الاتصال نشط، انتظر للفحص
                self.stop_event.wait(self.sync_interval)

    def _notify(self, message, kind="info"):
        if self.ui and hasattr(self.ui, "show_toast"):
            try:
                self.ui.show_toast(message, kind)
            except:
                pass
        else:
            print(message)

    def start_auto_sync(self):
        if self.sync_thread and self.sync_thread.is_alive():
            return

        def loop():
            first_run = True

            if self.auto_recovery_enabled:
                recovery_thread = threading.Thread(
                    target=self._auto_recovery_loop,
                    daemon=True,
                    name="AutoRecovery"
                )
                recovery_thread.start()
                print("🔄 بدء خيط التعافي التلقائي")
            
            while not self.stop_event.is_set():
                try:
                    with self.sync_lock:
                        net_status = "ok"
                        if self.ui:
                            net_status = self.ui.check_internet_connection()
                            
                        if net_status == "offline" or net_status == "weak":
                            
                            if self.initialize_google():
                                
                                if first_run:  # ✅ فقط أول مرة نعرض رسالة نجاح
                                    self._notify("✅ تم استعادة الاتصال .", "success")
                            else:
                                # فشل في إعادة الاتصال (قد يكون ضعيفاً جداً)
                                if first_run:
                                    self._notify("⚠️ المزامنة غير ممكنة: الاتصال ضعيف. سأحاول مجدداً.", "warning")
                                self.is_connected = False # تأكد من تعيين الحالة Offline
                                wait = self.retry_interval
                                first_run = False  # 🔸 بعد أول محاولة، لا نعرض رسائل مرة أخرى
                                continue
                        
                        # 3. إجراء المزامنة (يحدث فقط إذا كانت self.is_connected هي True)
                        if self.is_connected: 
                            self.sync_all() 
                            wait = self.sync_interval
                        else:
                            wait = self.retry_interval

                except Exception as e:
                    print(f"Unexpected error in auto-sync loop: {e}")
                    wait = self.retry_interval

                if self.stop_event.wait(wait):
                    break

        self.sync_thread = threading.Thread(target=loop, daemon=True, name="SyncManagerAutoSync")
        self.sync_thread.start()

    def stop_auto_sync(self, join_timeout: float = 2.0):
        self.stop_event.set()
        if self.sync_thread and self.sync_thread.is_alive():
            try:
                self.sync_thread.join(timeout=join_timeout)
            except:
                pass

    def force_reconnect(self):
        """إجبار إعادة الاتصال يدوياً"""
        print("🔄 محاولة إعادة اتصال يدوية...")
        self.is_connected = False
        self.client = None
        self.sheet = None
        self.auto_recovery_enabled = True
        self.current_retries = 0
        
        if self.initialize_google():
            self._notify("✅ تم إعادة الاتصال بنجاح", "success")
            return True
        else:
            self._notify("❌ فشل إعادة الاتصال", "error")
            return False

    def get_connection_status(self) -> dict:
        """الحصول على حالة الاتصال"""
        return {
            'connected': self.is_connected,
            'auto_recovery': self.auto_recovery_enabled,
            'stats': self.connection_stats.copy(),
            'current_retries': self.current_retries,
            'max_retries': self.max_retries,
            'internet_available': self.check_internet_connection()
    }

    def sync_all(self):
        # محاولة القفل بعيدًا أولًا
        got_remote_lock = False
        got_local_lock = False
        lock_file = os.path.join(self.safe_data_dir, "sync_lock.json")

        ok = self.is_connected  # ✅ أضف هذا السطر قبل استخدام ok

        if self.is_connected and self.lock_manager:
            try:
                got_remote_lock = self.lock_manager.acquire_lock(timeout=10, retry_delay=1, lock_ttl=120)
            except Exception:
                got_remote_lock = False

        if not got_remote_lock:
            # fallback لقفل محلي
            if os.path.exists(lock_file):
                try:
                    with open(lock_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if time.time() - data.get("start_time", 0) < 120:
                        self._notify("⚙️ مزامنة أخرى قيد التنفيذ — الرجاء الانتظار.", "warning")
                        return
                except Exception:
                    pass
                try:
                    os.remove(lock_file)
                except Exception:
                    pass
            try:
                with open(lock_file, "w", encoding="utf-8") as f:
                    json.dump({"start_time": time.time(), "client_id": self.client_id}, f)
                got_local_lock = True
            except Exception:
                return

        try:
            if not self.is_connected:
                ok = self.initialize_google()

            if ok:
                #self._notify("✅ تم إعادة الاتصال بـ Google Sheets. جاري المزامنة...", "success")
                pass
            else:
                self._notify("⚠️ المزامنة غير ممكنة: أنت تعمل في وضع Offline. جاري العمل محلياً.", "warning")
                return

            # رفع بيانات -> Google
            try:
                sync_products(self.products_sheet, self.DATABASE_FILE, ui=self.ui)
            except Exception as e:
                print("error syncing products:", e)
                self.is_connected = False
                self._notify("⚠️ فقد الاتصال أثناء رفع المنتجات.", "warning")
                return
            if got_remote_lock:
                try:
                    self.lock_manager.refresh_remote_lock()
                except:
                    pass

            # رفع القوائم
            try:
                sync_lists(self.lists_sheet, self.LISTS_FILE, ui=self.ui)
            except Exception as e:
                print("error syncing lists:", e)
                self.is_connected = False
                self._notify("⚠️ فقد الاتصال أثناء رفع القوائم.", "warning")
                return
            if got_remote_lock:
                try:
                    self.lock_manager.refresh_remote_lock()
                except:
                    pass

            # تحميل من Google -> محلي
            try:
                download_products(self.products_sheet, self.DATABASE_FILE)
            except Exception as e:
                print("error downloading products:", e)
                self.is_connected = False
                self._notify("⚠️ فقد الاتصال أثناء تحميل المنتجات.", "warning")
            if got_remote_lock:
                try:
                    self.lock_manager.refresh_remote_lock()
                except:
                    pass

            try:
                download_lists(self.lists_sheet, self.LISTS_FILE)
            except Exception as e:
                print("error downloading lists:", e)
                self.is_connected = False
                self._notify("⚠️ فقد الاتصال أثناء تحميل القوائم.", "warning")
            if got_remote_lock:
                try:
                    self.lock_manager.refresh_remote_lock()
                except:
                    pass

            # Update UI after sync
            if self.ui:
                try:
                    if hasattr(self.ui, "refresh_tools_list"):
                        self.ui.refresh_tools_list()
                except Exception as e:
                    pass

            # Update UI after sync
            # ✅ بعد تحميل المنتجات من Google Sheets
            download_products(self.products_sheet, self.DATABASE_FILE)

            # 🟢 تحديث الكاش والواجهة بعد المزامنة
            if self.ui:
                try:
                    if hasattr(self.ui, "data_manager"):
                        # تحميل النسخة الجديدة من الملف
                        self.ui.data_manager.load_tools()

                    # تحديث عناصر الواجهة
                    if hasattr(self.ui, "refresh_tools_list"):
                        self.ui.refresh_tools_list()
                    elif hasattr(self.ui, "reload_data"):
                        self.ui.reload_data()
                    else:
                        pass
                except Exception as e:
                    pass


            if self.is_connected:
                pass
                #self._notify(f"✅ تمت المزامنة بنجاح — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "success")
            else:
                self._notify(f"⚠️ فشلت المزامنة. لا يوجد اتصال بالإنترنت أو تم فقدانه.", "warning")

        finally:
            # فك الأقفال
            try:
                if got_remote_lock and self.lock_manager:
                    try:
                        self.lock_manager.release_lock()
                    except:
                        pass
                if got_local_lock and os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                    except:
                        pass
            except Exception:
                pass

    def delete_product_from_sheet(self, final_code: str):
        """
        حذف منتج من Google Sheets بناءً على الكود النهائي (final_code)
        """
        try:
            # ✅ تأكد أن الاتصال جاهز
            if not self.is_connected or not self.products_sheet:
                self._notify("⚠️ لا يوجد اتصال بـ Google Sheets، سيتم إعادة الاتصال الآن...", "warning")
                if not self.initialize_google():
                    self._notify("❌ فشل الاتصال بـ Google Sheets أثناء محاولة الحذف.")
                    return False

            products_sheet = self.products_sheet
            records = products_sheet.get_all_records()
            row_to_delete = None

            # ابحث عن الصف المطلوب
            for idx, row in enumerate(records, start=2):  # نبدأ من الصف 2 (العناوين)
                if str(row.get("final_code", "")).strip().lower() == str(final_code).strip().lower():
                    row_to_delete = idx
                    break

            if row_to_delete:
                products_sheet.delete_rows(row_to_delete)
                #print(f"🗑️ تم حذف الأداة من Google Sheets (Row {row_to_delete})")
                return True
            else:
                #print(f"⚠️ لم يتم العثور على الأداة في Google Sheets بالكود: {final_code}")
                return False

        except Exception as e:
            print(f"⚠️ خطأ أثناء حذف الأداة من Google Sheets: {e}")
            return False

    def update_product_in_sheet(self, final_code: str, updated_tool: dict) -> bool:
        """
        تحديث منتج في Google Sheets بناءً على الكود النهائي (final_code)
        """
        try:
            # ✅ تأكد من وجود الاتصال
            if not self.is_connected or not self.products_sheet:
                if not self.initialize_google():
                    #print("⚠️ لا يمكن الاتصال بـ Google Sheets الآن.")
                    return False

            # ✅ جلب كل البيانات
            records = self.products_sheet.get_all_records()
            row_to_update = None

            # ✅ ابحث عن الصف اللي يحتوي على الكود النهائي المطلوب
            for idx, row in enumerate(records, start=2):
                sheet_code = str(row.get("final_code", "")).strip()
                if sheet_code.lower() == str(final_code).strip().lower():
                    row_to_update = idx
                    break



            # ✅ لو الأداة مش موجودة نضيفها كصف جديد بدل ما نسيبها
            if not row_to_update:
                print(f"⚠️ لم يتم العثور على الأداة في Google Sheets، سيتم إضافتها كصف جديد.")
                new_row = [
                    updated_tool.get("name_ar", ""),
                    updated_tool.get("name_en", ""),
                    updated_tool.get("category", ""),
                    updated_tool.get("description", ""),
                    json.dumps(updated_tool.get("properties", {}), ensure_ascii=False),
                    updated_tool.get("template", ""),
                    final_code,
                    updated_tool.get("project_name", ""),
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                ]
                self.products_sheet.append_row(new_row)
                return True

            # ✅ تجهيز البيانات الجديدة بنفس ترتيب الأعمدة في الجدول
            updated_row = [
                updated_tool.get("name_ar", ""),
                updated_tool.get("name_en", ""),
                updated_tool.get("category", ""),
                updated_tool.get("description", ""),
                json.dumps(updated_tool.get("properties", {}), ensure_ascii=False),
                updated_tool.get("template", ""),
                final_code,
                updated_tool.get("project_name", ""),
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            ]

            # ✅ تحديث الصف المحدد
            cell_range = f"A{row_to_update}:I{row_to_update}"
            self.products_sheet.update(cell_range, [updated_row])
            print(f"📝 تم تحديث الأداة في Google Sheets (Row {row_to_update}) بنجاح.")
            return True

        except Exception as e:
            print(f"⚠️ خطأ أثناء تحديث الأداة في Google Sheets: {e}")
            return False

                

    def __del__(self):
        try:
            if self.lock_manager:
                self.lock_manager.release_lock()
        except Exception:
            pass
