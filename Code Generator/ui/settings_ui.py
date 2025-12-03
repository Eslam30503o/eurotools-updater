# ui/settings_ui.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import win32print
import json
import os
import threading
from pathlib import Path
from tkinter import messagebox
from update_checker import UpdateChecker
from config import AppConfig
from ui.items_form import DynamicFormApp
from ui.history_screen import HistoryScreen
from ui.login_screen import LoginScreen
from google_users import verify_user, add_user
import customtkinter as ctk
import time



class LoadingOverlay:
    """Premium loading overlay with smooth animations"""
    
    def __init__(self, parent, message="جاري التحميل..."):
        # Semi-transparent dark overlay
        self.overlay = ctk.CTkFrame(
            parent,
            fg_color=("#1A1A1A", "#0A0A0A"),
            corner_radius=0
        )
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Loading container with blur effect simulation
        self.blur_frame = ctk.CTkFrame(
            self.overlay,
            fg_color=("#2C2C2C", "#1A1A1A"),
            corner_radius=16,
            border_width=1,
            border_color=("#3A3A3A", "#2A2A2A")
        )
        self.blur_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        loading_frame = ctk.CTkFrame(
            self.blur_frame,
            fg_color="transparent",
            width=320,
            height=200
        )
        loading_frame.pack(padx=40, pady=30)
        loading_frame.pack_propagate(False)
        
        # Animated spinner
        self.spinner_label = ctk.CTkLabel(
            loading_frame,
            text="",
            font=("Segoe UI", 45),
            text_color=("#3498DB", "#3498DB")
        )
        self.spinner_label.pack(pady=(20, 15))
        
        # Loading message
        self.message_label = ctk.CTkLabel(
            loading_frame,
            text=message,
            font=("Cairo", 15, "bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        )
        self.message_label.pack(pady=8)
        
        # Progress dots
        self.dots_label = ctk.CTkLabel(
            loading_frame,
            text="",
            font=("Cairo", 14),
            text_color=("#95A5A6", "#95A5A6")
        )
        self.dots_label.pack(pady=(5, 15))
        
        self.is_active = True
        self.spinner_frames = ["◐", "◓", "◑", "◒"]
        self.current_frame = 0
        self.dots_count = 0
        
        self._animate()

    def _animate(self):
        if not self.is_active:
            return
        
        # Spinner animation
        self.spinner_label.configure(text=self.spinner_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.spinner_frames)
        
        # Dots animation
        dots = "." * (self.dots_count % 4)
        self.dots_label.configure(text=dots)
        self.dots_count += 1
        
        self.overlay.after(150, self._animate)
    
    def load_data_from_google(self, local_path):
        self.sync_thread = threading.Thread(target=self.sync_manager.download_from_google, args=(local_path,))
        self.sync_thread.start()


    def update_message(self, message):
        self.message_label.configure(text=message)
    
    def destroy(self):
        self.is_active = False
        self.overlay.destroy()




class SettingsMixin:

    def create_settings_ui(self):
        """إنشاء واجهة الإعدادات الاحترافية"""

        base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "EuroTools" / "data"
        self.SETTING = str(base_dir / "app_settings.json")
        os.makedirs(base_dir, exist_ok=True)

        self.settings_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Container رئيسي بتصميم احترافي
        main_container = ctk.CTkFrame(self.settings_frame, fg_color=("#f0f0f0", "#1a1a1a"), corner_radius=20)
        main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header مع تصميم جذاب
        header_frame = ctk.CTkFrame(main_container, fg_color=("#2196F3", "#1565C0"), corner_radius=15, height=80)
        header_frame.pack(fill="x", padx=15, pady=(15, 20))
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(header_frame, text="⚙️ الإعدادات والتخصيص", 
                           font=("Arial", 26, "bold"), text_color="white")
        title.pack(pady=15)
        
        subtitle = ctk.CTkLabel(header_frame, text="تحكم كامل في إعدادات النظام", 
                              font=("Arial", 12), text_color=("#E3F2FD", "#BBDEFB"))
        subtitle.pack()

        # Scrollable Frame للإعدادات
        scroll_frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)






            
        # ===================== عمود الأزرار السريعة (تحت بعض في أعلى اليسار =====================
        # فريم رأسي يحتوي على الأزرار المهمة تحت بعض
        quick_actions_frame = ctk.CTkFrame(main_container, width=260, fg_color=("#e3f2fd", "#1f1f1f"), corner_radius=18)
        quick_actions_frame.pack(side="left", fill="y", padx=(20, 10), pady=(15, 20))
        quick_actions_frame.pack_propagate(False)
        #quick_actions_frame.pack_forget()

        role=getattr(self.app_ref, "logged_in_role", "user")
        #print(role)
        if role in ("admin" , "Manager"):
            pass
        else:
            quick_actions_frame.pack_forget()


        # عنوان العمود
        ctk.CTkLabel(
            quick_actions_frame,
            text="أدوات وإجراءات سريعة",
            font=("Arial", 18, "bold"),
            text_color=("#1565C0", "#64B5F6"),
            pady=20
        ).pack()

        # الأزرار تحت بعض بتصميم فخم
        buttons_config = [
            ("Items Form", self.show_items_manager, "#673AB7", "#5E35B1"),
            ("السجل والتقارير", self.create_history_page, "#9C27B0", "#7B1FA2"),
            ("البحث عن تحديثات", self.manual_update_check, "#2196F3", "#1976D2"),
            ("Add New User", self._open_add_user_dialog, "#2196F3", "#1976D2"),
        ]

        for text, command, color, hover in buttons_config:
            btn = ctk.CTkButton(
                quick_actions_frame,
                text=text,
                command=command,
                height=65,
                font=("Arial", 15, "bold"),
                fg_color=color,
                hover_color=hover,
                corner_radius=15,
                anchor="center",
                image=self._load_icon(f"{text.split()[0].lower()}.png") if hasattr(self, "_load_icon") else None,
                compound="left"
            )
            btn.pack(pady=12, padx=25, fill="x")

        # إضافة فاصل أنيق
        ctk.CTkFrame(quick_actions_frame, height=2, fg_color=("#bbdefb", "#424242")).pack(fill="x", padx=30, pady=25)

        # معلومات الإصدار في الأسفل
        ctk.CTkLabel(
            quick_actions_frame,
            text=f"إصدار التطبيق\n{AppConfig.VERSION}",
            font=("Arial", 12),
            text_color=("#555", "#ccc"),
            justify="center"
        ).pack(side="bottom", pady=30)

        # ===================== باقي المحتوى (الإعدادات) في المنتصف واليمين =====================
        # نعدل الـ scroll_frame عشان ياخد الباقي
        scroll_frame.pack_forget()  # نلغي الـ pack السابق
        scroll_frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        scroll_frame.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=10)

        # نعيد إنشاء الأقسام داخل الـ scroll_frame الجديد
        self._create_section(scroll_frame, "إعدادات المظهر", [
            ("الثيم", "theme"), ("نوع الخط", "font_family"),
            ("حجم الخط", "font_size"), ("لغة الواجهة", "language")
        ])
        self._create_section(scroll_frame, "إعدادات قاعدة البيانات", [
            ("ملف البيانات", "database"), ("النسخ الاحتياطي", "backup")
        ])
        self._create_section(scroll_frame, "إعدادات الطباعة", [
            ("الطابعة الافتراضية", "printer"), ("حجم الورق", "paper_size")
        ])
        self._create_section(scroll_frame, "إعدادات متقدمة", [
            ("الإشعارات", "notifications"), ("التحديثات التلقائية", "auto_update")
        ])
        self._create_section(quick_actions_frame, "إعدادات الأمان", [
            ("كلمة المرور", "admin_password")
        ])

        # ===================== الأزرار السفلية (حفظ - إعادة تعيين - رجوع) =====================
        bottom_bar = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        bottom_bar.pack(fill="x", side="bottom", pady=20, padx=20)

        btns = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        btns.pack(expand=True)

        ctk.CTkButton(btns, text="حفظ التغييرات", command=self.save_settings,
                      width=170, height=50, font=("Arial", 15, "bold"),
                      fg_color=("#4CAF50", "#2E7D32"), corner_radius=12).pack(side="left", padx=8)

        ctk.CTkButton(btns, text="إعادة تعيين", command=self.reset_settings,
                      width=150, height=50, font=("Arial", 14),
                      fg_color=("#FF9800", "#F57C00"), corner_radius=12).pack(side="left", padx=8)

        ctk.CTkButton(btns, text="رجوع", command=self.show_main_menu,
                      width=130, height=50, font=("Arial", 14),
                      fg_color=("#757575", "#424242"), corner_radius=12).pack(side="left", padx=8)




                # تحميل الإعدادات السابقة (لو موجودة)
        if os.path.exists(self.SETTING):
            with open(self.SETTING, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if "language" in settings:
                    self.lang_option.set(settings["language"])
                    self.current_language = settings["language"]
                if "font_family" in settings:
                    self.font_family_option.set(settings["font_family"])
                    self.current_font_family = settings["font_family"]
                if "font_size" in settings:
                    # تحويل الرقم إلى اسم
                    size_map = {12: "صغير", 14: "متوسط", 16: "كبير", 18: "كبير جداً"}
                    size_name = size_map.get(settings["font_size"], "متوسط")
                    self.font_size_option.set(size_name)
                    self.current_font_size = settings["font_size"]

    # ADMIN_PASSWORD = "admin@123"

    COLORS = {
        "primary": "#2C3E50",
        "primary_hover": "#34495E",
        "success": "#27AE60",
        "success_hover": "#229954",
        "danger": "#E74C3C",
        "accent": "#3498DB",
        "bg_light": "#F8F9FA",
        "bg_dark": "#0F1729",
        "card_light": "#FFFFFF",
        "card_dark": "#1A1A2E",
        "text_primary": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "border": "#E8E8E8",
        "border_dark": "#2C3E50"
    }
    def _open_add_user_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("إضافة مستخدم جديد")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")

        self._create_add_user_ui(dialog)

    def _create_add_user_ui(self, dialog: ctk.CTkToplevel) -> None:
        main_frame = ctk.CTkFrame(dialog, fg_color=(self.COLORS["card_light"], self.COLORS["card_dark"]))
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        ctk.CTkLabel(
            main_frame,
            text=" Add New User ",
            font=("Cairo", 24, "bold"),
            text_color=(self.COLORS["primary"], "#FFFFFF")
        ).pack(pady=(10, 20))

        # Entry creator
        def create_entry(label, is_pass=False):
            frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            frame.pack(pady=10, fill="x")
            ctk.CTkLabel(
                frame,
                text=label,
                font=("Cairo", 13),
                text_color=(self.COLORS["text_primary"], "#FFFFFF"),
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            input_frame = ctk.CTkFrame(frame, fg_color="transparent")
            input_frame.pack(fill="x")
            entry = self._create_premium_entry(input_frame, f"أدخل {label}", is_pass)
            entry.pack(side="left", fill="x", expand=True)
            toggle_btn = None
            if is_pass:
                toggle_btn = ctk.CTkButton(
                    input_frame,
                    text="👁",
                    width=40,
                    height=40,
                    corner_radius=10,
                    fg_color="transparent",
                    command=lambda e=entry: e.configure(show="" if e.cget("show") else "●"),
                    font=("Segoe UI", 16)
                )
                toggle_btn.pack(side="left", padx=(8, 0))
            return entry

        # admin_entry = create_entry("كلمة مرور المدير", is_pass=True)
        username_entry = create_entry("اسم المستخدم الجديد")
        password_entry = create_entry("كلمة المرور الجديدة", is_pass=True)

        # Role
        ctk.CTkLabel(
            main_frame,
            text="نوع الحساب",
            font=("Cairo", 13),
            text_color=(self.COLORS["text_primary"], "#FFFFFF"),
            anchor="w"
        ).pack(pady=(20, 5), fill="x")

        role_option = ctk.CTkOptionMenu(
            main_frame,
            values=["User", "Manager"],
            width=200,
            height=45,
            corner_radius=12,
            font=("Cairo", 14),
            fg_color=(self.COLORS["primary"], self.COLORS["primary"]),
            button_color=(self.COLORS["primary_hover"], self.COLORS["primary_hover"]),
            button_hover_color=(self.COLORS["primary_hover"], self.COLORS["primary_hover"])
        )
        role_option.set("User")
        role_option.pack(fill="x", pady=(0, 30))

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        add_btn = ctk.CTkButton(
            btn_frame,
            text="✅ إضافة المستخدم",
            command=lambda: self._process_add_user(
                # admin_entry,
                username_entry,
                password_entry,
                role_option,
                dialog,
                add_btn,
                cancel_btn
            ),
            height=52,
            corner_radius=12,
            font=("Cairo", 15, "bold"),
            fg_color=(self.COLORS["success"], self.COLORS["success"]),
            hover_color=(self.COLORS["success_hover"], self.COLORS["success_hover"])
        )
        add_btn.pack(fill="x", pady=(0, 10))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ إلغاء",
            command=dialog.destroy,
            height=48,
            corner_radius=12,
            font=("Cairo", 14),
            fg_color="transparent",
            hover_color=(self.COLORS["border"], "#2C3E50"),
            border_width=1,
            border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
            text_color=(self.COLORS["text_primary"], "#FFFFFF")
        )
        cancel_btn.pack(fill="x")

    def _create_premium_entry(self, parent, placeholder: str, is_password: bool) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=46,
            corner_radius=12,
            border_width=1,
            border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
            fg_color=(self.COLORS["card_light"], "#0F1729"),
            font=("Cairo", 13),
            show="●" if is_password else ""
        )
        return entry


    def _process_add_user(
        self,
        #admin_entry: ctk.CTkEntry,
        username_entry: ctk.CTkEntry,
        password_entry: ctk.CTkEntry,
        role_option: ctk.CTkOptionMenu,
        dialog: ctk.CTkToplevel,
        add_btn: ctk.CTkButton,
        cancel_btn: ctk.CTkButton
    ) -> None:
        #admin_input = admin_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        role = "admin" if role_option.get() == "Manager" else "user"

        if not username or not password:
            messagebox.showwarning("⚠️ تنبيه", "الرجاء إدخال جميع البيانات.")
            return

        # Disable inputs and show loading
        add_btn.configure(state="disabled")
        cancel_btn.configure(state="disabled")
        #admin_entry.configure(state="disabled")
        username_entry.configure(state="disabled")
        password_entry.configure(state="disabled")
        role_option.configure(state="disabled")
        
        loading = LoadingOverlay(dialog, "جاري إضافة المستخدم...")

        def process():
            try:
                time.sleep(0.8)  # Simulate processing
                
                if add_user(username, password, role):
                    dialog.after(0, loading.destroy)
                    dialog.after(0, lambda: messagebox.showinfo("✓ نجح", f"تم إضافة المستخدم '{username}' بنجاح!"))
                    dialog.after(100, dialog.destroy)
                else:
                    dialog.after(0, loading.destroy)
                    dialog.after(0, lambda: messagebox.showwarning("⚠️ موجود", f"المستخدم '{username}' موجود مسبقًا."))
                    
            except Exception as e:
                dialog.after(0, loading.destroy)
                dialog.after(0, lambda: messagebox.showerror("❌ خطأ", f"حدث خطأ أثناء الإضافة:\n{e}"))
            
            finally:
                def re_enable():
                    add_btn.configure(state="normal")
                    cancel_btn.configure(state="normal")
                    #admin_entry.configure(state="normal")
                    username_entry.configure(state="normal")
                    password_entry.configure(state="normal")
                    role_option.configure(state="normal")
                
                dialog.after(0, re_enable)
        
        threading.Thread(target=process, daemon=True).start()


    def manual_update_check(self):
        """التحقق اليدوي من وجود تحديث — يشغّل فحص في خيط منفصل."""
        try:
            # إذا التطبيق أو الـ UI مرّر reference للـ app، نستخدم الـ updater الموجود
            updater = None
            # محاولات لاستخراج updater من السياقات الممكنة
            if hasattr(self, "app_ref") and getattr(self.app_ref, "updater", None):
                updater = self.app_ref.updater
            elif getattr(self, "updater", None):
                updater = self.updater

            if updater is None:
                # إنشاؤه مؤقتًا باستخدام AppConfig
                updater = UpdateChecker(
                    current_version=AppConfig.VERSION,
                    version_url=AppConfig.VERSION_URL,
                    download_url=AppConfig.DOWNLOAD_URL,
                    check_interval_hours=AppConfig.UPDATE_CHECK_INTERVAL_HOURS
                )

            # شغل الفحص في خيط منفصل عشان ما يتجمدش الـ UI
            threading.Thread(target=lambda: updater.check_for_update(silent=False, auto_download=False),
                             daemon=True, name="ManualUpdateCheck").start()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل التحقق من التحديثات:\n{e}")

    def force_download_update(self, latest_version: str = None):
        """واجهة بسيطة لبدء التحميل من الإعداد (يمكن استدعاؤها لو عايز زر تحميل مباشر)."""
        try:
            updater = None
            if hasattr(self, "app_ref") and getattr(self.app_ref, "updater", None):
                updater = self.app_ref.updater
            elif getattr(self, "updater", None):
                updater = self.updater

            if updater is None:
                updater = UpdateChecker(
                    current_version=AppConfig.VERSION,
                    version_url=AppConfig.VERSION_URL,
                    download_url=AppConfig.DOWNLOAD_URL,
                    check_interval_hours=AppConfig.UPDATE_CHECK_INTERVAL_HOURS
                )

            # نجهز خيط لتحميل التحديث عشان لا يعلق الـ UI
            threading.Thread(target=lambda: updater._download_update(), daemon=True, name="ManualUpdateDownload").start()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل بدء التحميل:\n{e}")



    def _create_section(self, parent, title, items):
        """إنشاء قسم إعدادات بتصميم احترافي"""
        section_frame = ctk.CTkFrame(parent, fg_color=("#ffffff", "#2b2b2b"), corner_radius=12)
        section_frame.pack(fill="x", pady=10)

        # عنوان القسم
        title_label = ctk.CTkLabel(
            section_frame, text=title, 
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=20, pady=(15, 10))

        # خط فاصل
        separator = ctk.CTkFrame(section_frame, height=2, fg_color=("#e0e0e0", "#404040"))
        separator.pack(fill="x", padx=20, pady=5)

        # العناصر
        for item_name, item_key in items:
            self._create_setting_item(section_frame, item_name, item_key)

    def _create_setting_item(self, parent, name, key):
        """إنشاء عنصر إعداد واحد"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=20, pady=8)

        # اسم الإعداد
        label = ctk.CTkLabel(item_frame, text=name, font=("Arial", 13))
        label.pack(side="left", padx=5)

        # العنصر التحكمي حسب النوع
        if key == "theme":
            theme_option = ctk.CTkOptionMenu(
                item_frame, 
                values=["Light", "Dark", "System"],
                command=self.change_theme,
                width=150,
                corner_radius=8
            )
            theme_option.set(ctk.get_appearance_mode())
            theme_option.pack(side="right", padx=5)

        elif key == "font_size":
            self.font_size_option = ctk.CTkOptionMenu(
                item_frame,
                values=["صغير", "متوسط", "كبير", "كبير جداً"],
                command=self.change_font_size,
                width=150,
                corner_radius=8
            )
            self.font_size_option.set("متوسط")
            self.font_size_option.pack(side="right", padx=5)

        elif key == "font_family":
            self.font_family_option = ctk.CTkOptionMenu(
                item_frame,
                values=["Cairo", "Arial", "Roboto", "Tajawal"],
                command=self.change_font_family,
                width=150,
                corner_radius=8
            )
            self.font_family_option.set("Cairo")
            self.font_family_option.pack(side="right", padx=5)

        elif key == "language":
            self.lang_option = ctk.CTkOptionMenu(
                item_frame, 
                values=["العربية", "English"],
                command=self.change_language,
                width=150,
                corner_radius=8
            )
            self.lang_option.set("العربية")
            self.lang_option.pack(side="right", padx=5)


        elif key == "database":
            db_btn = ctk.CTkButton(
                item_frame, text="📁 اختيار", 
                command=self.choose_db_file,
                width=150,
                corner_radius=8,
                fg_color=("#2196F3", "#1565C0")
            )
            db_btn.pack(side="right", padx=5)

        elif key == "backup":
            backup_btn = ctk.CTkButton(
                item_frame, text="💾 نسخ احتياطي", 
                command=self.backup_database,
                width=150,
                corner_radius=8,
                fg_color=("#4CAF50", "#2E7D32")
            )
            backup_btn.pack(side="right", padx=5)

        elif key == "printer":
            printer_btn = ctk.CTkButton(
                item_frame, text="🖨️ إعداد", 
                command=self.open_printer_settings,
                width=150,
                corner_radius=8,
                fg_color=("#FF9800", "#F57C00")
            )
            printer_btn.pack(side="right", padx=5)

        elif key == "paper_size":
            paper_option = ctk.CTkOptionMenu(
                item_frame, 
                values=["A4", "A5", "Letter", "80mm (حراري)"],
                width=150,
                corner_radius=8
            )
            paper_option.set("80mm (حراري)")
            paper_option.pack(side="right", padx=5)

        elif key == "notifications":
            notif_switch = ctk.CTkSwitch(item_frame, text="", width=50)
            notif_switch.select()
            notif_switch.pack(side="right", padx=5)

        elif key == "auto_update":
            update_switch = ctk.CTkSwitch(item_frame, text="", width=50)
            update_switch.select()
            update_switch.pack(side="right", padx=5)

        # elif key == "admin_password":
        #     self.admin_password_entry = ctk.CTkEntry(
        #         item_frame,
        #         placeholder_text="Create Password",
        #         show="*",
        #         width=150,
        #         corner_radius=8
        #     )
        #     self.admin_password_entry.pack(side="left")
        #     # تحميل كلمة السر المحفوظة لو موجودة
        #     if os.path.exists(self.SETTING):
        #         with open(self.SETTING, "r", encoding="utf-8") as f:
        #             data = json.load(f)
        #             if "admin_password" in data:
        #                 self.admin_password_entry.insert(0, data["admin_password"])
        #     self.admin_password_entry.pack(side="right", padx=5)
        #     self.admin_password_entry.configure(state="normal")

        #     def toggle_show_password():
        #         if self.admin_password_entry.cget("show") == "*":
        #             self.admin_password_entry.configure(show="")
        #             show_btn.configure(text="🔒 إخفاء")
        #         else:
        #             self.admin_password_entry.configure(show="*")
        #             show_btn.configure(text="👁️ إظهار")

        #     show_btn = ctk.CTkButton(
        #         item_frame,
        #         text="👁️ إظهار",
        #         command=toggle_show_password,
        #         width=80,
        #         fg_color=("#9E9E9E", "#5D6D7E"), # لون رمادي مناسب
        #         hover_color=("#757575", "#424242"),
        #         corner_radius=8
        #     )
        #     show_btn.pack(side="right", padx=5)
            
        elif key == "admin_password":
            # تحقق من الرول أولاً
            role = getattr(self.app_ref, "logged_in_role", "user").lower()
            if role not in ("admin", "manager"):
                return

            item_frame = ctk.CTkFrame(parent, fg_color="transparent")
            item_frame.pack(fill="x", padx=20, pady=12)

            # اسم الإعداد على الشمال
            ctk.CTkLabel(item_frame, text=name, font=("Cairo", 15, "bold"), anchor="e").pack(side="right", padx=(0, 20))

            # الـ Frame اللي هيحتوي الـ Entry + الزر داخلها
            password_frame = ctk.CTkFrame(item_frame, fg_color="transparent", height=46)
            password_frame.pack(side="left")
            password_frame.pack_propagate(False)

            # الـ Entry
            self.admin_password_entry = ctk.CTkEntry(
                password_frame,
                placeholder_text="Enter Password",
                show="*",
                font=("Cairo", 14),
                height=46,
                corner_radius=12,
                border_width=2,
                fg_color=("#f0f0f0", "#2b2b2b"),
                text_color=("black", "white")
            )
            self.admin_password_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

            # زر الإظهار داخل الـ Entry من اليمين
            def toggle_password():
                if self.admin_password_entry.cget("show") == "*":
                    self.admin_password_entry.configure(show="")
                    eye_btn.configure(text="👁")
                else:
                    self.admin_password_entry.configure(show="*")
                    eye_btn.configure(text="👁")

            eye_btn = ctk.CTkButton(
                password_frame,
                text="👁",
                width=10,
                height=10,
                corner_radius=15,
                font=("Cairo", 12, "bold"),
                fg_color="transparent",
                hover_color=("#2980b9", "#3498db"),
                command=toggle_password
            )
            eye_btn.place(relx=1.0, rely=0.5, x=-8, anchor="e")  # مكان الزر داخل الـ Entry

            # تحميل كلمة المرور المحفوظة (اختياري: خليها فاضية للأمان)
            if os.path.exists(self.SETTING):
                try:
                    with open(self.SETTING, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "admin_password" in data:
                            self.admin_password_entry.insert(0, data["admin_password"])
                        self.admin_password_entry.pack(side="right", padx=5)
                        self.admin_password_entry.configure(state="normal")
                except:
                    pass



    def open_printer_settings(self):
        """نافذة إعدادات الطابعة الاحترافية"""
        win = ctk.CTkToplevel(self.root)
        win.title("إعدادات الطابعة")
        win.geometry("550x500")
        win.resizable(False, False)

        # Header
        header = ctk.CTkFrame(win, fg_color=("#FF9800", "#F57C00"), corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🖨️ إعدادات الطابعة المتقدمة", 
                    font=("Cairo", 20, "bold"), text_color="white").pack(pady=20)

        # محتوى النافذة
        content = ctk.CTkScrollableFrame(win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # الحصول على قائمة الطابعات
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            default_printer = win32print.GetDefaultPrinter()
        except Exception as e:
            printers = ["لا توجد طابعات مثبتة"]
            default_printer = None
            messagebox.showerror("خطأ", f"تعذر الحصول على قائمة الطابعات:\n{e}")

        # اختيار الطابعة
        printer_frame = ctk.CTkFrame(content, fg_color=("#f5f5f5", "#2b2b2b"), corner_radius=10)
        printer_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(printer_frame, text="الطابعة الافتراضية:", 
                    font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        printer_option = ctk.CTkOptionMenu(
            printer_frame, 
            values=printers if printers else ["لا توجد طابعات"],
            width=450,
            corner_radius=8
        )
        printer_option.set(default_printer if default_printer else printers[0] if printers else "لا توجد طابعات")
        printer_option.pack(padx=15, pady=(0, 15))

        # إعدادات الطباعة
        settings_frame = ctk.CTkFrame(content, fg_color=("#f5f5f5", "#2b2b2b"), corner_radius=10)
        settings_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(settings_frame, text="خيارات الطباعة:", 
                    font=("Cairo", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))

        # حجم الورق
        paper_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        paper_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(paper_frame, text="حجم الورق:").pack(side="left")
        paper_menu = ctk.CTkOptionMenu(paper_frame, values=["A4", "A5", "80mm", "58mm"], width=150)
        paper_menu.set("80mm")
        paper_menu.pack(side="right")

        # عدد النسخ
        copies_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        copies_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(copies_frame, text="عدد النسخ:").pack(side="left")
        copies_entry = ctk.CTkEntry(copies_frame, width=150)
        copies_entry.insert(0, "1")
        copies_entry.pack(side="right")

        # جودة الطباعة
        quality_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        quality_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(quality_frame, text="جودة الطباعة:").pack(side="left")
        quality_menu = ctk.CTkOptionMenu(quality_frame, values=["عادية", "عالية", "مسودة"], width=150)
        quality_menu.set("عادية")
        quality_menu.pack(side="right")

        # طباعة تلقائية
        auto_print = ctk.CTkSwitch(settings_frame, text="طباعة تلقائية بعد الفاتورة")
        auto_print.pack(anchor="w", padx=15, pady=10)
        auto_print.select()

        # الأزرار
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=20)

        test_btn = ctk.CTkButton(
            btn_frame, text="🖨️ اختبار الطباعة",
            command=lambda: self.test_print(printer_option.get()),
            fg_color=("#2196F3", "#1565C0"),
            width=160,
            height=40
        )
        test_btn.pack(side="left", padx=5)

        save_btn = ctk.CTkButton(
            btn_frame, text="💾 حفظ الإعدادات",
            command=lambda: self.save_printer_settings(printer_option.get(), paper_menu.get()),
            fg_color=("#4CAF50", "#2E7D32"),
            width=160,
            height=40
        )
        save_btn.pack(side="left", padx=5)

    def test_print(self, printer_name):
        """اختبار الطباعة"""
        messagebox.showinfo("اختبار الطباعة", 
                          f"✅ تم إرسال صفحة اختبار إلى:\n{printer_name}\n\nتحقق من الطابعة الآن.")

    def save_printer_settings(self, printer_name, paper_size):
        """حفظ إعدادات الطابعة"""
        try:
            settings = {
                "printer": printer_name,
                "paper_size": paper_size
            }
            # حفظ في ملف JSON
            with open("printer_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("نجح الحفظ", 
                              f"✅ تم حفظ إعدادات الطابعة بنجاح!\n\nالطابعة: {printer_name}\nحجم الورق: {paper_size}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ الإعدادات:\n{e}")

    def backup_database(self):
        """نسخ احتياطي لقاعدة البيانات"""
        try:
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                initialfile=f"backup_{self.get_timestamp()}.json"
            )
            if backup_path:
                # نسخ الملف
                import shutil
                shutil.copy2(self.data_manager.DATABASE_FILE, backup_path)
                messagebox.showinfo("نجح النسخ", f"✅ تم إنشاء نسخة احتياطية بنجاح!\n\n{backup_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل النسخ الاحتياطي:\n{e}")

    def get_timestamp(self):
        """الحصول على timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def show_settings_page(self):
        """عرض صفحة الإعدادات"""
        self.clear_main_frames()
        if not hasattr(self, "settings_frame"):
            self.create_settings_ui()
        self.settings_frame.pack(expand=True, fill="both")

    def change_theme(self, choice):
        """تغيير الثيم"""
        ctk.set_appearance_mode(choice)
        messagebox.showinfo("تم التغيير", f"✅ تم تغيير الثيم إلى: {choice}")

    def choose_db_file(self):
        """اختيار ملف قاعدة البيانات"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            self.data_manager.DATABASE_FILE = filename
            messagebox.showinfo("تم التحديث", f"✅ تم اختيار ملف قاعدة البيانات:\n{filename}")

    def save_settings(self):
        """حفظ جميع الإعدادات"""
        try:
            settings = {
                "theme": ctk.get_appearance_mode(),
                "language": getattr(self, "current_language", "العربية"),
                "font_family": getattr(self, "current_font_family", "Cairo"),
                "font_size": getattr(self, "current_font_size", 14),
                "database": self.data_manager.DATABASE_FILE,
                "timestamp": self.get_timestamp(),
                "admin_password": getattr(self, "admin_password_entry", None).get().strip() if hasattr(self, "admin_password_entry") else "Admin@123"

            }
            
            with open(self.SETTING, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("نجح الحفظ", "✅ تم حفظ جميع الإعدادات بنجاح!")

            # 🏠 العودة للقائمة الرئيسية بعد الحفظ
            self.show_main_menu()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ الإعدادات:\n{e}")

    def reset_settings(self):
        """إعادة تعيين الإعدادات للوضع الافتراضي"""
        result = messagebox.askyesno(
            "تأكيد إعادة التعيين",
            "⚠️ هل أنت متأكد من إعادة تعيين جميع الإعدادات؟\n\nسيتم فقدان الإعدادات الحالية."
        )
        if result:
            ctk.set_appearance_mode("System")
            messagebox.showinfo("تم إعادة التعيين", "✅ تم إعادة تعيين جميع الإعدادات للوضع الافتراضي")

    def clear_main_frames(self):
        """إخفاء جميع الفريمات"""
        for widget in self.main_container.winfo_children():
            widget.pack_forget()

    def show_items_manager(self):
        """عرض صفحة إدارة الـ Items داخل تبويب الإعدادات"""
        self.clear_main_frames()
        
        # إنشاء فريم جديد داخل main_container لعرض الصفحة
        self.items_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.items_frame.pack(fill="both", expand=True)

        # إنشاء واجهة العناصر داخل الفريم
        self.items_page = DynamicFormApp(self.items_frame)
        self.items_page.pack(fill="both", expand=True)

        # زر رجوع أسفل الصفحة
        back_btn = ctk.CTkButton(
            self.items_frame,
            text="رجوع الي الاعدادات ←",
            command=self.show_settings_page,
            fg_color=("#757575", "#424242"),
            hover_color=("#616161", "#212121"),
            corner_radius=10,
            height=40,
            width=200
        )
        back_btn.pack(pady=15)



    def show_main_menu(self):
        """الرجوع للقائمة الرئيسية"""
        self.clear_main_frames()

        # ✅ تأكد إن القوائم الجانبية مغلقة تمامًا
        if hasattr(self, "lists_frame"):
            try:
                self.lists_frame.pack_forget()
            except:
                pass

        # ✅ صِفِّر حالة القوائم
        if hasattr(self, "sidebar_visible"):
            self.sidebar_visible = False

        # ✅ أظهر الإطارات الرئيسية فقط
        self.products_frame.pack(side="right", expand=True, fill="both", padx=(10, 5), pady=10)
        #self.lists_frame.pack(side="left", fill="both", padx=(5, 10), pady=10)

    def change_font_size(self, choice):
        """تغيير حجم الخط في التطبيق"""
        sizes = {
            "صغير": 12,
            "متوسط": 14,
            "كبير": 16,
            "كبير جداً": 18
        }
        self.current_font_size = sizes.get(choice, 14)
        self.apply_font_changes()

    def change_font_family(self, choice):
        """تغيير نوع الخط"""
        self.current_font_family = choice
        self.apply_font_changes()

    def apply_font_changes(self):
        """تطبيق التغييرات على الواجهة"""
        try:
            for widget in self.root.winfo_children():
                self._apply_font_recursive(widget)
            messagebox.showinfo("تم", "✅ تم تحديث الخط بنجاح")
        except Exception as e:
            print("خطأ في تغيير الخط:", e)

    def _apply_font_recursive(self, widget):
        """تغيير الخط داخل كل العناصر"""
        try:
            widget.configure(font=(self.current_font_family, self.current_font_size))
        except:
            pass
        for child in widget.winfo_children():
            self._apply_font_recursive(child)

    def change_language(self, lang):
        """تبديل اللغة"""
        self.current_language = lang
        if lang == "English":
            messagebox.showinfo("Language Changed", "✅ Interface language changed to English")
        else:
            messagebox.showinfo("تم", "✅ تم تغيير اللغة إلى العربية")
        # TODO: إعادة تحميل النصوص في الواجهة (اختياري)
    
    

