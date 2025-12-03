import customtkinter as ctk
from functools import partial
from tkinter import messagebox
import tkinter as tk
import json
from pathlib import Path
from datetime import datetime
from ui.history_screen import HistoryScreen
from sync.manager import SyncManager
import threading
from categories import CATEGORIES

class ProductUtilsMixin :

    CATEGORIES = CATEGORIES
        
    def create_products_ui(self):
        """إنشاء واجهة المنتجات الرئيسية - تصميم احترافي متقدم"""
        
        # Header مع تدرج لوني احترافي
        header_frame = ctk.CTkFrame(
            self.products_frame, 
            fg_color=("transparent"),
            corner_radius=0
        )
        header_frame.pack(pady=(20, 15), padx=20, fill="x")
        
        # عنوان رئيسي مع أيقونة متحركة
        title_container = ctk.CTkFrame(header_frame, fg_color=("#2C3E50", "#34495E"), corner_radius=15, height=80)
        title_container.pack(fill="x")
        title_container.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            title_container,
            text="📦 إدارة المنتجات",
            font=("Cairo", 25, "bold"),
            text_color=("#ECF0F1", "#ECF0F1")
        )
        title_label.pack(pady=(10, 5))
        
        # Badge لعدد المنتجات مع تصميم أنيق
        self.products_count_label = ctk.CTkLabel(
            title_container,
            text="",
            font=("Cairo", 12),
            text_color=("#BDC3C7", "#95A5A6")
        )
        self.products_count_label.pack(pady=(0, 10))
        
        # Toolbar عصري مع تأثيرات
        self._create_modern_toolbar()
        
        # شريط البحث والفلترة المتطور
        self._create_advanced_search_section()
        
        # قائمة المنتجات مع Scrollbar مخصص
        self.products_list_frame = ctk.CTkScrollableFrame(
            self.products_frame,
            fg_color=("gray92", "gray14"),
            corner_radius=10,
            scrollbar_button_color=("#3498DB", "#2980B9"),
            scrollbar_button_hover_color=("#2980B9", "#21618C")
        )
        self.products_list_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))

           # Pagination defaults
        self.current_page = 0              # رقم الصفحة الحالية (0-based index)
        self.items_per_page = 25           # الافتراضي: 50 منتج في الصفحة
        self.total_pages = 1
        self._pagination_created = False   # علم إننا أنشأنا عناصر pagination أم لا
        self._last_filtered_data = [] 

        # إنشاء إطار أزرار الصفحات أسفل القائمة
        self.create_pagination_controls()
        self._pagination_created = True

          # سيتم تخزين النتائج المفلترة هنا (list)

        
        # إطار القوائم المحفوظة (مخفي بشكل افتراضي)
        self.saved_lists_frame = ctk.CTkFrame(
            self.products_frame,
            fg_color=("#FFFFFF", "#1E1E1E"),
            width=100,
            corner_radius=13
        )
        
        self.sidebar_visible = False
        
    def _create_modern_toolbar(self):
        """شريط أدوات احترافي مع تصميم Material Design"""
        toolbar = ctk.CTkFrame(
            self.products_frame,
            fg_color=("#FFFFFF", "#2B2B2B"),
            corner_radius=15,
            height=50,
            border_width=2,
            border_color=("#E0E0E0", "#404040")
        )
        toolbar.pack(padx=20, pady=(0, 15), fill="x")
        toolbar.pack_propagate(False)
        
        # المحتوى الداخلي
        inner_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=15, pady=12)
        
        # الجانب الأيمن - أزرار الإجراءات
        right_section = ctk.CTkFrame(inner_frame, fg_color="transparent")
        right_section.pack(side="right", fill="x", expand=True)
        
        buttons_data = [
            ("🔄 مزامنة الآن", "#2874A6", "#1F618D", self.manual_sync, "bold"),
            ("➕ إضافة منتج", "#34495E", "#1C2833", self.add_new_tool_window, "bold"),
            ("📊 تصدير Excel", "#2874A6", "#1F618D", self.export_selected_to_excel, "bold"),
            ("➕ إضافة لقائمة", "#34495E", "#1C2833", self.show_add_selected_to_list_dialog, "bold"),
            ("📂 القوائم", "#2874A6", "#1F618D", self.toggle_saved_lists, "bold"),
            #("📜 السجل", "#34495E", "#2C3E50", self.create_history_page, "bold"),
            ("⚙️", "#34495E", "#1C2833", self.show_settings_page, "bold"),


        ]
        
        for text, color, hover, cmd, weight in buttons_data:
            btn = ctk.CTkButton(
                right_section,
                text=text,
                fg_color=color,
                hover_color=hover,
                command=cmd,
                corner_radius=10,
                height=46,
                font=("Cairo", 13, weight),
                border_width=0
            )
            btn.pack(side="right", padx=4, expand=True, fill="x")
        
            # حفظ مرجع الزر لو هو زر المزامنة
            if "مزامنة" in text:
                self.sync_now_btn = btn


    def _finalize_ui_update(self, filtered_data, count):
        # تنظيف الإطار (يجب أن يتم على شريط الواجهة الرئيسي)
        for widget in self.products_list_frame.winfo_children():
            widget.destroy()
            
        current_time = datetime.now().strftime("الساعة %I:%M:%S %p")

        # تحديث عداد المنتجات (يجب أن يتم على شريط الواجهة الرئيسي)
        self.products_count_label.configure(
            text=f"عدد المنتجات: {count} | آخر تحديث: {current_time}"
        )

        # ✅ لو مفيش بيانات — نعرض الحالة الفارغة
        if not filtered_data or len(filtered_data) == 0:
            self._show_empty_state()   # <=== ✅ هنا مكانها المثالي
            self._last_filtered_data = []
            self.current_page = 0
            self.total_pages = 1

            # تحديث الـ pagination لو موجودة
            if self._pagination_created:
                self.page_label.configure(text="صفحة 0 من 0")
                self.prev_btn.configure(state="disabled")
                self.next_btn.configure(state="disabled")

            return   # ✅ نخرج من الدالة بعد عرض الحالة الفارغة

        # ✅ لو في بيانات — نحدث العرض العادي
        self._last_filtered_data = list(filtered_data)
        self.current_page = 0
        total_items = len(self._last_filtered_data)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)

        self.update_products_display()


 