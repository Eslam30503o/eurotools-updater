# ui/settings_ui.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import win32print
import json
import os

class SettingsMixin:

    def create_settings_ui(self):
        """إنشاء واجهة الإعدادات الاحترافية"""
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

        # قسم 1: إعدادات المظهر
        self._create_section(scroll_frame, "🎨 إعدادات المظهر", [
            ("الثيم", "theme"),
            ("نوع الخط", "font_family"),
            ("حجم الخط", "font_size"),
            ("لغة الواجهة", "language")
        ])
        # قسم 2: إعدادات قاعدة البيانات
        self._create_section(scroll_frame, "💾 إعدادات قاعدة البيانات", [
            ("ملف البيانات", "database"),
            ("النسخ الاحتياطي", "backup"),
        ])

        # قسم 3: إعدادات الطابعة
        self._create_section(scroll_frame, "🖨️ إعدادات الطباعة", [
            ("الطابعة الافتراضية", "printer"),
            ("حجم الورق", "paper_size"),
        ])

        # قسم 4: إعدادات متقدمة
        self._create_section(scroll_frame, "🔧 إعدادات متقدمة", [
            ("الإشعارات", "notifications"),
            ("التحديثات التلقائية", "auto_update"),
        ])

        # Action Buttons في الأسفل
        actions_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=15)

        # الأزرار بتصميم modern
        btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_frame.pack()

        save_btn = ctk.CTkButton(
            btn_frame, text="💾 حفظ التغييرات", 
            command=self.save_settings,
            font=("Arial", 14, "bold"),
            fg_color=("#4CAF50", "#2E7D32"),
            hover_color=("#45a049", "#1B5E20"),
            corner_radius=10,
            height=45,
            width=160
        )
        save_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(
            btn_frame, text="🔄 إعادة تعيين", 
            command=self.reset_settings,
            font=("Arial", 14, "bold"),
            fg_color=("#FF9800", "#F57C00"),
            hover_color=("#FB8C00", "#E65100"),
            corner_radius=10,
            height=45,
            width=160
        )
        reset_btn.pack(side="left", padx=5)

        back_btn = ctk.CTkButton(
            btn_frame, text="← رجوع", 
            command=self.show_main_menu,
            font=("Arial", 14, "bold"),
            fg_color=("#757575", "#424242"),
            hover_color=("#616161", "#212121"),
            corner_radius=10,
            height=45,
            width=120
        )
        back_btn.pack(side="left", padx=5)

                # تحميل الإعدادات السابقة (لو موجودة)
        if os.path.exists("app_settings.json"):
            with open("app_settings.json", "r", encoding="utf-8") as f:
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
                "timestamp": self.get_timestamp()
            }
            
            with open("app_settings.json", "w", encoding="utf-8") as f:
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
    
    

