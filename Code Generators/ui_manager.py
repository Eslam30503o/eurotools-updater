import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from data_manager import DataManager
from google_sheets_uploader import GoogleSheetsUploader
import pandas as pd
import threading
import os
import gspread
import socket
import time
import requests
from google.oauth2.service_account import Credentials
from ui.products_ui import ProductsMixin
from ui.lists_ui import ListsMixin
from ui.export_excel import ExportExcelMixin
from ui.new_tool import NewToolMixin
from ui.edit_tool import EditToolMixin
from ui.printer import PrinterMixin
from ui.settings_ui import SettingsMixin
from sync.history_manager import HistoryManager


CATEGORIES = ["الكل", "BOM", "CNC Cutting Tools", "Hand Tools", "Machine Spare Parts", "Oil & Lubricants", "Stationary","Standared Components"]

class UIManager(ProductsMixin,
                ListsMixin,
                ExportExcelMixin,
                NewToolMixin,
                EditToolMixin,
                PrinterMixin,
                SettingsMixin):
    
    def __init__(self, root, data_manager, sync_manager=None, history_manager=None):
        self.root = root
        self.data_manager = data_manager
        self.gsu = GoogleSheetsUploader(root)
        self.sync_manager = sync_manager   # ✅ هذا هو التعديل الصحيح
        self.history = HistoryManager()
        self.selected_items = {}

        self.create_main_frames()
        self.root.after(300, lambda: self.update_products_list())
        self.sidebar_visible = False
        self.products_mixin = ProductsMixin()
        self.logged_in_user = None  # 🟢 هنا يتم حفظ اسم المستخدم بعد تسجيل الدخول

        if hasattr(self, 'get_final_code'):
            self.products_mixin.get_final_code = self.get_final_code

    # ==========================
    # 🔄 دالة مزامنة الآن
    # ==========================
    def sync_now(self):
        """مزامنة فورية مع Google Sheets + تحديث الواجهة"""
        if not self.sync_manager:
            self.show_toast("⚠️ مدير المزامنة غير جاهز بعد.", "warning")
            return

        if getattr(self, "_sync_in_progress", False):
            self.show_toast("⏳ المزامنة قيد التنفيذ حالياً...", "info")
            return

        self._sync_in_progress = True
        btn = getattr(self, "sync_now_btn", None)
        if btn:
            btn.configure(state="disabled", text="⏳ جاري المزامنة...")

        def do_sync():
            try:
                self.sync_manager.sync_all()
                self.root.after(0, self.reload_data)
                #self.show_toast("✅ تمت المزامنة بنجاح!", "success")
            except Exception as e:
                self.show_toast(f"⚠️ فشل أثناء المزامنة: {e}", "error")
            finally:
                self._sync_in_progress = False
                if btn:
                    self.root.after(0, lambda: btn.configure(state="normal", text="🔄 مزامنة الآن"))

        threading.Thread(target=do_sync, daemon=True).start()





    def get_final_code(self, tool_data) -> str:
        final_code = tool_data.get("template", "")
        
        if not isinstance(final_code, str):
            final_code = str(final_code)
        for prop_name, prop_value in tool_data.get("properties", {}).items():
            final_code = final_code.replace("{" + prop_name + "}", str(prop_value))
        return final_code.strip()



    def refresh_tools_list(self):
        """إعادة تحميل الأدوات من البيانات المحلية وتحديث الجدول"""
        self.data_manager.load_tools()
        #self.show_tools_table()  # أو أي ميثود عندك بتعيد بناء الجدول


    def reload_data(self):
        """إعادة تحميل البيانات وتحديث كل الواجهات"""
        try:
            # 🧩 تحميل الأدوات والقوائم من الملفات المحلية
            self.data_manager.load_tools()
            self.data_manager.load_lists()

            # 🔁 تحديث الجدول والقوائم (على واجهة المستخدم)
            if hasattr(self, "root"):
                self.root.after(0, self._safe_ui_update)
            else:
                self._safe_ui_update()

            print("🔃 واجهة المستخدم تم تحديثها بالكامل من البيانات المحلية.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء تحديث الواجهة: {e}")

    def _safe_ui_update(self):
        """تحديث آمن للـ UI"""
        if hasattr(self, "update_products_list"):
            self.update_products_list()

        if hasattr(self, "update_lists_view"):
            self.update_lists_view()


 
    def create_main_frames(self):
            self.main_container = ctk.CTkFrame(self.root)
            self.main_container.pack(expand=True, fill="both")

            self.products_frame = ctk.CTkFrame(self.main_container)
            self.products_frame.pack(side="right", expand=True, fill="both", padx=(10, 5), pady=10)
            
            self.lists_frame = ctk.CTkFrame(self.main_container, width=500)
            self.lists_visible = False  # القوائم مخفية في البداية

            #self.lists_frame.pack(side="left", fill="both", padx=(5, 10), pady=10)
            
            self.create_products_ui()
            self.create_lists_ui()
            self.create_connection_status_bar()

            self.lists_visible = False  # القوائم مخفية في البداية



    def create_connection_status_bar(self):
        """شريط حالة الاتصال بالإنترنت"""
        self.connection_frame = ctk.CTkFrame(
            self.root,
            fg_color="#2C3E50",
            height=30,
            corner_radius=0
        )
        self.connection_frame.pack(side="top", fill="x")

        self.connection_label = ctk.CTkLabel(
            self.connection_frame,
            text="🔄 جاري فحص الاتصال...",
            font=("Cairo", 13, "bold"),
            text_color="white"
        )
        self.connection_label.pack(pady=3)

        # بدء الفحص الدوري
        self.update_connection_status()

        
    def check_internet_connection(self, timeout=3):
        """🌐 فحص حالة الاتصال بالإنترنت"""
        try:
            start = time.time()
            requests.get("https://www.google.com", timeout=timeout)
            ping = time.time() - start
            if ping > 1.5:
                return "weak"   # بطيء
            return "ok"         # سريع
        except:
            return "offline"


    def update_connection_status(self):
        """🔁 تحديث شريط الحالة كل 5 ثواني"""
        if not hasattr(self, "connection_frame") or not self.connection_frame.winfo_exists():
            return
        status = self.check_internet_connection()

        if status == "ok":
            # ✅ متصل
            self.connection_frame.configure(fg_color="#1E8449")  # أخضر
            self.connection_label.configure(
                text="🟢 متصل بالإنترنت",
                text_color="white"
            )
            self.enable_manual_sync_button()

        elif status == "weak":
            # ⚠️ ضعيف
            self.connection_frame.configure(fg_color="#F39C12")  # برتقالي
            self.connection_label.configure(
                text="🟠 الاتصال ضعيف",
                text_color="black"
            )
            self.enable_manual_sync_button()

        else:
            # ❌ غير متصل
            self.connection_frame.configure(fg_color="#922B21")  # أحمر
            self.connection_label.configure(
                text="🔴 غير متصل بالإنترنت",
                text_color="white"
            )
            self.disable_manual_sync_button()

        # يعيد التحديث كل 5 ثواني
        self.root.after(5000, self.update_connection_status)

    def clear_root(self):
        """حذف جميع العناصر من نافذة الجذر"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_history_page(self):
        """عرض صفحة سجل العمليات بشكل صحيح داخل الواجهة الرئيسية"""
        from ui.history_screen import HistoryScreen
        
        # أخفي الواجهات الحالية بدل ما أحذفها
        if hasattr(self, "clear_main_frames"):
            self.clear_main_frames()
        else:
            for widget in self.main_container.winfo_children():
                widget.pack_forget()

        data_dir = getattr(self.data_manager, "safe_data_dir", None)
        if not data_dir:
            messagebox.showerror("خطأ", "⚠️ لم يتم العثور على مسار البيانات (data_dir).")
            return

        # إنشاء صفحة السجل داخل main_container (مش root)
        self.history_screen = HistoryScreen(
                parent=self.main_container, 
                ui_manager=self, # ⬅️ تمرير 'self' (كائن UIManager) هنا
                data_dir=data_dir
            )  
        self.history_screen.pack(fill="both", expand=True)

        
            # ==========================
    # 🔘 التحكم في زر المزامنة اليدوية
    # ==========================
    def enable_manual_sync_button(self):
        """تمكين زر المزامنة اليدوية"""
        try:
            if hasattr(self, "sync_now_btn") and self.sync_now_btn:
                self.sync_now_btn.configure(state="normal", text="🔄 مزامنة الآن")
        except :
            pass

    def disable_manual_sync_button(self):
        """تعطيل زر المزامنة اليدوية"""
        try:
            if hasattr(self, "sync_now_btn") and self.sync_now_btn:
                self.sync_now_btn.configure(state="disabled", text="🚫 غير متصل")
        except Exception as e:
            pass



    def return_to_main(self):
        """العودة إلى الواجهة الرئيسية بعد عرض السجل (مع debug)"""
        try:
            if hasattr(self, "clear_main_frames"):
                self.clear_main_frames()
            else:
                print("🔴 [DEBUG] لا توجد دالة clear_main_frames()!")

            if hasattr(self, "products_frame"):
                self.products_frame.pack(side="right", expand=True, fill="both", padx=(10, 5), pady=10)
            else:
                print("🔴 [DEBUG] لا يوجد products_frame!")

        except Exception as e:
            import traceback
            print("❌ [DEBUG] Exception in return_to_main:", e)
            print(traceback.format_exc())
