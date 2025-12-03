import customtkinter as ctk
from functools import partial
from tkinter import messagebox
import tkinter as tk
import json
from pathlib import Path
from ui.history_screen import HistoryScreen
from sync.manager import SyncManager
import threading
from categories import CATEGORIES
import os

CATEGORIES = CATEGORIES

class ProductActionsMixin: 

    def manual_sync(self):
        """زر مزامنة الآن مع شريط تقدم متحرك و Spinner أثناء التنفيذ"""
        #print("🧩 SyncManager:", self.sync_manager)

        if not hasattr(self, "sync_manager") or self.sync_manager is None:
            self.show_toast("⚠️ مدير المزامنة غير جاهز بعد.", "warning")
            return

        if getattr(self, "_sync_in_progress", False):
            self.show_toast("⏳ المزامنة قيد التنفيذ حالياً...", "info")
            return

        self._sync_in_progress = True
        btn = getattr(self, "sync_now_btn", None)

        # إنشاء إطار شريط التقدم
        progress_container = ctk.CTkFrame(self.products_frame, fg_color="transparent")
        progress_bar = ctk.CTkProgressBar(progress_container, width=300, height=10)
        progress_bar.pack(pady=(8, 5))
        progress_bar.set(0)
        progress_container.pack()

        # 🔄 Spinner Label بجانب النص
        spinner_label = None
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        def animate_spinner(index=0):
            """تحريك شكل اللودنج أثناء المزامنة"""
            if not getattr(self, "_sync_in_progress", False):
                if spinner_label:
                    spinner_label.destroy()
                return
            spinner_label.configure(text=spinner_frames[index % len(spinner_frames)])
            self.root.after(100, lambda: animate_spinner(index + 1))

        # تعديل الزر مؤقتًا
        if btn:
            btn.configure(
                text=" جاري المزامنة ",
                fg_color=("#7F8C8D", "#566573"),
                hover_color=("#7F8C8D", "#566573"),
                state="disabled"
            )
            # إضافة الـ Spinner جوه الزر
            spinner_label = ctk.CTkLabel(btn, text="", font=("Consolas", 20))
            spinner_label.place(relx=0.1, rely=0.5, anchor="center")
            animate_spinner()  # 🔁 بدء التحريك

        # حركة شريط التقدم التدريجية
        def animate_progress():
            if not getattr(self, "_sync_in_progress", False):
                return
            current = progress_bar.get()
            if current < 0.9:
                progress_bar.set(current + 0.03)
                self.root.after(100, animate_progress)

        animate_progress()

        def reset_ui():
            """إعادة الزر لوضعه الطبيعي بعد الانتهاء"""
            if spinner_label:
                spinner_label.destroy()
            if btn:
                btn.configure(
                    text="🔄 مزامنة الآن",
                    fg_color=("#2874A6", "#1F618D"),
                    hover_color=("#34495E", "#1C2833"),
                    state="normal"
                )
            if progress_container.winfo_exists():
                progress_container.destroy()


        def do_sync():
            try:
                if hasattr(self.sync_manager, "stop_event"):
                    self.sync_manager.stop_event.set()  # ⏸️ إيقاف AutoSync مؤقتًا

                #self.show_toast("🔄 جاري المزامنة ", "info")
                self.sync_manager.sync_all()
                self.root.after(0, lambda: progress_bar.set(1.0))
                #self.show_toast("✅ تمت المزامنة بنجاح!", "success")
                self.root.after(0, self.reload_data)

            except Exception as e:
                print("⚠️ خطأ أثناء المزامنة:", e)
                #self.show_toast(f"⚠️ فشل في المزامنة: {e}", "error")
                self.root.after(0, lambda: progress_bar.configure(progress_color="#C0392B"))

            finally:
                self._sync_in_progress = False
                if hasattr(self.sync_manager, "stop_event"):
                    self.sync_manager.stop_event.clear()
                self.root.after(1500, reset_ui)

        threading.Thread(target=do_sync, daemon=True).start()
        
    def create_history_page(self):
        """📜 فتح شاشة السجل"""
        if hasattr(self, "_history_window") and self._history_window.winfo_exists():
            self._history_window.focus()
            return

        self._history_window = ctk.CTkToplevel(self.root)
        self._history_window.title("📜 سجل العمليات - My Tools Sync")
        self._history_window.geometry("1000x700")
        self._history_window.transient(self.root)
        self._history_window.grab_set()

        container = ctk.CTkFrame(self._history_window, corner_radius=15)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        history_ui = HistoryScreen(container, data_dir=self.data_manager.data_dir)
        history_ui.pack(fill="both", expand=True)

    def show_product_details(self, tool_name_en, tool_data, final_code):
        """نافذة تفاصيل المنتج - تصميم احترافي"""
        win = ctk.CTkToplevel(self.root)
        win.title(f"تفاصيل المنتج - {tool_data.get('name_ar', tool_name_en)}")
        win.geometry("700x600")
        win.transient(self.root)
        win.grab_set()

        # ====== Header ======
        header = ctk.CTkFrame(win, fg_color=("#2C3E50", "#1C2833"), corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=f"📦 {tool_data.get('name_ar', 'غير محدد')} ({tool_name_en})",
            font=("Cairo", 22, "bold"),
            text_color="#ECF0F1"
        ).pack(pady=15)

        # ====== Details Section ======
        body = ctk.CTkScrollableFrame(win, fg_color=("white", "#2B2B2B"), corner_radius=15)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # المعلومات الأساسية
        details = [
            ("الاسم بالعربي", tool_data.get("name_ar", "غير محدد")),
            ("الاسم بالإنجليزية", tool_name_en),
            ("الوصف", tool_data.get("description", "لا يوجد")),
            ("الفئة", tool_data.get("category", "غير محددة")),
            ("المشروع او مكنة", tool_data.get("project_name", "غير محدد")),
            ("الكود النهائي", final_code),
        ]

        for label, value in details:
            frame = ctk.CTkFrame(body, fg_color=("gray94", "#1C2833"), corner_radius=12)
            frame.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(frame, text=f": {label}", font=("Cairo", 14, "bold")).pack(side="right", padx=10, pady=10)
            ctk.CTkLabel(frame, text=value, font=("Cairo", 14)).pack(side="right", padx=10)

        # الخصائص
        props = tool_data.get("properties", {})
        if props:
            props_title = ctk.CTkLabel(body, text="⚙️ الخصائص", font=("Cairo", 16, "bold"))
            props_title.pack(pady=(15, 5))
            for k, v in props.items():
                prop_frame = ctk.CTkFrame(body, fg_color=("gray95", "#212F3C"), corner_radius=8)
                prop_frame.pack(fill="x", padx=15, pady=4)
                ctk.CTkLabel(prop_frame, text=f": {k}", font=("Cairo", 13, "bold")).pack(side="right", padx=10, pady=6)
                ctk.CTkLabel(prop_frame, text=str(v), font=("Cairo", 13)).pack(side="right", padx=10)

        # ====== Action Buttons ======
        actions_frame = ctk.CTkFrame(win, fg_color="transparent")
        actions_frame.pack(fill="x", pady=15)

        buttons = [
            ("🖨️ طباعة", "#2874A6", "#1F618D", lambda: self.show_print_dialog(final_code)),
            ("✍️ تعديل", "#D68910", "#B9770E", lambda: self.edit_tool_window(tool_name_en)),
            ("🗑️ حذف", "#C0392B", "#A93226", lambda: self.delete_tool(tool_name_en)),
            ("❌ إغلاق", "#7F8C8D", "#566573", win.destroy),
        ]

        for text, color, hover, cmd in buttons:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                fg_color=color,
                hover_color=hover,
                command=cmd,
                corner_radius=10,
                width=120,
                height=42,
                font=("Cairo", 13, "bold")
            )
            btn.pack(side="right", padx=8)

    def delete_tool(self, tool_name_en):
        """حذف أداة بعد إدخال كلمة سر للتأكيد"""
    

        base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "EuroTools" / "data"
        self.SETTING = str(base_dir / "app_settings.json")
        os.makedirs(base_dir, exist_ok=True)

       
        if os.path.exists(self.SETTING):
            with open(self.SETTING, "r", encoding="utf-8") as f:
                settings = json.load(f)
            correct_password = settings.get("admin_password", "Admin@123")
        else:
            correct_password = "Admin@123"
        # نافذة كلمة السر
        password_window = ctk.CTkToplevel(self.root)
        password_window.title("🔒 تأكيد الهوية قبل الحذف")
        password_window.geometry("700x500")
        password_window.transient(self.root)
        password_window.grab_set()

        # توسيط النافذة
        password_window.update_idletasks()
        x = (password_window.winfo_screenwidth() // 2) - 225
        y = (password_window.winfo_screenheight() // 2) - 160
        password_window.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(password_window, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # أيقونة التحذير
        ctk.CTkLabel(
            frame,
            text="⚠️",
            font=("Arial", 60)
        ).pack(pady=(20, 10))

        # عنوان النافذة
        header_label = ctk.CTkFrame(frame, fg_color=("#e74c3c", "#c0392b"), corner_radius=10)
        header_label.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            header_label,
            text="🗑️ تأكيد الحذف",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(pady=10)

        # رسالة التأكيد
        ctk.CTkLabel(
            frame,
            text=f"هل ترغب في حذف الأداة:",
            font=("Arial", 13),
            justify="center"
        ).pack(pady=(5, 5))
        
        ctk.CTkLabel(
            frame,
            text=tool_name_en,
            font=("Arial", 18, "bold"),
            text_color=("#e74c3c", "#c0392b"),
            justify="center"
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            frame,
            text="أدخل كلمة السر للتأكيد:",
            font=("Arial", 12),
            justify="center"
        ).pack(pady=(0, 15))

        # حقل كلمة السر
        password_entry = ctk.CTkEntry(
            frame,
            placeholder_text="كلمة السر",
            show="*",
            height=42,
            font=("Arial", 13),
            corner_radius=8
        )
        password_entry.pack(fill="x", padx=40, pady=(0, 20))
        password_entry.focus()

        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=40, pady=(0, 15)) 
        def verify_and_delete():
            if password_entry.get().strip() == correct_password:
                password_window.destroy()
                confirm_delete()
            else:
                messagebox.showerror("خطأ", "❌ كلمة السر غير صحيحة!")
            if password_window.winfo_exists():
                x, y = password_window.winfo_x(), password_window.winfo_y()
                for i in range(3):
                    if not password_window.winfo_exists():
                        break
                    password_window.geometry(f"+{x + 10}+{y}")
                    password_window.update_idletasks()
                    password_window.after(50)

                    if not password_window.winfo_exists():
                        break
                    password_window.geometry(f"+{x - 10}+{y}")
                    password_window.update_idletasks()
                    password_window.after(50)

                if password_window.winfo_exists():
                    password_window.geometry(f"+{x}+{y}")


                


        def confirm_delete():
            """نافذة التأكيد النهائية"""
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("⚠️ تأكيد نهائي")
            dialog.geometry("700x500")
            dialog.transient(self.root)
            dialog.grab_set()

            # توسيط النافذة
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - 250
            y = (dialog.winfo_screenheight() // 2) - 160
            dialog.geometry(f"+{x}+{y}")

            main_frame = ctk.CTkFrame(dialog, corner_radius=20)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # أيقونة تحذير كبيرة
            ctk.CTkLabel(
                main_frame,
                text="🚨",
                font=("Arial", 70)
            ).pack(pady=(25, 15))

            # رسالة التحذير
            warning_frame = ctk.CTkFrame(main_frame, fg_color=("#fff3cd", "#856404"), corner_radius=12)
            warning_frame.pack(fill="x", padx=30, pady=(0, 10))
            
            ctk.CTkLabel(
                warning_frame,
                text="⚠️ تحذير: هذا الإجراء لا يمكن التراجع عنه!",
                font=("Arial", 14, "bold"),
                text_color=("#856404", "#fff3cd")
            ).pack(pady=10)

            ctk.CTkLabel(
                main_frame,
                text="هل أنت متأكد من حذف الأداة:",
                font=("Arial", 14),
                justify="center"
            ).pack(pady=(15, 5))

            ctk.CTkLabel(
                main_frame,
                text=tool_name_en,
                font=("Arial", 16, "bold"),
                text_color=("#c0392b", "#e74c3c"),
                justify="center"
            ).pack(pady=(0, 25))

            def perform_delete():
                try:
                    tools_data = self.data_manager.load_tools()
                    deleted = False
                    target_tool = None

                    if isinstance(tools_data, dict):
                        if tool_name_en in tools_data:
                            target_tool = tools_data[tool_name_en]
                            del tools_data[tool_name_en]
                            deleted = True
                    elif isinstance(tools_data, list):
                        # نحاول نحصل على كود الأداة الفعلي من البيانات الحالية
                        target_tool = next((t for t in tools_data if t.get("name_en") == tool_name_en), None)
                        if target_tool:
                            target_code = self.get_final_code(target_tool) if hasattr(self, "get_final_code") else target_tool.get("code", "")
                            # نحذف بناءً على الكود وليس الاسم فقط
                            new_data = [
                                t for t in tools_data
                                if (self.get_final_code(t) if hasattr(self, "get_final_code") else t.get("code", "")) != target_code
                            ]
                            if len(new_data) < len(tools_data):
                                tools_data = new_data
                                deleted = True

                    if deleted:
                        # ✅ حذف من الملف المحلي
                        self.data_manager.save_tools(tools_data)

                        #self.show_toast("✅ تم حذف الأداة محليًا بنجاح", "success")

                        # ✅ حذف من Google Sheets أيضًا (لو الـ SyncManager متاح)
                        try:
                            if hasattr(self, "sync_manager") and self.sync_manager and target_tool:
                                final_code = self.get_final_code(target_tool)
                                threading.Thread(
                                    target=lambda: self.sync_manager.delete_product_from_sheet(final_code),
                                    daemon=True
                                ).start()
                                #self.show_toast(f"🗑️ جارٍ حذف الأداة من Google Sheets ({final_code})", "success")
                                #print(f"🗑️ جارٍ حذف الأداة من Google Sheets ({final_code})")
                                
                                
                                user = getattr(self, "logged_in_user", None) or getattr(SyncManager, "logged_in_user", None)
                                self.history.log_action(
                                    user = user, 
                                    action="حذف منتج", 
                                    item=final_code,
                                    details=None,
                                    status="✅ Success"
                                )
                                
                            else:
                                self.show_toast(f"⚠️ database بعد،. ({final_code})", "warning")                               
                                print("⚠️ لم يتم تهيئة SyncManager بعد، لن يتم حذف الأداة من Google Sheets.")
                        except Exception as e:
                            print(f"⚠️ خطأ أثناء حذف الأداة من Google Sheets: {e}")

                        # ✅ تحديث الواجهة بعد الحذف
                        self.update_products_list()

                    else:
                        self.show_toast("❌ لم يتم العثور على الأداة", "warning")
                        
                        user = getattr(self, "logged_in_user", None) or getattr(SyncManager, "logged_in_user", None)
                        self.history.log_action(
                            user = user, 
                            action="حذف منتج", 
                            item=final_code,
                            details=None,
                        status="❌ [Failed] "
                        )

                except Exception as e:
                    self.show_toast(f"⚠️ خطأ أثناء الحذف: {str(e)}", "error")
                finally:
                    dialog.destroy()


            # إطار الأزرار
            buttons_container = ctk.CTkFrame(main_frame, fg_color="transparent")
            buttons_container.pack(pady=(0, 20))

            ctk.CTkButton(
                buttons_container,
                text="🗑️ نعم، احذف نهائياً",
                fg_color="#c0392b",
                hover_color="#a93226",
                command=perform_delete,
                width=180,
                height=48,
                corner_radius=10,
                font=("Arial", 14, "bold")
            ).pack(side="left", padx=8, expand=True)

            ctk.CTkButton(
                buttons_container,
                text="❌ إلغاء",
                fg_color="#7f8c8d",
                hover_color="#566573",
                command=dialog.destroy,
                width=180,
                height=48,
                corner_radius=10,
                font=("Arial", 14, "bold")
            ).pack(side="left", padx=8, expand=True)

        # أزرار النافذة الأولى
        ctk.CTkButton(
            buttons_frame,
            text="✅ تأكيد",
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=verify_and_delete,
            width=140,
            height=45,
            corner_radius=8,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=8, expand=True)

        ctk.CTkButton(
            buttons_frame,
            text="❌ إلغاء",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=password_window.destroy,
            width=140,
            height=45,
            corner_radius=8,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=8, expand=True)

        password_entry.bind("<Return>", lambda e: verify_and_delete())
    
    def toggle_saved_lists(self):
        """إظهار أو إخفاء القوائم المحفوظة بشكل أنيق"""
        if self.sidebar_visible:
            self.lists_frame.pack_forget()
            self.sidebar_visible = False
        else:
            self.lists_frame.pack(side="left", fill="both", padx=(10, 5), pady=10, expand=True)
            self.sidebar_visible = True

            # لو أول مرة يتفتح، نبني الواجهة
            if not hasattr(self, "saved_lists_frame"):
                self.create_lists_ui()
            else:
                # لو موجودة، نعمل تحديث للمحتوى
                self.update_saved_lists_ui()

    @staticmethod

    def safe_window_action(window, func, *args, **kwargs):
        """ينفذ دالة فقط لو النافذة لسه موجودة"""
        try:
            if window and window.winfo_exists():
                func(*args, **kwargs)
        except Exception:
            pass

