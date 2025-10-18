import customtkinter as ctk
from tkinter import ttk, messagebox
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
matplotlib.use('Agg')  # لاستخدام matplotlib بدون واجهة رسومية
from io import BytesIO
from PIL import ImageTk, Image as PILImage

class HistoryScreen(ctk.CTkFrame):
    """
    شاشة عرض السجل الاحترافية داخل البرنامج الرئيسي EuroTools
    """
    def __init__(self, parent, ui_manager, data_dir):
        super().__init__(parent, fg_color="#0a0e27")
        self.pack(fill="both", expand=True)

        self.data_dir = data_dir
        self.creds_path = os.path.join(self.data_dir, "my-tools-sync.json")
        self.sheet_name = "My Tools Sync"
        self.history_sheet_name = "History"
        self.ui_manager = ui_manager  # ⬅️ حفظ مرجع لـ UIManager

        self.df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        self.is_loading = False
        
        # متغيرات الفلترة
        self.filter_vars = {
            'search': ctk.StringVar(),
            'date_from': ctk.StringVar(),
            'date_to': ctk.StringVar(),
            'username': ctk.StringVar(),
            'operation': ctk.StringVar(),
            'status': ctk.StringVar()
        }
        
        # متغيرات الرسم البياني
        self.chart_type = ctk.StringVar(value="bar")
        
        self.create_ui()
        self.load_data_async()

    def create_ui(self):
        """إنشاء واجهة احترافية مميزة"""
        # ═══════════════════════════════════════════════════════════
        # HEADER SECTION - شريط العنوان الفاخر
        # ═══════════════════════════════════════════════════════════
        header = ctk.CTkFrame(self, fg_color="#1a1f3a", height=120, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # عنوان رئيسي مع أيقونة
        title_container = ctk.CTkFrame(header, fg_color="transparent")
        title_container.pack(side="top", pady=(20, 5))

        icon_label = ctk.CTkLabel(
            title_container,
            text="📊",
            font=("Segoe UI Emoji", 36),
        )
        icon_label.pack(side="left", padx=(0, 10))

        title_label = ctk.CTkLabel(
            title_container,
            text="سجل العمليات",
            font=("Segoe UI", 32, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left")

        # خط فاصل متدرج
        separator = ctk.CTkFrame(header, fg_color="#00d9ff", height=3, corner_radius=0)
        separator.pack(fill="x", padx=40, pady=(5, 10))

        # معلومات إحصائية سريعة
        self.stats_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=40, pady=(0, 10))

        self.total_records_label = ctk.CTkLabel(
            self.stats_frame,
            text="📋 إجمالي السجلات: 0",
            font=("Segoe UI", 12),
            text_color="#b0b0b0"
        )
        self.total_records_label.pack(side="right", padx=10)

        self.last_update_label = ctk.CTkLabel(
            self.stats_frame,
            text="🕒 آخر تحديث: --",
            font=("Segoe UI", 12),
            text_color="#b0b0b0"
        )
        self.last_update_label.pack(side="right", padx=10)

        # ═══════════════════════════════════════════════════════════
        # TOOLBAR - شريط الأدوات العلوي
        # ═══════════════════════════════════════════════════════════
        toolbar = ctk.CTkFrame(self, fg_color="#151938", corner_radius=0)
        toolbar.pack(fill="x", padx=0, pady=0)

        toolbar_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        toolbar_inner.pack(fill="both", expand=True, padx=30, pady=15)

        # مربع البحث الفاخر
        search_container = ctk.CTkFrame(toolbar_inner, fg_color="#1e2347", corner_radius=15, height=50)
        search_container.pack(side="left", fill="x", expand=True)
        search_container.pack_propagate(False)

        search_icon = ctk.CTkLabel(
            search_container,
            text="🔍",
            font=("Segoe UI Emoji", 18),
            text_color="#00d9ff"
        )
        search_icon.pack(side="left", padx=(15, 5))

        self.search_entry = ctk.CTkEntry(
            search_container,
            textvariable=self.filter_vars['search'],
            placeholder_text="بحث عام في جميع الحقول...",
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 13),
            text_color="#ffffff",
            placeholder_text_color="#606582"
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=(5, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        # أزرار الإجراءات
        btn_container = ctk.CTkFrame(toolbar_inner, fg_color="transparent")
        btn_container.pack(side="right", padx=(15, 0))

        # زر الفلاتر المتقدمة
        self.filters_btn = ctk.CTkButton(
            btn_container,
            text="🎛️ فلاتر متقدمة",
            command=self.toggle_advanced_filters,
            width=140,
            height=45,
            corner_radius=12,
            fg_color="#f59e0b",
            hover_color="#d97706",
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold")
        )
        self.filters_btn.pack(side="left", padx=5)

        # زر الرسم البياني
        self.chart_btn = ctk.CTkButton(
            btn_container,
            text="📈 رسم بياني",
            command=self.show_chart_dialog,
            width=120,
            height=45,
            corner_radius=12,
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold")
        )
        self.chart_btn.pack(side="left", padx=5)

        self.refresh_btn = ctk.CTkButton(
            btn_container,
            text="🔄 تحديث",
            command=self.load_data_async,
            width=120,
            height=45,
            corner_radius=12,
            fg_color="#00d9ff",
            hover_color="#00b8d4",
            text_color="#0a0e27",
            font=("Segoe UI", 13, "bold")
        )
        self.refresh_btn.pack(side="left", padx=5)

        self.export_btn = ctk.CTkButton(
            btn_container,
            text="📥 تصدير",
            command=self.export_data,
            width=120,
            height=45,
            corner_radius=12,
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold")
        )
        self.export_btn.pack(side="left", padx=5)

        # ═══════════════════════════════════════════════════════════
        # ADVANCED FILTERS PANEL - لوحة الفلاتر المتقدمة
        # ═══════════════════════════════════════════════════════════
        self.filters_panel = ctk.CTkFrame(self, fg_color="#1a1f3a", corner_radius=0)
        # مخفي افتراضياً
        self.filters_visible = False

        filters_inner = ctk.CTkFrame(self.filters_panel, fg_color="transparent")
        filters_inner.pack(fill="both", expand=True, padx=30, pady=20)

        # عنوان اللوحة
        panel_title = ctk.CTkLabel(
            filters_inner,
            text="🎯 الفلاتر المتقدمة",
            font=("Segoe UI", 18, "bold"),
            text_color="#00d9ff"
        )
        panel_title.grid(row=0, column=0, columnspan=6, pady=(0, 15), sticky="w")

        # الصف الأول: التاريخ
        row1_frame = ctk.CTkFrame(filters_inner, fg_color="transparent")
        row1_frame.grid(row=1, column=0, columnspan=6, sticky="ew", pady=5)
        filters_inner.grid_columnconfigure(0, weight=1)

        # من تاريخ
        date_from_container = self.create_filter_field(
            row1_frame,
            "📅 من تاريخ",
            self.filter_vars['date_from'],
            "YYYY-MM-DD"
        )
        date_from_container.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # إلى تاريخ
        date_to_container = self.create_filter_field(
            row1_frame,
            "📅 إلى تاريخ",
            self.filter_vars['date_to'],
            "YYYY-MM-DD"
        )
        date_to_container.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # اسم المستخدم
        username_container = self.create_filter_field(
            row1_frame,
            "👤 اسم المستخدم",
            self.filter_vars['username'],
            "اختر أو اكتب..."
        )
        username_container.pack(side="left", fill="x", expand=True)

        # الصف الثاني: نوع العملية والحالة
        row2_frame = ctk.CTkFrame(filters_inner, fg_color="transparent")
        row2_frame.grid(row=2, column=0, columnspan=6, sticky="ew", pady=5)

        # نوع العملية
        operation_container = self.create_filter_field(
            row2_frame,
            "⚙️ نوع العملية",
            self.filter_vars['operation'],
            "اختر أو اكتب..."
        )
        operation_container.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # حالة العملية
        status_container = self.create_filter_field(
            row2_frame,
            "📊 حالة العملية",
            self.filter_vars['status'],
            "اختر أو اكتب..."
        )
        status_container.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # أزرار التحكم
        buttons_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        buttons_frame.pack(side="left", fill="x")

        apply_btn = ctk.CTkButton(
            buttons_frame,
            text="✓ تطبيق",
            command=self.apply_filters,
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            font=("Segoe UI", 12, "bold")
        )
        apply_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="✖ مسح الكل",
            command=self.clear_all_filters,
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#ffffff",
            font=("Segoe UI", 12, "bold")
        )
        clear_btn.pack(side="left", padx=5)

        # ═══════════════════════════════════════════════════════════
        # TABLE SECTION - جدول البيانات الاحترافي
        # ═══════════════════════════════════════════════════════════
        table_container = ctk.CTkFrame(self, fg_color="#151938", corner_radius=0)
        table_container.pack(fill="both", expand=True, padx=0, pady=0)

        # إطار الجدول مع ظل داخلي
        table_wrapper = ctk.CTkFrame(table_container, fg_color="#1e2347", corner_radius=20)
        table_wrapper.pack(fill="both", expand=True, padx=30, pady=30)

        # حالة التحميل
        self.loading_frame = ctk.CTkFrame(table_wrapper, fg_color="transparent")
        self.loading_frame.pack(fill="both", expand=True)

        loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="⏳",
            font=("Segoe UI Emoji", 48)
        )
        loading_label.pack(pady=(100, 10))

        loading_text = ctk.CTkLabel(
            self.loading_frame,
            text="جاري تحميل البيانات...",
            font=("Segoe UI", 16),
            text_color="#b0b0b0"
        )
        loading_text.pack()

        # إطار فارغ للبيانات
        self.empty_frame = ctk.CTkFrame(table_wrapper, fg_color="transparent")
        
        empty_icon = ctk.CTkLabel(
            self.empty_frame,
            text="📭",
            font=("Segoe UI Emoji", 64)
        )
        empty_icon.pack(pady=(80, 15))

        empty_text = ctk.CTkLabel(
            self.empty_frame,
            text="لا توجد بيانات مطابقة",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"
        )
        empty_text.pack(pady=(0, 5))

        empty_subtext = ctk.CTkLabel(
            self.empty_frame,
            text="جرب تعديل الفلاتر أو البحث عن شيء آخر",
            font=("Segoe UI", 13),
            text_color="#7d7d7d"
        )
        empty_subtext.pack()

        # الجدول الفعلي
        self.table_frame = ctk.CTkFrame(table_wrapper, fg_color="transparent")

        # إنشاء Treeview مع تنسيق احترافي
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Custom.Treeview",
            background="#1e2347",
            foreground="#ffffff",
            fieldbackground="#1e2347",
            borderwidth=0,
            font=("Segoe UI", 11),
            rowheight=35
        )
        
        style.configure(
            "Custom.Treeview.Heading",
            background="#2a3052",
            foreground="#00d9ff",
            borderwidth=0,
            font=("Segoe UI", 12, "bold"),
            relief="flat"
        )
        
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#343a5e")]
        )
        
        style.map(
            "Custom.Treeview",
            background=[("selected", "#00d9ff")],
            foreground=[("selected", "#0a0e27")]
        )

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=[],
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )
        self.tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)

        scrollbar_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent", width=30)
        scrollbar_frame.pack(side="right", fill="y", padx=(5, 20), pady=20)

        vsb = ttk.Scrollbar(
            scrollbar_frame,
            orient="vertical",
            command=self.tree.yview,
            style="Custom.Vertical.TScrollbar"
        )
        vsb.pack(fill="y", expand=True)
        self.tree.configure(yscrollcommand=vsb.set)

        style.configure(
            "Custom.Vertical.TScrollbar",
            background="#2a3052",
            troughcolor="#1e2347",
            borderwidth=0,
            arrowcolor="#00d9ff"
        )

        # ═══════════════════════════════════════════════════════════
        # FOOTER - معلومات القدم
        # ═══════════════════════════════════════════════════════════
        footer = ctk.CTkFrame(self, fg_color="#1a1f3a", height=50, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        footer_inner = ctk.CTkFrame(footer, fg_color="transparent")
        footer_inner.pack(fill="both", expand=True, padx=20, pady=10)

        self.footer_label = ctk.CTkLabel(
            footer_inner,
            text="💡 اضغط مرتين على أي سجل لعرض التفاصيل الكاملة",
            font=("Segoe UI", 11),
            text_color="#7d7d7d"
        )
        self.footer_label.pack(side="right")

        # زر الرجوع إلى القائمة الرئيسية
        self.back_btn = ctk.CTkButton(
            footer_inner,
            text="⬅️ رجوع",
            command=self.go_back,
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#00d9ff",
            hover_color="#00b8d4",
            text_color="#0a0e27",
            font=("Segoe UI", 12, "bold")
        )
        self.back_btn.pack(side="left")

        self.tree.bind("<Double-1>", self.on_row_double_click)

    def create_filter_field(self, parent, label_text, variable, placeholder):
        """إنشاء حقل فلتر احترافي"""
        container = ctk.CTkFrame(parent, fg_color="#1e2347", corner_radius=12)
        
        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=("Segoe UI", 11, "bold"),
            text_color="#00d9ff",
            anchor="w"
        )
        label.pack(anchor="w", padx=12, pady=(8, 2))
        
        entry = ctk.CTkEntry(
            container,
            textvariable=variable,
            placeholder_text=placeholder,
            fg_color="#2a3052",
            border_width=0,
            font=("Segoe UI", 11),
            text_color="#ffffff",
            placeholder_text_color="#606582",
            height=35
        )
        entry.pack(fill="x", padx=10, pady=(0, 8))
        entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        return container

    def toggle_advanced_filters(self):
        """إظهار/إخفاء لوحة الفلاتر المتقدمة"""
        if self.filters_visible:
            self.filters_panel.pack_forget()
            self.filters_btn.configure(text="🎛️ فلاتر متقدمة", fg_color="#f59e0b")
            self.filters_visible = False
        else:
            self.filters_panel.pack(fill="x", after=self.filters_btn.master.master, pady=(0, 0))
            self.filters_btn.configure(text="✖ إخفاء الفلاتر", fg_color="#ef4444")
            self.filters_visible = True
            self.populate_filter_suggestions()

    def populate_filter_suggestions(self):
        """ملء القوائم المنسدلة بالقيم الفريدة من البيانات"""
        if self.df.empty:
            return

    def apply_filters(self):
        """تطبيق جميع الفلاتر"""
        if self.df.empty:
            return

        filtered = self.df.copy()

        # فلتر البحث العام
        search_query = self.filter_vars['search'].get().strip().lower()
        if search_query:
            filtered = filtered[
                filtered.apply(
                    lambda r: r.astype(str).str.lower().str.contains(search_query).any(),
                    axis=1
                )
            ]

        # فلتر التاريخ (من)
        date_from = self.filter_vars['date_from'].get().strip()
        if date_from and 'Date' in filtered.columns:
            try:
                filtered = filtered[pd.to_datetime(filtered['Date'], errors='coerce') >= pd.to_datetime(date_from)]
            except:
                pass

        # فلتر التاريخ (إلى)
        date_to = self.filter_vars['date_to'].get().strip()
        if date_to and 'Date' in filtered.columns:
            try:
                filtered = filtered[pd.to_datetime(filtered['Date'], errors='coerce') <= pd.to_datetime(date_to)]
            except:
                pass

        # فلتر اسم المستخدم
        username = self.filter_vars['username'].get().strip().lower()
        if username:
            user_cols = [col for col in filtered.columns if 'user' in col.lower() or 'name' in col.lower()]
            if user_cols:
                filtered = filtered[
                    filtered[user_cols].apply(
                        lambda r: r.astype(str).str.lower().str.contains(username).any(),
                        axis=1
                    )
                ]

        # فلتر نوع العملية
        operation = self.filter_vars['operation'].get().strip().lower()
        if operation:
            op_cols = [col for col in filtered.columns if 'operation' in col.lower() or 'type' in col.lower() or 'عملية' in col.lower()]
            if op_cols:
                filtered = filtered[
                    filtered[op_cols].apply(
                        lambda r: r.astype(str).str.lower().str.contains(operation).any(),
                        axis=1
                    )
                ]

        # فلتر حالة العملية
        status = self.filter_vars['status'].get().strip().lower()
        if status:
            status_cols = [col for col in filtered.columns if 'status' in col.lower() or 'state' in col.lower() or 'حالة' in col.lower()]
            if status_cols:
                filtered = filtered[
                    filtered[status_cols].apply(
                        lambda r: r.astype(str).str.lower().str.contains(status).any(),
                        axis=1
                    )
                ]

        self.filtered_df = filtered
        self.update_table()
        self.update_stats(len(filtered), len(self.df))

        if filtered.empty and not self.df.empty:
            self.show_empty()
            self.footer_label.configure(text="🔍 لم يتم العثور على نتائج مطابقة للفلاتر")
        else:
            self.show_table()
            self.footer_label.configure(text="💡 اضغط مرتين على أي سجل لعرض التفاصيل الكاملة")

    def clear_all_filters(self):
        """مسح جميع الفلاتر"""
        for var in self.filter_vars.values():
            var.set("")
        self.apply_filters()

    def load_data_async(self):
        """تحميل البيانات في Thread منفصل"""
        if self.is_loading:
            return
            
        import threading
        self.is_loading = True
        self.show_loading()
        threading.Thread(target=self.load_data, daemon=True).start()

    def show_loading(self):
        """عرض شاشة التحميل"""
        self.table_frame.pack_forget()
        self.empty_frame.pack_forget()
        self.loading_frame.pack(fill="both", expand=True)
        self.refresh_btn.configure(state="disabled")

    def show_table(self):
        """عرض الجدول"""
        self.loading_frame.pack_forget()
        self.empty_frame.pack_forget()
        self.table_frame.pack(fill="both", expand=True)
        self.refresh_btn.configure(state="normal")

    def show_empty(self):
        """عرض شاشة فارغة"""
        self.loading_frame.pack_forget()
        self.table_frame.pack_forget()
        self.empty_frame.pack(fill="both", expand=True)
        self.refresh_btn.configure(state="normal")

    def load_data(self):
        """تحميل البيانات من Google Sheets"""
        try:
            df = self.fetch_history()
            self.after(0, lambda: self._update_after_load(df))
        except Exception as e:
            self.after(0, lambda: self._handle_load_error(str(e)))
        finally:
            self.is_loading = False

    def _update_after_load(self, df):
        """تحديث الواجهة بعد تحميل البيانات"""
        if df.empty:
            self.show_empty()
            self.update_stats(0)
        else:
            self.df = df
            self.filtered_df = df
            self.update_table()
            self.update_stats(len(df))
            self.show_table()

    def _handle_load_error(self, error_msg):
        """معالجة خطأ التحميل"""
        self.show_empty()
        messagebox.showerror("خطأ", f"⚠️ فشل تحميل السجل:\n{error_msg}")

    def fetch_history(self):
        """جلب بيانات ورقة History من Google Sheets"""
        creds = Credentials.from_service_account_file(
            self.creds_path,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ],
        )
        client = gspread.authorize(creds)
        sheet = client.open(self.sheet_name)
        worksheet = sheet.worksheet(self.history_sheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)

    def update_table(self):
        """عرض البيانات في الجدول بشكل احترافي"""
        self.tree.delete(*self.tree.get_children())
        
        if self.filtered_df.empty:
            return

        self.tree["columns"] = list(self.filtered_df.columns)

        for col in self.filtered_df.columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=150, anchor="center", minwidth=100)

        for idx, row in self.filtered_df.iterrows():
            tags = ("evenrow",) if idx % 2 == 0 else ("oddrow",)
            self.tree.insert("", "end", values=list(row), tags=tags)

        self.tree.tag_configure("evenrow", background="#1e2347")
        self.tree.tag_configure("oddrow", background="#252b4a")

    def update_stats(self, filtered_count=0, total_count=None):
        """تحديث معلومات الإحصائيات"""
        if total_count is None:
            total_count = filtered_count
            
        if filtered_count == total_count:
            self.total_records_label.configure(text=f"📋 إجمالي السجلات: {total_count}")
        else:
            self.total_records_label.configure(
                text=f"📋 عرض {filtered_count} من {total_count} سجل"
            )
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.last_update_label.configure(text=f"🕒 آخر تحديث: {now}")

    def export_data(self):
        """تصدير البيانات إلى ملف Excel"""
        if self.filtered_df.empty:
            messagebox.showwarning("تنبيه", "⚠️ لا توجد بيانات لتصديرها!")
            return

        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                self.filtered_df.to_excel(filename, index=False, engine='openpyxl')
                messagebox.showinfo("نجح", f"✅ تم تصدير البيانات بنجاح!\n{filename}")
        except Exception as e:
            messagebox.showerror("خطأ", f"⚠️ فشل التصدير:\n{e}")

    def on_row_double_click(self, event):
        """عرض تفاصيل السجل عند النقر المزدوج"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item['values']
        columns = list(self.filtered_df.columns)

        details_window = ctk.CTkToplevel(self)
        details_window.title("تفاصيل السجل")
        details_window.geometry("600x500")
        details_window.configure(fg_color="#0a0e27")

        header = ctk.CTkFrame(details_window, fg_color="#1a1f3a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="📄 تفاصيل السجل",
            font=("Segoe UI", 24, "bold"),
            text_color="#00d9ff"
        )
        title.pack(pady=20)

        content = ctk.CTkScrollableFrame(details_window, fg_color="#151938")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        for col, val in zip(columns, values):
            row_frame = ctk.CTkFrame(content, fg_color="#1e2347", corner_radius=10)
            row_frame.pack(fill="x", pady=5)

            label = ctk.CTkLabel(
                row_frame,
                text=f"{col}:",
                font=("Segoe UI", 13, "bold"),
                text_color="#00d9ff",
                anchor="w"
            )
            label.pack(side="top", anchor="w", padx=15, pady=(10, 5))

            value = ctk.CTkLabel(
                row_frame,
                text=str(val),
                font=("Segoe UI", 12),
                text_color="#ffffff",
                anchor="w",
                wraplength=500
            )
            value.pack(side="top", anchor="w", padx=15, pady=(0, 10))

        close_btn = ctk.CTkButton(
            details_window,
            text="✖ إغلاق",
            command=details_window.destroy,
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=("Segoe UI", 13, "bold"),
            height=40
        )
        close_btn.pack(pady=(0, 20))

    def go_back(self):
        """الرجوع إلى القائمة الرئيسية مع تتبع التصحيح"""
        try:

            self.ui_manager.return_to_main()
        except Exception as e:
            import traceback
            print("❌ [DEBUG] Exception in go_back:", e)
            print(traceback.format_exc())


    def show_chart_dialog(self):
        """عرض نافذة اختيار الرسم البياني"""
        if self.filtered_df.empty:
            messagebox.showwarning("تنبيه", "⚠️ لا توجد بيانات لعرض رسم بياني!")
            return

        chart_window = ctk.CTkToplevel(self)
        chart_window.title("الرسم البياني")
        chart_window.geometry("500x400")
        chart_window.configure(fg_color="#0a0e27")
        chart_window.resizable(False, False)

        # مركزية النافذة
        chart_window.transient(self)
        chart_window.grab_set()

        header = ctk.CTkFrame(chart_window, fg_color="#1a1f3a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="📈 الرسم البياني",
            font=("Segoe UI", 24, "bold"),
            text_color="#00d9ff"
        )
        title.pack(pady=20)

        content = ctk.CTkFrame(chart_window, fg_color="#151938")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # اختيار نوع الرسم البياني
        chart_type_frame = ctk.CTkFrame(content, fg_color="#1e2347", corner_radius=12)
        chart_type_frame.pack(fill="x", pady=10)

        chart_type_label = ctk.CTkLabel(
            chart_type_frame,
            text="📊 اختر نوع الرسم البياني:",
            font=("Segoe UI", 14, "bold"),
            text_color="#00d9ff"
        )
        chart_type_label.pack(anchor="w", padx=15, pady=(15, 5))

        chart_type_options = ctk.CTkFrame(chart_type_frame, fg_color="transparent")
        chart_type_options.pack(fill="x", padx=15, pady=(0, 15))

        bar_radio = ctk.CTkRadioButton(
            chart_type_options,
            text="📊 رسم أعمدة (Bar)",
            variable=self.chart_type,
            value="bar",
            font=("Segoe UI", 12),
            text_color="#ffffff"
        )
        bar_radio.pack(side="left", padx=(0, 20))

        pie_radio = ctk.CTkRadioButton(
            chart_type_options,
            text="🥧 رسم دائري (Pie)",
            variable=self.chart_type,
            value="pie",
            font=("Segoe UI", 12),
            text_color="#ffffff"
        )
        pie_radio.pack(side="left")

        # اختيار العمود للرسم البياني
        column_frame = ctk.CTkFrame(content, fg_color="#1e2347", corner_radius=12)
        column_frame.pack(fill="x", pady=10)

        column_label = ctk.CTkLabel(
            column_frame,
            text="🎯 اختر العمود للإحصائيات:",
            font=("Segoe UI", 14, "bold"),
            text_color="#00d9ff"
        )
        column_label.pack(anchor="w", padx=15, pady=(15, 5))

        # اختيار العمود الافتراضي (الحالة)
        default_column = "Status"
        available_columns = list(self.filtered_df.columns)
        
        if default_column not in available_columns and available_columns:
            default_column = available_columns[0]

        self.selected_column = ctk.StringVar(value=default_column)
        
        column_combo = ctk.CTkComboBox(
            column_frame,
            values=available_columns,
            variable=self.selected_column,
            font=("Segoe UI", 12),
            dropdown_font=("Segoe UI", 11),
            fg_color="#2a3052",
            border_color="#00d9ff",
            button_color="#00d9ff",
            text_color="#ffffff"
        )
        column_combo.pack(fill="x", padx=15, pady=(0, 15))

        # أزرار التنفيذ
        buttons_frame = ctk.CTkFrame(content, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)

        preview_btn = ctk.CTkButton(
            buttons_frame,
            text="👁️ معاينة الرسم",
            command=lambda: self.generate_chart(preview=True),
            width=140,
            height=45,
            corner_radius=10,
            fg_color="#00d9ff",
            hover_color="#00b8d4",
            text_color="#0a0e27",
            font=("Segoe UI", 13, "bold")
        )
        preview_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(
            buttons_frame,
            text="📥 تصدير PDF",
            command=lambda: self.generate_chart(preview=False),
            width=140,
            height=45,
            corner_radius=10,
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold")
        )
        export_btn.pack(side="left", padx=5)

        close_btn = ctk.CTkButton(
            buttons_frame,
            text="✖ إغلاق",
            command=chart_window.destroy,
            width=100,
            height=45,
            corner_radius=10,
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold")
        )
        close_btn.pack(side="left", padx=5)

    def generate_chart(self, preview=True):
        """إنشاء الرسم البياني مع دعم كامل للعربية + شعار البرنامج"""
        import matplotlib.pyplot as plt
        from matplotlib import font_manager, rcParams
        from matplotlib.backends.backend_pdf import PdfPages
        import arabic_reshaper
        from bidi.algorithm import get_display
        from tkinter import filedialog
        from datetime import datetime
        from PIL import Image

        def fix_arabic_text(text):
            """إصلاح الحروف واتجاه النص العربي"""
            try:
                reshaped_text = arabic_reshaper.reshape(str(text))
                return get_display(reshaped_text)
            except Exception:
                return str(text)

        try:
            column = self.selected_column.get()
            if column not in self.filtered_df.columns:
                messagebox.showerror("خطأ", f"العمود '{column}' غير موجود في البيانات!")
                return

            # إعداد الخط العربي
            font_path = None
            for f in font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
                if any(k in f for k in ["Cairo", "Arial", "Noto", "Tahoma", "Geeza"]):
                    font_path = f
                    break

            if font_path:
                rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
            else:
                rcParams['font.family'] = 'Arial Unicode MS'

            rcParams['axes.unicode_minus'] = False

            # تجهيز البيانات
            stats = self.filtered_df[column].value_counts()
            if stats.empty:
                messagebox.showwarning("تنبيه", "⚠️ لا توجد بيانات كافية لعرض رسم بياني!")
                return

            plt.figure(figsize=(11, 8))
            plt.style.use('seaborn-v0_8-darkgrid')

            # 📊 نوع الرسم
            if self.chart_type.get() == "bar":
                labels = [fix_arabic_text(lbl) for lbl in stats.index.astype(str)]
                bars = plt.bar(labels, stats.values,
                            color=['#00d9ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444'])

                plt.xlabel(fix_arabic_text(column), fontsize=14, fontweight='bold')
                plt.ylabel(fix_arabic_text("عدد السجلات"), fontsize=14, fontweight='bold')
                plt.title(fix_arabic_text(f"توزيع {column}"), fontsize=20, fontweight='bold', pad=20)

                # القيم فوق الأعمدة
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{int(height)}', ha='center', va='bottom', fontsize=12)

                plt.xticks(rotation=45, ha='right')

            else:
                labels = [fix_arabic_text(lbl) for lbl in stats.index.astype(str)]
                colors = plt.cm.Set3(range(len(stats)))
                wedges, texts, autotexts = plt.pie(
                    stats.values,
                    labels=labels,
                    autopct='%1.1f%%',
                    colors=colors,
                    startangle=90
                )

                plt.title(fix_arabic_text(f"توزيع {column}"), fontsize=20, fontweight='bold', pad=20)

                for t in texts + autotexts:
                    t.set_fontsize(11)
                    t.set_fontfamily(rcParams['font.family'])

            # 🌟 إضافة شعار EURO TOOLS في الأسفل
            plt.figtext(0.5, 0.02, "EURO TOOLS - CODE MANAGER PRO", ha='center',
                        fontsize=16, color='#00d9ff', fontweight='bold')

            # 🖼️ إضافة اللوجو في الزاوية اليمنى العليا
            try:
                from config import AppConfig
                logo_path = getattr(AppConfig, "LOGO_IMAGE", None)
                if logo_path and os.path.exists(logo_path):
                    logo = Image.open(logo_path)
                    new_size = (120, 120)
                    logo.thumbnail(new_size)

                    plt.figimage(logo, xo=plt.gcf().bbox.xmax - 150, yo=plt.gcf().bbox.ymax - 150, alpha=0.25, zorder=10)
            except Exception as e:
                print(f"⚠️ Logo load error: {e}")

            plt.tight_layout(rect=[0, 0.05, 1, 1])

            # ✅ عرض أو تصدير
            if preview:
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                
                preview_window = ctk.CTkToplevel(self)
                preview_window.title("معاينة الرسم البياني")
                preview_window.geometry("900x700")
                preview_window.configure(fg_color="#0a0e27")
                
                preview_window.transient(self)  # يخليها فوق النافذة الأصلية
                preview_window.lift()           # يرفعها للأمام فورًا
                preview_window.focus_force()    # يخليها تاخد التركيز


                fig = plt.gcf()  # احصل على الشكل الحالي
                canvas = FigureCanvasTkAgg(fig, master=preview_window)
                canvas.draw()
                widget = canvas.get_tk_widget()
                widget.pack(fill="both", expand=True, padx=10, pady=10)

                close_btn = ctk.CTkButton(
                    preview_window,
                    text="✖ إغلاق",
                    command=preview_window.destroy,
                    fg_color="#ef4444",
                    hover_color="#dc2626",
                    font=("Segoe UI", 13, "bold"),
                    height=40
                )
                close_btn.pack(pady=(0, 15))
            else:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"chart_{column}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )
                if filename:
                    with PdfPages(filename) as pdf:
                        pdf.savefig()
                    plt.close()
                    messagebox.showinfo("نجح", f"✅ تم تصدير الرسم البياني بنجاح!\n{filename}")
                else:
                    plt.close()


        except Exception as e:
            plt.close()
            messagebox.showerror("خطأ", f"⚠️ فشل إنشاء الرسم البياني:\n{e}")
