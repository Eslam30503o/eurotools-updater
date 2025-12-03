import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
import pandas as pd
import threading
import time
import requests

from google.oauth2.service_account import Credentials
from data_manager import DataManager
from ui.products_ui import ProductsMixin
from ui.lists_ui import ListsMixin
from ui.export_excel import ExportExcelMixin
from ui.new_tool import NewToolMixin,SearchableDropdown
from ui.edit_tool import EditToolMixin
from ui.printer import PrinterMixin
from ui.settings_ui import SettingsMixin
from sync.history_manager import HistoryManager
from ui.history_screen import HistoryScreen
#from ui.items_form import DynamicFormApp

#from google_sheets_uploader import GoogleSheetsUploader
from ui.products_ui import ProductsMixin
from categories import CATEGORIES
#from ui.items_form import SearchableDropdown


CATEGORIES = CATEGORIES
class UIManager(ProductsMixin,
                ListsMixin,
                ExportExcelMixin,
                NewToolMixin,
                EditToolMixin,
                PrinterMixin,
                SettingsMixin):
    
    def __init__(self, root, data_manager,app_ref, sync_manager=None, history_manager=None):
        self.root = root
        self.data_manager = data_manager
        #self.gsu = GoogleSheetsUploader(root)
        self.sync_manager = sync_manager   # ✅ هذا هو التعديل الصحيح
        self.history = HistoryManager()
        self.selected_items = {}

        self.app_ref = app_ref

        self.create_main_frames()
        self.root.after(100, lambda: self.update_products_list())
        self.sidebar_visible = False
        self.products_mixin = ProductsMixin()
        self.logged_in_user = None  # 🟢 هنا يتم حفظ اسم المستخدم بعد تسجيل الدخول
        self.logged_in_role = None
        

        #self.properties_container = ctk.CTkFrame(self.root)
        self.condition_widgets = []


        if hasattr(self, 'get_final_code'):
            self.products_mixin.get_final_code = self.get_final_code

        # print('ui')
        # role = self.app_ref.logged_in_role  # لو عايز تجيب الصلاحيه 
    
        # print(role)
        # print("self.app_ref.logged_in_role")



    # ==========================
    # 🔄 دالة مزامنة الآن
    # ==========================
    def sync_now(self):
        """مزامنة فورية مع Google Sheets + تحديث الواجهة"""
        if not self.sync_manager:
            self.show_toast("⚠️ مدير المزامنة غير جاهز بعد.", "warning")
            return

        if getattr(self, "_sync_in_progress", False):
            self.show_toast("⏳ المزامنة قيد التنفيذ حالياً", "info")
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
                    self.root.after(200, lambda: btn.configure(state="normal", text="🔄 مزامنة الآن"))

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

            #print("🔃 واجهة المستخدم تم تحديثها بالكامل من البيانات المحلية.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء تحديث الواجهة: {e}")


    def _safe_ui_update(self):
        """🔄 تحديث آمن وسريع للـ UI بدون تجميد."""
        try:
            # أولاً نحدث واجهة المستخدم بشكل بسيط (loading message مثلاً)
            if hasattr(self, "products_count_label"):
                self.products_count_label.configure(text="🔄 جاري تحديث البيانات...")

            # تحديث المنتجات في خيط منفصل
            if hasattr(self, "update_products_list"):
                threading.Thread(
                    target=lambda: self.root.after(0, self.update_products_list),
                    daemon=True
                ).start()

            # تحديث القوائم بعد تأخير بسيط عشان الواجهة متتلخبطش
            if hasattr(self, "update_lists_view"):
                self.root.after(1000, self.update_lists_view)

            # بعد انتهاء كل التحديثات، أعد النص الافتراضي
            #self.root.after(2000, lambda: self.products_count_label.configure(
                #text="✅ تم تحديث الواجهة بنجاح"
            #))

        except Exception as e:
            print(f"⚠️ خطأ أثناء تحديث الواجهة: {e}")


    def create_main_frames(self):
            self.main_container = ctk.CTkFrame(self.root)
            self.main_container.pack(expand=True, fill="both")

            self.products_frame = ctk.CTkFrame(self.main_container)
            self.products_frame.pack(side="right", expand=True, fill="both", padx=(10, 5), pady=10)
            
            self.lists_frame = ctk.CTkFrame(self.main_container, width=100) #500
            self.lists_visible = False  # القوائم مخفية في البداية

            #self.lists_frame.pack(side="left", fill="both", padx=(5, 10), pady=10)
            


            
            self.create_products_ui()
            self.create_lists_ui()
            self.create_connection_status_bar()


            self.lists_visible = False  # القوائم مخفية في البداية
            

    def create_connection_status_bar(self):
        """🔹 إنشاء شريط حالة الاتصال"""
        self.connection_frame = ctk.CTkFrame(
            self.root,
            fg_color="#2C3E50",
            height=15,
            corner_radius=0
        )
        self.connection_label = ctk.CTkLabel(
            self.connection_frame,
            text="🔄 جاري فحص الاتصال...",
            font=("Cairo", 13, "bold"),
            text_color="white"
        )
        self.connection_label.pack(pady=3)
        self.update_connection_status()  # بدء الفحص الدوري


    def check_internet_connection(self, timeout=3):
        """🌐 فحص حالة الاتصال بالإنترنت"""
        try:
            start = time.time()
            requests.get("https://www.google.com", timeout=timeout)
            ping = time.time() - start
            if ping > 1.5:
                return "weak"   # الإنترنت بطيء
            return "ok"         # متصل وسريع
        except:
            return "offline"


    def update_connection_status(self):
        """🔁 تشغيل الفحص في Thread منفصل وتحديث الواجهة بأمان"""
        def background_check():
            status = self.check_internet_connection()
            self.root.after(0, lambda: self.update_connection_ui(status))

        threading.Thread(target=background_check, daemon=True).start()
        self.root.after(10000, self.update_connection_status)  # تكرار كل 5 ثواني


    def update_connection_ui(self, status):
        """🎨 تحديث واجهة الشريط حسب حالة الاتصال"""
        if status == "ok":
            # 🔵 متصل بسرعة جيدة
            self.connection_frame.pack_forget()  # إخفاء الشريط تمامًا
            self.enable_manual_sync_button()

        elif status == "weak":
            # 🟡 الإنترنت بطيء
            self.connection_frame.configure(fg_color="#F39C12")  # برتقالي
            self.connection_label.configure(
                text="🟠 الاتصال ضعيف",
                text_color="black"
            )
            self.connection_frame.pack(side="top", fill="x")
            self.enable_manual_sync_button()

        else:
            # 🔴 غير متصل بالإنترنت
            self.connection_frame.configure(fg_color="#922B21")  # أحمر
            self.connection_label.configure(
                text="🔴 غير متصل بالإنترنت",
                text_color="white"
            )
            self.connection_frame.pack(side="top", fill="x")
            self.disable_manual_sync_button()


    def enable_manual_sync_button(self):
        """✅ تمكين زر المزامنة اليدوية بأمان"""
        try:
            if hasattr(self, "sync_now_btn") and self.sync_now_btn:
                self.root.after(0, lambda: self.sync_now_btn.configure(state="normal", text="🔄 مزامنة الآن"))
        except:
            pass


    def disable_manual_sync_button(self):
        """🚫 تعطيل زر المزامنة اليدوية بأمان"""
        try:
            if hasattr(self, "sync_now_btn") and self.sync_now_btn:
                self.root.after(0, lambda: self.sync_now_btn.configure(state="disabled", text="🚫 غير متصل"))
        except Exception:
            pass


    def clear_root(self):
        """حذف جميع العناصر من نافذة الجذر"""
        for widget in self.root.winfo_children():
            widget.destroy()


    def create_history_page(self):
        """عرض صفحة سجل العمليات بشكل صحيح داخل الواجهة الرئيسية"""
        
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


    # def apply_conditions(self, selected_key, code_template_2=None):
        
    #     """يفحص شروط الـ Condition ويضيف خصائص جديدة أو يحدث الكود مباشرة"""
    #     if not hasattr(self, 'condition_props') or not self.condition_props:
    #         return

    #     for cond in self.condition_props:
    #         prop_name = cond.get("property")
    #         operator = cond.get("condition")
    #         compare_value = cond.get("value")
    #         if_action = cond.get("if_action", {})

    #         current_value = None
    #         for pname, widget in self.props_fields:
    #             if pname == prop_name:
    #                 if isinstance(widget, ctk.CTkEntry) or isinstance(widget, SearchableDropdown):
    #                     current_value = widget.get().strip()
    #                 break
                

    #         if current_value is None:
    #             continue

    #         try:
    #             expr = f"'{current_value}' {operator} '{compare_value}'"
    #             result = eval(expr)
    #         except:
    #             result = False

    #     # حذف أي تغييرات سابقة إذا لم يتحقق الشرط
    #         prop_name_new = if_action.get("prop_name")
    #         if not result and prop_name_new in self.condition_widgets:
    #             widget_to_remove = self.condition_widgets[prop_name_new]
    #             widget_to_remove.destroy()
    #             del self.condition_widgets[prop_name_new]
                
                

    #         if result:
    #             action_type = if_action.get("action")
    #             if action_type in ("add_property", "add_property_edit_code"):
    #                 prop_name_new = if_action.get("prop_name")
    #                 prop_type_new = if_action.get("prop_type", "entry")
    #                 data_type_new = if_action.get("data_type", "any")
    #                 values_new = if_action.get("values", [])
    #                 if not isinstance(values_new, list):
    #                     values_new = [values_new]
    #                 # add_property_frame تحتاج تكون موجودة في الكلاس
    #                 widget =self.add_property_frame(
    #                     self.properties_container, 
    #                     selected_key, 
    #                     prop_name_new, 
    #                     prop_type_new, 
    #                     data_type_new,
    #                     values_new
    #                 )

    #                 self.condition_widgets.append(widget)

    #                 if action_type in ("add_property_edit_code", "edit_code"):
    #                     # تحديث الـ template مباشرة
    #                     if code_template_2:
    #                         self.template_entry_new.configure(text=code_template_2)
                
    #             elif action_type=="edit_code":
    #                 # تحديث الـ template مباشرة
    #                 if code_template_2:
    #                     self.template_entry_new.configure(text=code_template_2)
                
    #             # elif prop_name_new in self.condition_widgets:
    #             #     widget_to_remove = self.condition_widgets[prop_name_new]
    #             #     widget_to_remove.destroy()
    #             #     del self.condition_widgets[prop_name_new]

    def apply_conditions(self, selected_key, code_template_2=None):
        if not hasattr(self, 'condition_props') or not self.condition_props:
            return

        if not hasattr(self, "condition_widgets") or not isinstance(self.condition_widgets, dict):
            self.condition_widgets = {}


        # تأكد من وجود نسخة أصلية للقالب
        if not hasattr(self, "original_template"):
            self.original_template = self.template_entry_new.cget("text")


        for cond in self.condition_props:
            prop_name = cond.get("property")
            operator = cond.get("condition")
            compare_value = cond.get("value")
            if_action = cond.get("if_action", {})

            current_value = None
            for pname, widget in self.props_fields:
                if pname == prop_name:
                    if isinstance(widget, ctk.CTkEntry) or isinstance(widget, SearchableDropdown):
                        current_value = widget.get().strip()
                    break

            if current_value is None:
                continue

            try:
                expr = f"'{current_value}' {operator} '{compare_value}'"
                result = eval(expr)
            except:
                result = False

            prop_name_new = if_action.get("prop_name")
            action_type = if_action.get("action")

            # 🔥 الحل الجديد: معالجة حالة عدم تحقق الشرط لكل نوع من أنواع الـ actions
            if not result:
                if action_type == "edit_code":
                    # إرجاع الكود الأصلي عند عدم تحقق الشرط
                    self.template_entry_new.configure(text=self.original_template)
                
                elif action_type in ("add_property", "add_property_edit_code"):
                    # حذف الخاصية المضافة إذا كانت موجودة
                    if prop_name_new and prop_name_new in self.condition_widgets:
                        self.condition_widgets[prop_name_new].destroy()
                        del self.condition_widgets[prop_name_new]
                        
                        # إرجاع الكود الأصلي إذا كان add_property_edit_code
                        if action_type == "add_property_edit_code":
                            self.template_entry_new.configure(text=self.original_template)
                        
                        # حذف من props_fields
                        self.props_fields = [(pname, w) for pname, w in self.props_fields if pname != prop_name_new]
                
                continue  # انتقل للشرط التالي

            # حالة تحقق الشرط
            if result:
                if action_type == "edit_code" and code_template_2:
                    # تحديث الكود الجديد
                    self.template_entry_new.configure(text=code_template_2)
                    print(f"✅ تم تحديث الكود: {prop_name} {operator} {compare_value}")
                
                elif action_type in ("add_property", "add_property_edit_code"):
                    prop_type_new = if_action.get("prop_type", "entry")
                    data_type_new = if_action.get("data_type", "any")
                    values_new = if_action.get("values", [])
                    if not isinstance(values_new, list):
                        values_new = [values_new]

                    # إضافة الخاصية الجديدة
                    widget = self.add_property_frame(
                        self.properties_container, 
                        selected_key, 
                        prop_name_new, 
                        prop_type_new, 
                        data_type_new,
                        values_new
                    )
                    self.condition_widgets[prop_name_new] = widget

                    if action_type == "add_property_edit_code" and code_template_2:
                        self.template_entry_new.configure(text=code_template_2)



    def add_property_frame(self, container, item_name, prop_name, prop_type="entry", data_type="any", values=None):

        if hasattr(self, "props_fields"):
            for i, (pname, widget) in enumerate(self.props_fields):
                if pname == prop_name:
                    # حذف الإطار الحاوي للويجيت (frame) وليس الويجيت فقط
                    widget.master.destroy()
                    del self.props_fields[i]
                    break
        # إنشاء الإطار
        frame = ctk.CTkFrame(container, corner_radius=8)
        frame.pack(fill="x", padx=10, pady=5)

        # تسمية الخاصية
        label = ctk.CTkLabel(frame, text=prop_name, font=("Arial", 12, "bold"), anchor="w")
        label.pack(anchor="w", padx=10, pady=3)

        # إضافة الويدجيت بناءً على النوع
        if prop_type == "entry":
            widget = ctk.CTkEntry(frame, placeholder_text=f"أدخل {prop_name}", font=("Arial", 12), height=35)
            widget.pack(fill="x", padx=10, pady=(0,5))
        elif prop_type == "dropdown":
            
            if not values:
                values = ["(اختر)"]
            widget = SearchableDropdown(frame, values=values, placeholder_text="اختر", font=("Arial", 12))
            widget.pack(fill="x", padx=10, pady=(0,5))

        else:
            widget = ctk.CTkLabel(frame, text=f"(نوع غير معروف: {prop_type})")
            widget.pack(anchor="w", padx=10, pady=5)

        # حفظ الويدجيت ضمن قائمة الخصائص لتسهيل الوصول لاحقًا
        if not hasattr(self, "props_fields"):
            self.props_fields = []
        self.props_fields.append((prop_name, widget))
        return frame 