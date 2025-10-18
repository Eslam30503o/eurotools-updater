import customtkinter as ctk
from functools import partial
from tkinter import messagebox
import tkinter as tk
from ui.history_screen import HistoryScreen
from sync.manager import SyncManager

import threading

CATEGORIES = ["الكل", "BOM", "CNC Cutting Tools", "Hand Tools", 
              "Machine Spare Parts", "Oil & Lubricants", "Stationary", 
              "Standard Components","أخرى"]

class ProductsMixin:
    
   
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
        title_container = ctk.CTkFrame(header_frame, fg_color=("#2C3E50", "#34495E"), corner_radius=15, height=90)
        title_container.pack(fill="x")
        title_container.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            title_container,
            text="📦 إدارة المنتجات",
            font=("Cairo", 28, "bold"),
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
            corner_radius=15,
            scrollbar_button_color=("#3498DB", "#2980B9"),
            scrollbar_button_hover_color=("#2980B9", "#21618C")
        )
        self.products_list_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))
        
        # إطار القوائم المحفوظة (مخفي بشكل افتراضي)
        self.saved_lists_frame = ctk.CTkFrame(
            self.products_frame,
            fg_color=("#FFFFFF", "#1E1E1E"),
            width=280,
            corner_radius=15
        )
        
        self.sidebar_visible = False
        

    def _create_modern_toolbar(self):
        """شريط أدوات احترافي مع تصميم Material Design"""
        toolbar = ctk.CTkFrame(
            self.products_frame,
            fg_color=("#FFFFFF", "#2B2B2B"),
            corner_radius=15,
            height=80,
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
            ("🔄 مزامنة الآن", "#27AE60", "#1E8449", self.manual_sync, "bold"),
            ("➕ إضافة منتج", "#16A085", "#138D75", self.add_new_tool_window, "bold"),
            ("📊 تصدير Excel", "#2874A6", "#1F618D", self.export_selected_to_excel, "bold"),
            ("➕ إضافة لقائمة", "#7D3C98", "#6C3483", self.show_add_selected_to_list_dialog, "bold"),
            ("📂 القوائم", "#D68910", "#B9770E", self.toggle_saved_lists, "bold"),
            ("📜 السجل", "#34495E", "#2C3E50", self.create_history_page, "bold"),
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

        # زر القائمة الجانبية
        menu_btn = ctk.CTkButton(
            right_section,
            text="⚙️",
            width=55,
            height=46,
            fg_color=("#34495E", "#2C3E50"),
            hover_color=("#2C3E50", "#1C2833"),
            command=self.show_settings_page,
            corner_radius=10,
            font=("Arial", 20)
        )
        menu_btn.pack(side="right", padx=4)

    def _on_search_change(self, *args):
        # إلغاء أي مؤقت سابق
        if hasattr(self, "_search_after_id"):
            self.root.after_cancel(self._search_after_id)

        # تأجيل التحديث نصف ثانية لتقليل الحمل
        self._search_after_id = self.root.after(00, self.update_products_list)


    def _create_advanced_search_section(self):
        """قسم البحث والفلترة المتقدم"""
        search_container = ctk.CTkFrame(
            self.products_frame,
            fg_color=("#FFFFFF", "#2B2B2B"),
            corner_radius=15,
            border_width=2,
            border_color=("#E0E0E0", "#404040")
        )
        search_container.pack(padx=20, pady=(0, 15), fill="x")
        
        inner = ctk.CTkFrame(search_container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=15)
        
        # الجانب الأيمن - الفلترة
        filter_section = ctk.CTkFrame(inner, fg_color="transparent")
        filter_section.pack(side="right")
        
        ctk.CTkLabel(
            filter_section,
            text="🏷️",
            font=("Arial", 18)
        ).pack(side="right", padx=(0, 8))
        
        self.category_filter_menu = ctk.CTkOptionMenu(
            filter_section,
            values=CATEGORIES,
            command=self.update_products_list,
            width=200,
            height=42,
            corner_radius=10,
            font=("Cairo", 13),
            dropdown_font=("Cairo", 12),
            fg_color=("#2874A6", "#1F618D"),
            button_color=("#1F618D", "#174A7E"),
            button_hover_color=("#174A7E", "#1B4F72")
        )
        self.category_filter_menu.pack(side="right")
        
        # الجانب الأيسر - البحث
        search_section = ctk.CTkFrame(inner, fg_color="transparent")
        search_section.pack(side="left", fill="x", expand=True, padx=(0, 25))
        
        # أيقونة البحث
        search_icon = ctk.CTkLabel(
            search_section,
            text="🔍",
            font=("Arial", 18)
        )
        search_icon.pack(side="left", padx=(0, 10))
        

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_section,
            textvariable=self.search_var,
            placeholder_text="ابحث بالاسم، الكود، الفئة أو الوصف..."
        )

        # اربط التغيير في النص مباشرة
        self.search_var.trace_add("write", self._on_search_change)

        self.search_entry.pack(side="left", fill="x", expand=True)
        
        # 🔥 إصلاح ربط الأحداث - إضافة تحقق
        def test_key_press(event):
            print(f"🎹 ضغط على زر: {event.keysym} | النص: '{self.search_entry.get()}'")
        
        def delayed_search(event=None):
            current_text = self.search_entry.get()
            print(f"🔍 تفعيل البحث بعد تأخير: '{current_text}'")
            
            if hasattr(self, "_search_after_id"):
                self.root.after_cancel(self._search_after_id)
            self._search_after_id = self.root.after(300, self.update_products_list)

        # ربط الأحداث بشكل مكثف
        self.search_entry.bind("<KeyPress>", test_key_press)  # للتحقق
        self.search_entry.bind("<KeyRelease>", delayed_search)  # البحث الفعلي
        
        # أيضًا ربط عند الضغط على Enter
        self.search_entry.bind("<Return>", lambda e: self.update_products_list())
        
        # زر مسح البحث
        clear_btn = ctk.CTkButton(
            search_section,
            text="✕",
            width=42,
            height=42,
            corner_radius=10,
            fg_color=("#95A5A6", "#7F8C8D"),
            hover_color=("#7F8C8D", "#566573"),
            command=self._clear_search,
            font=("Arial", 16, "bold")
        )
        clear_btn.pack(side="left", padx=(8, 0))
        
        # أضف هذا في _create_advanced_search_section بعد حقل البحث
        test_btn = ctk.CTkButton(
            search_section,
            text="🔍",
            width=42,
            height=42,
            command=lambda: print(f"🔍 اختبار البحث: '{self.search_entry.get()}'")
        )
        test_btn.pack(side="left", padx=(8, 0))

    # ضع هذا التعريف في نفس الكلاس ProductsMixin (استبدال للدالة القديمة)
    def _clear_search(self):
        """مسح البحث: يمسح StringVar ويكنسل أي بعد مؤجل ثم يحدث اللائحة."""
        try:
            # ألغِ أي "after" مؤجل (debounce) لو موجود
            if hasattr(self, "_search_after_id"):
                try:
                    self.root.after_cancel(self._search_after_id)
                except Exception:
                    pass

            # مسح الـ StringVar (هذا سيُحدّث الـ Entry تلقائيًا لأننا ربطناه بـ textvariable)
            if hasattr(self, "search_var"):
                self.search_var.set("")
            else:
                # كفالة: إذا ما فيش search_var نستخدم delete مباشرة
                if hasattr(self, "search_entry"):
                    self.search_entry.delete(0, "end")

            # حدث التحديث (لو عايز تستخدم الـ trace بدل النداء المباشر، ممكن تحذفه)
            # نُشغّل التحديث في الخيط UI عبر root.after لضمان سلامة تحديث الواجهة
            self.root.after(0, lambda: self.update_products_list())

            # طباعة للتصحيح
            print("🧹 _clear_search: search_var =", getattr(self, "search_var", None) and self.search_var.get())

        except Exception as e:
            print("⚠️ خطأ في _clear_search:", e)


    # 1. تحديث دالة update_products_list
    def update_products_list(self, category_choice=None):
        """تحديث قائمة المنتجات بتأثيرات سلسة - يتم الآن بدء عملية البحث في خيط منفصل."""
        # تأكد من أن category_choice يتم تحديثه إذا تم اختياره من القائمة
        
        if category_choice and self.category_filter_menu.get() != category_choice:
            # هذه الخطوة مهمة لضمان أن الفلترة تعتمد على الاختيار الجديد
            self.category_filter_menu.set(category_choice) 
        
        # ⚠️ الخطوة الأهم: نقل العملية الثقيلة إلى خيط منفصل
        threading.Thread(
            target=self._run_filtering_and_display,
            daemon=True,
            name="ProductFilterThread"
        ).start()

    # 2. إضافة دالة _run_filtering_and_display لتنفيذ العمل في الخلفية
    def _run_filtering_and_display(self):
        try:           
            tools_data = self.data_manager.load_tools()           
            filtered_data = self._get_filtered_products(tools_data)           
            count = len(filtered_data)           
            self.root.after(0, lambda: self._finalize_ui_update(filtered_data, count))

        except Exception as e:
            print(f"خطأ في خيط التصفية: {e}")

    def _finalize_ui_update(self, filtered_data, count):
        # تنظيف الإطار (يجب أن يتم على شريط الواجهة الرئيسي)
        for widget in self.products_list_frame.winfo_children():
            widget.destroy()
            
        # تحديث عداد المنتجات (يجب أن يتم على شريط الواجهة الرئيسي)
        self.products_count_label.configure(
            text=f"عدد المنتجات: {count} | آخر تحديث: الآن"
        )
        
        if not filtered_data:
            self._show_empty_state()
        else:
            self._display_products(filtered_data)
            
    # في ملف ProductsMixin
    def _get_filtered_products(self, tools_data):
        """الحصول على المنتجات المفلترة (يدعم list و dict)"""
        search_query = self.search_var.get().strip().lower()
        selected_category = self.category_filter_menu.get().strip()

        print(f"🔍 البحث: '{search_query}' | الفئة: '{selected_category}'")
        print(f"✅ get_final_code متاحة: {hasattr(self, 'get_final_code')}")

        # 1. تهيئة البيانات: تحويل أي dict إلى list
        if isinstance(tools_data, dict):
            tools_list = list(tools_data.values())
            print(f"📊 تم تحويل dict إلى list: {len(tools_list)} عنصر")
        elif isinstance(tools_data, list):
            tools_list = tools_data
            print(f"📊 البيانات list: {len(tools_list)} عنصر")
        else:
            tools_list = []
            print("❌ نوع البيانات غير معروف")

        current_data = tools_list

        # 2. 🔎 فلترة حسب الفئة (Category Filter)
        if selected_category != "الكل":
            original_count = len(current_data)
            current_data = [
                t for t in current_data
                if t.get("category", "").strip().lower() == selected_category.lower()
            ]
            print(f"🏷️ بعد فلترة الفئة [{selected_category}]: {original_count} → {len(current_data)}")

        # 3. 🔍 فلترة حسب البحث النصي (Text Search Filter)
        if search_query:
            original_count = len(current_data)
            print(f"🔤 تطبيق البحث النصي: '{search_query}'")
            
            filtered_results = []
            for i, tool in enumerate(current_data):
                name_en = tool.get("name_en", f"tool_{i}")
                if self._matches_search(name_en, tool, search_query):
                    filtered_results.append(tool)
            
            current_data = filtered_results
            print(f"📈 بعد البحث النصي: {original_count} → {len(current_data)}")
        
        print(f"✅ النتيجة النهائية: {len(current_data)} منتج مطابق")
        return current_data

    def _matches_search(self, name_en, data, query):
        """بحث شامل في عدة حقول"""
        query = query.strip().lower()
        if not query:
            return True
        
        final_code = ""
        if hasattr(self, "get_final_code"):
            try:
                final_code = self.get_final_code(data).lower()
            except Exception as e:
                print(f"⚠️ خطأ في get_final_code: {e}")
        else:
            final_code = data.get("final_code", "").lower()

        # الحقول التي نبحث فيها
        fields = [
            data.get("name_ar", ""),
            data.get("name_en", ""),
            data.get("code", ""),
            data.get("category", ""),
            data.get("description", ""),
            data.get("project_name", ""),
            final_code
        ]

        # إذا كان أي حقل يحتوي على نص البحث → نرجع True
        for field in fields:
            if query in str(field).lower():
                print(f"✅ مطابقة في: {field}")
                return True

        return False



    def _show_empty_state(self):
        """حالة فارغة احترافية"""
        empty_container = ctk.CTkFrame(
            self.products_list_frame,
            fg_color="transparent"
        )
        empty_container.pack(expand=True, fill="both", pady=100)
        
        # أيقونة كبيرة
        icon_frame = ctk.CTkFrame(empty_container, fg_color=("#E8F4F8", "#2C3E50"), corner_radius=100, width=150, height=150)
        icon_frame.pack(pady=(0, 25))
        icon_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_frame,
            text="📦",
            font=("Arial", 70)
        ).pack(expand=True)
        
        ctk.CTkLabel(
            empty_container,
            text="لا توجد منتجات مطابقة",
            font=("Cairo", 26, "bold"),
            text_color=("#34495E", "#BDC3C7")
        ).pack()
        
        ctk.CTkLabel(
            empty_container,
            text="جرب تغيير معايير البحث أو الفلترة",
            font=("Cairo", 15),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack(pady=(8, 0))

    def _display_products(self, filtered_data):
        """عرض المنتجات ببطاقات احترافية - يدعم dict و list"""

        # ✅ تأكد أن الإطار الخاص بالقائمة موجود (أو أعد إنشاؤه لو اختفى)
        if not hasattr(self, "products_list_frame") or not self.products_list_frame.winfo_exists():
            self.products_list_frame = ctk.CTkScrollableFrame(
                self.products_frame,
                fg_color=("gray92", "gray14"),
                corner_radius=15,
                scrollbar_button_color=("#3498DB", "#2980B9"),
                scrollbar_button_hover_color=("#2980B9", "#21618C")
            )
            self.products_list_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        # ✅ تنظيف محتوى الإطار فقط بدون تدميره
        for widget in self.products_list_frame.winfo_children():
            widget.destroy()

        # ✅ دعم الحالتين: dict أو list
        if isinstance(filtered_data, dict):
            iterable_data = filtered_data.items()
        elif isinstance(filtered_data, list):
            iterable_data = [(tool.get("name_en", f"Tool_{i+1}"), tool) for i, tool in enumerate(filtered_data)]
        else:
            from tkinter import messagebox
            messagebox.showerror("خطأ", "نوع البيانات غير مدعوم في عرض المنتجات.")
            return

        # ✅ لو مفيش أدوات
        if not iterable_data:
            ctk.CTkLabel(
                self.products_list_frame,
                text="❌ لا توجد أدوات مضافة حتى الآن",
                font=("Arial", 14, "bold"),
                text_color="gray"
            ).pack(pady=50)
            return

        # ✅ عرض كل أداة كبطاقة احترافية
        for idx, (tool_name_en, tool_data) in enumerate(iterable_data):
            final_code = self.get_final_code(tool_data)
            self._create_premium_product_card(tool_name_en, tool_data, final_code, idx)

    def _create_premium_product_card(self, tool_name_en, tool_data, final_code, index):
        """بطاقة منتج بتصميم Premium"""
        card_container = ctk.CTkFrame(
            self.products_list_frame,
            fg_color="transparent"
        )
        card_container.pack(padx=12, pady=10, fill="x")
        
        card = ctk.CTkFrame(
            card_container,
            fg_color=("#FFFFFF", "#2B2B2B"),
            corner_radius=18,
            border_width=2,
            border_color=("#E8E8E8", "#404040")
        )
        card.pack(fill="x")

        # 🖱️ خلي البطاقة كلها قابلة للضغط
        card.bind("<Button-1>", lambda e: self.show_product_details(tool_name_en, tool_data, final_code))

        # باقي الكود زي ما هو (checkbox + info + actions ...)
        top_section = ctk.CTkFrame(card, fg_color="transparent")
        top_section.pack(fill="x", padx=25, pady=(20, 15))
        
        self._create_premium_checkbox(top_section, tool_name_en, tool_data)
        self._create_premium_product_info(top_section, tool_name_en, tool_data, final_code)
        # الجزء الخاص بالأزرار (تفاصيل، طباعة، تعديل...)
        actions_section = ctk.CTkFrame(card, fg_color="transparent")
        actions_section.pack(fill="x", padx=20, pady=(10, 15))

        self._create_premium_action_buttons(actions_section, tool_name_en, tool_data, final_code)


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
            ("المشروع", tool_data.get("project_name", "غير محدد")),
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



    def _create_premium_checkbox(self, parent, tool_name_en, tool_data):
        """Checkbox احترافي"""
        selected_var = ctk.BooleanVar(value=tool_name_en in self.selected_items)
        
        def on_select():
            if selected_var.get():
                self.selected_items[tool_name_en] = tool_data
            else:
                self.selected_items.pop(tool_name_en, None)
        
        checkbox = ctk.CTkCheckBox(
            parent,
            text="",
            variable=selected_var,
            command=on_select,
            width=35,
            height=35,
            corner_radius=8,
            border_width=3,
            fg_color=("#16A085", "#138D75"),
            hover_color=("#138D75", "#117A65"),
            border_color=("#BDC3C7", "#7F8C8D")
        )
        checkbox.pack(side="left", padx=(0, 20))

    def _create_premium_product_info(self, parent, tool_name_en, tool_data, final_code):
        """معلومات المنتج بتنسيق Premium"""
        info_container = ctk.CTkFrame(parent, fg_color="transparent")
        info_container.pack(side="right", fill="x", expand=True)
        
        # الاسم العربي
        name_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        name_frame.pack(anchor="e", fill="x")
        
        ctk.CTkLabel(
            name_frame,
            text=f"📦 {tool_data.get('name_ar', 'غير محدد')}",
            font=("Cairo", 17, "bold"),
            text_color=("#2C3E50", "#ECF0F1"),
            anchor="e"
        ).pack(side="right")
        
        # الاسم الإنجليزي والفئة
        details_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        details_frame.pack(anchor="e", pady=(5, 0))
        
        # Badge للفئة
        category_colors = {
            "BOM": ("#E74C3C", "#C0392B"),
            "CNC Cutting Tools": ("#3498DB", "#2980B9"),
            "Hand Tools": ("#F39C12", "#E67E22"),
            "Machine Spare Parts": ("#9B59B6", "#8E44AD"),
            "Oil & Lubricants": ("#1ABC9C", "#16A085"),
            "Stationary": ("#95A5A6", "#7F8C8D"),
            "Standard Components": ("#34495E", "#2C3E50")
        }
        
        category = tool_data.get('category', 'غير محددة')
        cat_color, cat_hover = category_colors.get(category, ("#7F8C8D", "#566573"))
        
        category_badge = ctk.CTkButton(
            details_frame,
            text=f"  {category}  ",
            font=("Cairo", 11, "bold"),
            fg_color=cat_color,
            hover_color=cat_hover,
            corner_radius=8,
            height=26,
            state="disabled",
            text_color=("#FFFFFF", "#FFFFFF")
        )
        category_badge.pack(side="right", padx=(0, 8))
        
        ctk.CTkLabel(
            details_frame,
            text=f"({tool_name_en})",
            font=("Arial", 12),
            text_color=("#7F8C8D", "#95A5A6")
        ).pack(side="right")
        
        # اسم المشروع
        if tool_data.get("project_name"):
            project_frame = ctk.CTkFrame(info_container, fg_color="transparent")
            project_frame.pack(anchor="e", pady=(5, 0))
            
            ctk.CTkLabel(
                project_frame,
                text=f"🎯 {tool_data.get('project_name')}",
                font=("Cairo", 11),
                text_color=("#34495E", "#BDC3C7")
            ).pack(side="right")
        
        # الكود مع خلفية
        code_frame = ctk.CTkFrame(
            info_container,
            fg_color=("#ECF0F1", "#34495E"),
            corner_radius=10
        )
        code_frame.pack(anchor="e", pady=(8, 0), fill="x")
        
        ctk.CTkLabel(
            code_frame,
            text=f"💻 {final_code}",
            font=("Consolas", 13, "bold"),
            text_color=("#2C3E50", "#ECF0F1")
        ).pack(padx=15, pady=8, anchor="e")

    def _create_premium_action_buttons(self, parent, tool_name_en, tool_data, final_code):
        """أزرار الإجراءات الاحترافية"""
        # الجانب الأيمن - الأزرار الرئيسية
        main_actions = ctk.CTkFrame(parent, fg_color="transparent")
        main_actions.pack(side="right")

        # زر التفاصيل بخاصية مميزة
        details_btn = ctk.CTkButton(
            main_actions,
            text="👁️ تفاصيل",
            command=lambda: self.show_product_details(tool_name_en, tool_data, final_code),
            width=120,
            height=40,
            corner_radius=12,
            fg_color="#1ABC9C",          # تركواز مميز
            hover_color="#16A085",
            font=("Cairo", 13, "bold"),
            text_color="white"

        )
        details_btn.pack(side="left", padx=8)

        # باقي الأزرار
        actions = [
            ("🖨️ طباعة", "#2874A6", "#1F618D", lambda: self.show_print_dialog(final_code)),
            ("📥 رفع", "#16A085", "#138D75", lambda: self.gsu.save_to_google_sheet(tool_data, final_code)),
            ("✍️ تعديل", "#D68910", "#B9770E", lambda: self.edit_tool_window(tool_name_en)),
            ("🗑️ حذف", "#C0392B", "#A93226", lambda: self.delete_tool(tool_name_en)),
        ]

        for text, color, hover, cmd in actions:
            btn = ctk.CTkButton(
                main_actions,
                text=text,
                command=cmd,
                width=100,
                height=38,
                corner_radius=10,
                fg_color=color,
                hover_color=hover,
                font=("Cairo", 12, "bold")
            )
            btn.pack(side="right", padx=4)

        # الجانب الأيسر - زر إضافة للقائمة
        add_list_btn = ctk.CTkButton(
            parent,
            text="➕ إضافة للقائمة",
            command=lambda: self.show_add_to_list_dialog(tool_data),
            width=140,
            height=38,
            corner_radius=10,
            fg_color=("#7D3C98", "#6C3483"),
            hover_color=("#6C3483", "#5B2C6F"),
            font=("Cairo", 12, "bold")
        )
        add_list_btn.pack(side="left")


    def safe_window_action(window, func, *args, **kwargs):
        """ينفذ دالة فقط لو النافذة لسه موجودة"""
        try:
            if window and window.winfo_exists():
                func(*args, **kwargs)
        except Exception:
            pass


    def delete_tool(self, tool_name_en):
        """حذف أداة بعد إدخال كلمة سر للتأكيد"""
        correct_password = "123"
        
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
                                self.show_toast(f"🗑️ جارٍ حذف الأداة من Google Sheets ({final_code})", "success")
                                print(f"🗑️ جارٍ حذف الأداة من Google Sheets ({final_code})")
                                
                                
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


    def show_toast(self, message, msg_type="info"):
        """رسالة Toast احترافية"""
        toast = ctk.CTkToplevel(self.products_frame)
        toast.withdraw()
        toast.overrideredirect(True)
        
        colors = {
            "success": ("#16A085", "#FFFFFF"),
            "error": ("#C0392B", "#FFFFFF"),
            "info": ("#2874A6", "#FFFFFF"),
            "warning": ("#D68910", "#FFFFFF")
        }
        
        bg_color, text_color = colors.get(msg_type, colors["info"])
        
        toast_frame = ctk.CTkFrame(
            toast,
            fg_color=bg_color,
            corner_radius=12
        )
        toast_frame.pack(padx=3, pady=3)
        
        # أيقونة حسب النوع
        icons = {
            "success": "✅",
            "error": "❌",
            "info": "ℹ️",
            "warning": "⚠️"
        }
        
        content_frame = ctk.CTkFrame(toast_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=15)
        
        ctk.CTkLabel(
            content_frame,
            text=icons.get(msg_type, "ℹ️"),
            font=("Arial", 20)
        ).pack(side="left", padx=(0, 12))
        
        ctk.CTkLabel(
            content_frame,
            text=message,
            font=("Cairo", 14, "bold"),
            text_color=text_color
        ).pack(side="left")
        
        # موضع Toast
        toast.update_idletasks()
        width = toast.winfo_width()
        x = (toast.winfo_screenwidth() // 2) - (width // 2)
        y = 80
        
        toast.geometry(f"+{x}+{y}")
        toast.deiconify()
        toast.attributes("-topmost", True)
        
        # إخفاء بعد 3 ثواني
        toast.after(3000, toast.destroy)

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
                    fg_color=("#27AE60", "#1E8449"),
                    hover_color=("#1E8449", "#145A32"),
                    state="normal"
                )
            progress_container.destroy()

        def do_sync():
            try:
                if hasattr(self.sync_manager, "stop_event"):
                    self.sync_manager.stop_event.set()  # ⏸️ إيقاف AutoSync مؤقتًا

                self.show_toast("🔄 جاري تنفيذ المزامنة الآن...", "info")
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
