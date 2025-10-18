import customtkinter as ctk
from tkinter import messagebox
from tkinter import simpledialog
import logging
import threading


class ListsMixin:
    def create_new_list_dialog(self):
        """إنشاء قائمة جديدة بتصميم عصري"""
        # نافذة مخصصة بدلاً من simpledialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("➕ إنشاء قائمة جديدة")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # توسيط النافذة
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # إطار رئيسي بتدرج لوني
        main_frame = ctk.CTkFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # أيقونة وعنوان
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(pady=(15, 10))
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text="📁",
            font=("Cairo", 40, "bold"),
        )
        icon_label.pack()
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="إنشاء قائمة جديدة",
            font=("Cairo", 18, "bold")
        )
        title_label.pack(pady=5)
        
        # حقل الإدخال مع تسمية
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(pady=15, padx=20, fill="x")
        
        ctk.CTkLabel(
            input_frame,
            text="اسم القائمة:",
            font=("Cairo", 13),
            anchor="e"
        ).pack(anchor="e", pady=(0, 5))
        
        name_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=" مثال:  مشروع 100 ",
            height=40,
            font=("Cairo", 13),
            corner_radius=10
        )
        name_entry.pack(fill="x")
        name_entry.focus()
        
        # دالة الحفظ
        def save_list():
            list_name = name_entry.get().strip()
            if not list_name:
                messagebox.showwarning("⚠️ تنبيه", "الرجاء إدخال اسم للقائمة")
                return
                
            lists_data = self.data_manager.load_lists()
            if list_name in lists_data:
                messagebox.showerror("❌ خطأ", "اسم هذه القائمة موجود بالفعل")
            else:
                lists_data[list_name] = []
                self.data_manager.save_lists(lists_data)
                self.update_saved_lists_ui()
                dialog.destroy()
                
                # رسالة نجاح أنيقة
                success_dialog = ctk.CTkToplevel(self.root)
                success_dialog.title("✅")
                success_dialog.geometry("150x150")
                success_dialog.transient(self.root)
                success_dialog.grab_set()
                
                success_frame = ctk.CTkFrame(success_dialog, fg_color="#2ecc71", corner_radius=15)
                success_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                ctk.CTkLabel(
                    success_frame,
                    text="✅",
                    font=("Cairo", 50, "bold")
                ).pack(pady=(20, 5))
                
                ctk.CTkLabel(
                    success_frame,
                    text="تم إنشاء القائمة بنجاح!",
                    font=("Cairo", 14, "bold"),
                    text_color="white"
                ).pack()
                
                success_dialog.after(500, success_dialog.destroy)
        
        # أزرار الإجراءات
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(10, 15), padx=20, fill="x")
        
        ctk.CTkButton(
            buttons_frame,
            text="✅ إنشاء",
            command=save_list,
            height=40,
            font=("Cairo", 13, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            buttons_frame,
            text="❌ إلغاء",
            command=dialog.destroy,
            height=40,
            font=("Cairo", 13),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Enter للحفظ
        name_entry.bind("<Return>", lambda e: save_list())

    def show_add_to_list_dialog(self, product_data):
        """إضافة منتج واحد محدد للقائمة بشكل أنيق"""
        lists_data = self.data_manager.load_lists()
        if not lists_data:
            self._show_modern_warning("لا توجد قوائم", "لا توجد قوائم محفوظة.\nالرجاء إنشاء قائمة أولاً.")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("➕ إضافة للقائمة")
        dialog.geometry("250x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # توسيط النافذة
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # إطار رئيسي
        main_frame = ctk.CTkFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # معلومات المنتج
        product_info_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#34495e")
        product_info_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            product_info_frame,
            text="📦 المنتج المحدد",
            font=("Cairo", 12, "bold"),
            text_color="#ecf0f1"
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            product_info_frame,
            text=product_data['name_ar'],
            font=("Cairo", 16, "bold"),
            text_color="white"
        ).pack(pady=(0, 10))
        
        # اختيار القائمة
        ctk.CTkLabel(
            main_frame,
            text="اختر القائمة:",
            font=("Cairo", 14, "bold"),
            anchor="e"
        ).pack(anchor="e", padx=15, pady=(15, 5))
        
        list_names = list(lists_data.keys())
        list_var = ctk.StringVar(value=list_names[0])
        
        list_menu = ctk.CTkOptionMenu(
            main_frame,
            values=list_names,
            variable=list_var,
            height=45,
            font=("Cairo", 13),
            corner_radius=10,
            fg_color="#3498db",
            button_color="#2980b9",
            button_hover_color="#1f618d"
        )
        list_menu.pack(fill="x", padx=15, pady=(0, 15))
        
        def add_and_save():
            selected_list = list_var.get()
            existing_items = lists_data[selected_list]
            existing_codes = {self.get_final_code(item) for item in existing_items}
            product_code = self.get_final_code(product_data)

            if product_code in existing_codes:
                self._show_modern_warning(
                    "منتج موجود",
                    f"المنتج '{product_data['name_ar']}'\nموجود بالفعل في القائمة\n\nالكود: {product_code}"
                )
                dialog.destroy()
                return

            existing_items.append(product_data)
            if self.data_manager.save_lists(lists_data):
                self.update_saved_lists_ui()
                dialog.destroy()
                self._show_modern_success("تمت الإضافة بنجاح!", f"تم إضافة المنتج إلى\n'{selected_list}'")
        
        # أزرار الإجراءات
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15), padx=15, fill="x")
        
        ctk.CTkButton(
            buttons_frame,
            text="✅ إضافة",
            command=add_and_save,
            height=45,
            font=("Cairo", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            buttons_frame,
            text="❌ إلغاء",
            command=dialog.destroy,
            height=45,
            font=("Cairo", 14, "bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))



    def delete_list(self, list_name):
        """حذف قائمة مع تأكيد أنيق واحترافي"""
        # نافذة تأكيد الحذف
        confirm_dialog = ctk.CTkToplevel(self.root)
        confirm_dialog.title("⚠️ تأكيد الحذف")
        confirm_dialog.geometry("350x200")
        confirm_dialog.transient(self.root)
        confirm_dialog.grab_set()

        # توسيط النافذة
        confirm_dialog.update_idletasks()
        x = (confirm_dialog.winfo_screenwidth() // 2) - (confirm_dialog.winfo_width() // 2)
        y = (confirm_dialog.winfo_screenheight() // 2) - (confirm_dialog.winfo_height() // 2)
        confirm_dialog.geometry(f"+{x}+{y}")

        # الإطار الرئيسي
        main_frame = ctk.CTkFrame(confirm_dialog, corner_radius=15, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # العنوان والأيقونة
        ctk.CTkLabel(
            main_frame,
            text="⚠️",
            font=("Cairo", 55, "bold"),
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            main_frame,
            text="هل أنت متأكد من حذف القائمة؟",
            font=("Cairo", 16, "bold"),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            main_frame,
            text=f"📁 {list_name}",
            font=("Cairo", 20, "bold"),
            text_color="white"
        ).pack(pady=(0, 20))

        # دالة التأكيد
        def confirm_delete():
            try:
                lists_data = self.data_manager.load_lists()
                if list_name not in lists_data:
                    self._show_modern_warning("القائمة غير موجودة", f"لم يتم العثور على القائمة '{list_name}'.")
                    confirm_dialog.destroy()
                    return

                # حذف القائمة
                del lists_data[list_name]
                saved = self.data_manager.save_lists(lists_data)

                if saved:
                    self.update_saved_lists_ui()
                    self.root.update_idletasks()
                    confirm_dialog.destroy()
                    self._show_modern_success("تم الحذف", f"تم حذف القائمة\n'{list_name}' بنجاح ✅")
                    
                    # ✅ تحديث Google Sheets بعد الحذف
                    if hasattr(self, "sync_manager") and self.sync_manager:
                        threading.Thread(target=self.sync_manager.sync_all, daemon=True).start()
                        print(f"🧩 تمت مزامنة الحذف '{list_name}' مع Google Sheets.")

                else:
                    self._show_modern_warning("خطأ", "لم يتم حفظ التغييرات!")
            except Exception as e:
                confirm_dialog.destroy()
                self._show_modern_warning("خطأ", f"حدث خطأ أثناء الحذف:\n{e}")

        # أزرار الإجراءات
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15), padx=20, fill="x")

        ctk.CTkButton(
            buttons_frame,
            text="🗑️ حذف",
            command=confirm_delete,
            height=40,
            font=("Cairo", 13, "bold"),
            fg_color="#c0392b",
            hover_color="#a93226",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            buttons_frame,
            text="↩️ إلغاء",
            command=confirm_dialog.destroy,
            height=40,
            font=("Cairo", 13, "bold"),
            fg_color="white",
            hover_color="#ecf0f1",
            text_color="#e74c3c",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))


    def show_add_selected_to_list_dialog(self):
        """إضافة مجموعة منتجات مختارة بشكل احترافي"""
        if not self.selected_items:
            self._show_modern_warning("لا يوجد اختيار", "الرجاء اختيار منتج واحد على الأقل")
            return
        
        lists_data = self.data_manager.load_lists()

        # 🔧 توحيد شكل الأكواد المحفوظة من البداية
        for lst_name, items in lists_data.items():
            for item in items:
                if "template" in item:
                    code = self.get_final_code(item).strip().lower()
                    item["__final_code__"] = code

        if not lists_data:
            self._show_modern_warning("لا توجد قوائم", "لا توجد قوائم محفوظة.\nالرجاء إنشاء قائمة أولاً.")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("➕ إضافة منتجات محددة")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # توسيط النافذة
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ctk.CTkFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # معلومات المنتجات
        info_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            info_frame,
            text="📦",
            font=("Cairo", 35, "bold"),
        ).pack(pady=(10, 0))
        
        count = len(self.selected_items)

        # تنسيق النص حسب العدد
        if count == 1:
            text = "منتج واحد محدد"
        elif count == 2:
            text = "منتجان محددان"
        elif 3 <= count <= 10:
            text = f"{count} منتجات محددة"
        else:
            text = f"{count} منتج محدد"
        xt = f"{count+1}منتجات محددة " if 2 <= count <= 10 else f"{count+1}منتج محدد "

        ctk.CTkLabel(
            info_frame,
            text=text,
            font=("Cairo", 18, "bold"),
            text_color="white"
        ).pack(pady=(0, 10))
        # اختيار القائمة
        ctk.CTkLabel(
            main_frame,
            text="إضافة إلى:",
            font=("Cairo", 14, "bold"),
            anchor="e"
        ).pack(anchor="e", padx=15, pady=(15, 5))
        
        list_names = list(lists_data.keys())
        list_var = ctk.StringVar(value=list_names[0])
        
        list_menu = ctk.CTkOptionMenu(
            main_frame,
            values=list_names,
            variable=list_var,
            height=45,
            font=("Cairo", 13, "bold"),
            corner_radius=10,
            fg_color="#8e44ad",
            button_color="#7d3c98",
            button_hover_color="#6c3483"
        )
        list_menu.pack(fill="x", padx=15, pady=(0, 15))
        
        def add_and_save():
            selected_list = list_var.get()
            existing_items = lists_data[selected_list]

            # ✅ تأكيد أن الأكواد كلها lowercase للمقارنة الدقيقة
            existing_codes = {
                item.get("__final_code__", self.get_final_code(item)).strip().lower()
                for item in existing_items
            }

            added_products = []
            skipped_products = []

            for product_data in list(self.selected_items.values()):
                code = self.get_final_code(product_data).lower()
                print(f"🔹 محاولة إضافة: {product_data.get('name_ar')} (كود: {code})")

                if code in existing_codes:
                    skipped_products.append(f"{product_data['name_ar']} (كود: {code})")
                    continue

                existing_items.append(product_data)
                existing_codes.add(code)
                added_products.append(f"{product_data['name_ar']} (كود: {code})")

            # ✅ بعد ما نخلص نحدث البيانات
            self.data_manager.save_lists(lists_data)
            self.update_saved_lists_ui()
            self.selected_items.clear()
            self.update_products_list()
            dialog.destroy()

            # ✅ تشغيل المزامنة التلقائية بعد الحفظ (رفع القائمة إلى Google Sheets)
            if hasattr(self, "sync_manager") and self.sync_manager:
                threading.Thread(target=self.sync_manager.sync_all, daemon=True).start()
                print("🚀 تم رفع القوائم الجديدة تلقائيًا إلى Google Sheets.")
            else:
                print("⚠️ لم يتم تهيئة SyncManager بعد، لن يتم رفع القوائم.")

            # 🪄 إنشاء نافذة النتيجة المودرن
            result_dialog = ctk.CTkToplevel(self.root)
            result_dialog.title("📋 نتيجة العملية")
            result_dialog.geometry("480x400")
            result_dialog.transient(self.root)
            result_dialog.grab_set()

            main_frame = ctk.CTkFrame(result_dialog, corner_radius=15)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # 🟢 لو تمت الإضافة
            if added_products:
                header_text = f"✅ تمت إضافة {len(added_products)} منتج إلى '{selected_list}' بنجاح"
                header_color = "#2ecc71"
                icon = "✅"
            else:
                header_text = f"⚠️ جميع المنتجات مكررة في '{selected_list}'"
                header_color = "#95a5a6"
                icon = "⚠️"

            ctk.CTkLabel(
                main_frame,
                text=icon,
                font=("Cairo", 48, "bold"),
                text_color=header_color
            ).pack(pady=(10, 5))

            ctk.CTkLabel(
                main_frame,
                text=header_text,
                font=("Cairo", 18, "bold"),
                text_color=header_color,
                wraplength=400
            ).pack(pady=(0, 10))

            # 🧾 عرض المنتجات المضافة
            if added_products:
                added_label = ctk.CTkLabel(
                    main_frame,
                    text="🟢 المنتجات المضافة:",
                    font=("Cairo", 15, "bold"),
                    text_color="white",
                    anchor="w"
                )
                added_label.pack(anchor="w", padx=10)
                for p in added_products:
                    ctk.CTkLabel(
                        main_frame,
                        text="  • " + p,
                        font=("Cairo", 13),
                        text_color="#d0f0d0",
                        anchor="w"
                    ).pack(anchor="w", padx=20)

            # ⚠️ عرض المنتجات المكررة
            if skipped_products:
                skipped_label = ctk.CTkLabel(
                    main_frame,
                    text="\n⚠️ المنتجات المكررة:",
                    font=("Cairo", 15, "bold"),
                    text_color="#f1c40f",
                    anchor="w"
                )
                skipped_label.pack(anchor="w", padx=10)
                for p in skipped_products:
                    ctk.CTkLabel(
                        main_frame,
                        text="  • " + p,
                        font=("Cairo", 13),
                        text_color="#f9e79f",
                        anchor="w"
                    ).pack(anchor="w", padx=20)

            # زر الإغلاق
            ctk.CTkButton(
                main_frame,
                text="إغلاق",
                command=result_dialog.destroy,
                fg_color=header_color,
                hover_color="#27ae60" if added_products else "#7f8c8d",
                corner_radius=10,
                height=40,
                font=("Cairo", 14, "bold")
            ).pack(pady=(20, 10))

        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15), padx=15, fill="x")
        
        ctk.CTkButton(
            buttons_frame,
            text="✅ إضافة الكل",
            command=add_and_save,
            height=45,
            font=("Cairo", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            buttons_frame,
            text="❌ إلغاء",
            command=dialog.destroy,
            height=45,
            font=("Cairo", 14, "bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            corner_radius=10
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def create_lists_ui(self):
        """إنشاء واجهة القوائم بشكل احترافي مع شريط بحث"""
        # Header أنيق
        header_frame = ctk.CTkFrame(self.lists_frame, corner_radius=15, fg_color="#3498db")
        header_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            header_frame,
            text="📁",
            font=("Cairo", 20, "bold"),
            text_color="white"
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            header_frame,
            text="القوائم المحفوظة",
            font=("Cairo", 20, "bold"),
            text_color="white"
        ).pack(pady=(5, 15))

        # 🧭 شريط البحث عن القوائم
        search_frame = ctk.CTkFrame(self.lists_frame, fg_color="white", corner_radius=10)
        search_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.list_search_var = ctk.StringVar()
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=("Cairo", 14), text_color="#7f8c8d")
        search_icon.pack(side="right", padx=8)

        # ⚠️ لازم نعرف search_entry هنا قبل ما نستخدمه بعدين
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.list_search_var,
            placeholder_text="ابحث عن قائمة...",
            font=("Cairo", 13),
            border_width=0,
            fg_color="white",
            text_color="black",
            corner_radius=10
        )
        search_entry.pack(side="right", fill="x", expand=True, padx=(0, 8), pady=5)

        # 🎨 تأثيرات الألوان عند الفوكس والكتابة
        def on_focus_in(event):
            search_frame.configure(fg_color="#e8f6f3")
            search_icon.configure(text_color="#1abc9c")

        def on_focus_out(event):
            if not self.list_search_var.get().strip():
                search_frame.configure(fg_color="white")
                search_icon.configure(text_color="#7f8c8d")

        def on_type(*args):
            if self.list_search_var.get().strip():
                search_frame.configure(fg_color="#d6eaf8")
                search_icon.configure(text_color="#2980b9")
            else:
                search_frame.configure(fg_color="white")
                search_icon.configure(text_color="#7f8c8d")

        # 🔗 ربط الأحداث بعد تعريف search_entry
        # حفظ مراجع البحث لاستخدامها لاحقًا
        self.search_frame = search_frame
        self.search_entry = search_entry
        self.search_icon = search_icon


        # زر إنشاء قائمة جديدة
        create_list_btn = ctk.CTkButton(
            self.lists_frame,
            text="➕ إنشاء قائمة جديدة",
            command=self.create_new_list_dialog,
            height=50,
            font=("Cairo", 18, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            corner_radius=12
        )
        create_list_btn.pack(fill="x", padx=15, pady=(0, 15))

        # منطقة عرض القوائم
        self.saved_lists_frame = ctk.CTkScrollableFrame(self.lists_frame, corner_radius=15)
        self.saved_lists_frame.pack(expand=True, fill="both", padx=15, pady=(0, 15))

        # 🔍 عند الكتابة في السيرش — تحدّث القوائم
        def on_search_lists(*args):
            query = self.list_search_var.get()

            # نبدأ Thread جديد للبحث
            def search_task():
                # نحدّث القوائم في Thread جديد
                lists_data = self.data_manager.load_lists()

                # تطبيق الفلترة
                filtered = {
                    name: items
                    for name, items in lists_data.items()
                    if query.strip().lower() in name.lower()
                }

                # علشان ما نحدّثش واجهة المستخدم من Thread فرعي
                # نستخدم after لتحديث الـ UI بأمان
                self.root.after(0, lambda: self._update_lists_from_thread(filtered))

            threading.Thread(target=search_task, daemon=True).start()


        self.list_search_var.trace_add("write", on_search_lists)

        # أول تحميل للقوائم
        self.update_saved_lists_ui()



    def _update_lists_from_thread(self, filtered_lists):
        """تحديث واجهة القوائم بعد البحث (بناءً على النتائج)"""
        # نحذف المحتوى القديم
        for widget in self.saved_lists_frame.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass

        if not filtered_lists:
            empty_frame = ctk.CTkFrame(self.saved_lists_frame, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both")
            ctk.CTkLabel(empty_frame, text="📭 لا توجد نتائج مطابقة", font=("Cairo", 18, "bold"), text_color="gray").pack(pady=50)
            return

        # ألوان الكروت
        colors = ["#3498db", "#1abc9c"]

        for idx, (list_name, products) in enumerate(filtered_lists.items()):
            color = colors[idx % len(colors)]

            list_card = ctk.CTkFrame(self.saved_lists_frame, corner_radius=12, fg_color=color)
            list_card.pack(fill="x", pady=8, padx=5)

            info_frame = ctk.CTkFrame(list_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=(15, 10))

            ctk.CTkLabel(
                info_frame,
                text=f"📁 {list_name}",
                font=("Cairo", 18, "bold"),
                text_color="white"
            ).pack(anchor="center")

            ctk.CTkLabel(
                info_frame,
                text=f"{len(products)} منتج",
                font=("Cairo", 14),
                text_color="white"
            ).pack(anchor="center")

            # ✅ نفس أزرار العرض / التصدير / الحذف
            buttons_frame = ctk.CTkFrame(list_card, fg_color="transparent")
            buttons_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

            btn_style = {
                "height": 38,
                "corner_radius": 10,
                "font": ("Cairo", 13, "bold")
            }

            buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
            buttons_frame.grid_rowconfigure(0, weight=1)

            # 👁️ عرض
            ctk.CTkButton(
                buttons_frame,
                text="👁️ عرض",
                command=lambda name=list_name: self.show_list_content(name),
                fg_color="#f39c12",
                text_color=color,
                hover_color="#ecf0f1",
                **btn_style
            ).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            # 📊 تصدير
            ctk.CTkButton(
                buttons_frame,
                text="📊 تصدير",
                command=lambda name=list_name: self.export_named_list_to_excel(name),
                fg_color="white",
                text_color=color,
                hover_color="#ecf0f1",
                **btn_style
            ).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

            # 🗑️ حذف
            ctk.CTkButton(
                buttons_frame,
                text="🗑️ حذف",
                command=lambda name=list_name: self.delete_list(name),
                fg_color="#c0392b",
                hover_color="#a93226",
                text_color="white",
                **btn_style
            ).grid(row=0, column=2, padx=5, pady=5, sticky="nsew")


    def update_saved_lists_ui(self, search_query=""):
        """تحديث واجهة القوائم المحفوظة بشكل كروت مع الأزرار أسفل النصوص"""
        # تفريغ أي عناصر قديمة
        for widget in self.saved_lists_frame.winfo_children():
            widget.destroy()

        lists_data = self.data_manager.load_lists()

        # 🔍 تطبيق البحث
        if search_query:
            lists_data = {
                name: items
                for name, items in lists_data.items()
                if search_query.strip().lower() in name.lower()
            }
            
            
            # 🎨 تفاعل شريط البحث (بناءً على ما حفظناه من create_lists_ui)
        def on_focus_in(event):
            self.search_frame.configure(fg_color="#e8f6f3")
            self.search_icon.configure(text_color="#1abc9c")

        def on_focus_out(event):
            if not self.list_search_var.get().strip():
                self.search_frame.configure(fg_color="white")
                self.search_icon.configure(text_color="#7f8c8d")

        def on_type(*args):
            if self.list_search_var.get().strip():
                self.search_frame.configure(fg_color="#d6eaf8")
                self.search_icon.configure(text_color="#2980b9")
            else:
                self.search_frame.configure(fg_color="white")
                self.search_icon.configure(text_color="#7f8c8d")

        # 🔗 ربط الأحداث
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)
        self.list_search_var.trace_add("write", on_type)
        
        # 🔍 عند الكتابة في السيرش — تحدّث القوائم
        def on_search_lists(*args):
            query = self.list_search_var.get()

            # إلغاء أي مؤقت سابق (لو المستخدم بيكتب بسرعة)
            if hasattr(self, "_search_after_id"):
                self.root.after_cancel(self._search_after_id)

            # نبدأ Thread جديد بعد 300 مللي ثانية من آخر كتابة
            self._search_after_id = self.root.after(300, lambda: self._run_search_thread(query))

        self.list_search_var.trace_add("write", on_search_lists)

        if not lists_data:
            empty_frame = ctk.CTkFrame(self.saved_lists_frame, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both")

            ctk.CTkLabel(empty_frame, text="📭", font=("Cairo", 60, "bold")).pack(pady=(50, 10))
            ctk.CTkLabel(empty_frame, text="لا توجد قوائم محفوظة",
                        font=("Cairo", 18, "bold"),
                        text_color="gray").pack()
            ctk.CTkLabel(empty_frame, text="ابدأ بإنشاء قائمتك الأولى",
                        font=("Cairo", 14),
                        text_color="gray").pack(pady=5)
            return

        # ألوان الكروت
        colors = ["#3498db", "#1abc9c"]

        for idx, (list_name, products) in enumerate(lists_data.items()):
            color = colors[idx % len(colors)]

            # الكارت الأساسي
            list_card = ctk.CTkFrame(
                self.saved_lists_frame,
                corner_radius=12,
                fg_color=color
            )
            list_card.pack(fill="x", pady=8, padx=5)

            # ======= النصوص =======
            info_frame = ctk.CTkFrame(list_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=(15, 10))

            ctk.CTkLabel(
                info_frame,
                text=f"📁 {list_name}",
                font=("Cairo", 18, "bold"),
                text_color="white"
            ).pack(anchor="center")

            ctk.CTkLabel(
                info_frame,
                text=f"{len(products)} منتج",
                font=("Cairo", 14),
                text_color="white"
            ).pack(anchor="center")

            # ======= الأزرار =======
            buttons_frame = ctk.CTkFrame(list_card, fg_color="transparent")
            buttons_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

            btn_style = {
                "height": 38,
                "corner_radius": 10,
                "font": ("Cairo", 13, "bold")
            }

            # بدل pack الأفقي، نستخدم grid علشان نتحكم أفضل في التمدد
            buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)  # يخلي كل عمود يتمد بالتساوي
            buttons_frame.grid_rowconfigure(0, weight=1)  # يخلي الأزرار تتمدد عمودياً لو النافذة كبرت

            # 👁️ عرض
            btn_show = ctk.CTkButton(
                buttons_frame,
                text="👁️ عرض",
                command=lambda name=list_name: self.show_list_content(name),
                fg_color="#f39c12",
                text_color=color,
                hover_color="#ecf0f1",
                **btn_style
            )
            btn_show.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            # 📊 تصدير
            btn_export = ctk.CTkButton(
                buttons_frame,
                text="📊 تصدير",
                command=lambda name=list_name: self.export_named_list_to_excel(name),
                fg_color="white",
                text_color=color,
                hover_color="#ecf0f1",
                **btn_style
            )
            btn_export.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

            # 🗑️ حذف
            btn_delete = ctk.CTkButton(
                buttons_frame,
                text="🗑️ حذف",
                command=lambda name=list_name: self.delete_list(name),
                fg_color="#c0392b",
                hover_color="#a93226",
                text_color="white",
                **btn_style
            )
            btn_delete.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

            # ======= تحديث الحجم تلقائياً مع تغيير حجم النافذة =======
            def update_button_sizes(event):
                # ناخد عرض النافذة علشان نحدد حجم الخط والزر
                width = buttons_frame.winfo_width()
                font_size = max(10, int(width / 50))   # كل ما تكبر النافذة، الخط يكبر
                btn_height = max(30, int(width / 25))  # الارتفاع كمان يتغير بنسبة للعرض

                for btn in [btn_show, btn_export, btn_delete]:
                    btn.configure(font=("Cairo", font_size, "bold"), height=btn_height)

            # نربط التحديث مع أي تغيير في حجم النافذة
            buttons_frame.bind("<Configure>", update_button_sizes)

    def _run_search_thread(self, query):
        """تشغيل البحث في Thread منفصل"""
        def search_task():
            lists_data = self.data_manager.load_lists()
            filtered = {
                name: items
                for name, items in lists_data.items()
                if query.strip().lower() in name.lower()
            }
            # تحديث الـ UI بأمان
            self.root.after(0, lambda: self._update_lists_from_thread(filtered))

        threading.Thread(target=search_task, daemon=True).start()



    def show_list_content(self, list_name):
        """عرض محتويات قائمة بشكل احترافي جداً"""
        try:
            lists_data = self.data_manager.load_lists()
            products_in_list = lists_data.get(list_name, [])
            
            content_window = ctk.CTkToplevel(self.root)
            content_window.title(f"📁 {list_name}")
            content_window.geometry("500x600")
            content_window.transient(self.root)
            content_window.grab_set()
            
            # توسيط النافذة
            content_window.update_idletasks()
            x = (content_window.winfo_screenwidth() // 2) - (content_window.winfo_width() // 2)
            y = (content_window.winfo_screenheight() // 2) - (content_window.winfo_height() // 2)
            content_window.geometry(f"+{x}+{y}")

            # Header جذاب
            header_frame = ctk.CTkFrame(content_window, corner_radius=15, fg_color="#34495e")
            header_frame.pack(fill="x", padx=15, pady=15)
            
            ctk.CTkLabel(
                header_frame,
                text="📁",
                font=("Cairo", 40, "bold")
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                header_frame,
                text=list_name,
                font=("Cairo", 20, "bold"),
                text_color="white"
            ).pack()
            
            # عداد المنتجات (سيتم تحديثه)
            count_label = ctk.CTkLabel(
                header_frame,
                text=f"إجمالي: {len(products_in_list)} منتج",
                font=("Cairo", 13, "bold"),
                text_color="#ecf0f1"
            )
            count_label.pack(pady=(5, 15))

            # في الأعلى قبل content_frame
            search_var = ctk.StringVar()

            def on_search(*args):
                query = search_var.get().strip()
                if query:
                    filtered = [
                        p for p in self.data_manager.load_lists().get(list_name, [])
                        if query.lower() in p.get('name_ar', '').lower()
                        or query.lower() in p.get('name_en', '').lower()
                    ]
                else:
                    filtered = self.data_manager.load_lists().get(list_name, [])
                
                # تحديث المحتوى بناءً على البحث
                for widget in content_frame.winfo_children():
                    widget.destroy()
                for i, product in enumerate(filtered, 1):
                    self._create_modern_product_card(content_frame, product, i, list_name, reload_content)

            search_var.trace_add("write", on_search)
            # 🧭 إطار البحث الأنيق
            search_frame = ctk.CTkFrame(header_frame, fg_color="white", corner_radius=10)
            search_frame.pack(fill="x", padx=15, pady=(5, 10))

            # 🔍 أيقونة العدسة
            search_icon = ctk.CTkLabel(
                search_frame,
                text="🔍",
                font=("Cairo", 14),
                text_color="#7f8c8d"
            )
            search_icon.pack(side="right", padx=8)

            # 📝 حقل البحث
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=search_var,
                placeholder_text="ابحث عن منتج...",
                font=("Cairo", 13),
                border_width=0,
                fg_color="white",
                text_color="black",
                corner_radius=10
            )
            search_entry.pack(side="right", fill="x", expand=True, padx=(0, 8), pady=5)

            # إطار المحتوى
            content_frame = ctk.CTkScrollableFrame(content_window, corner_radius=15)
            content_frame.pack(expand=True, fill="both", padx=15, pady=(0, 15))
            
            # 🎨 تغيير اللون عند الفوكس
            def on_focus_in(event):
                search_frame.configure(fg_color="#e8f6f3")  # لون فاتح عند التركيز
                search_icon.configure(text_color="#1abc9c")  # العدسة تبقى خضراء

            def on_focus_out(event):
                if not search_var.get().strip():
                    search_frame.configure(fg_color="white")
                    search_icon.configure(text_color="#7f8c8d")

            def on_type(*args):
                if search_var.get().strip():
                    search_frame.configure(fg_color="#d6eaf8")  # أزرق فاتح أثناء الكتابة
                    search_icon.configure(text_color="#2980b9")
                else:
                    search_frame.configure(fg_color="white")
                    search_icon.configure(text_color="#7f8c8d")

            # 🔗 ربط الأحداث
            search_entry.bind("<FocusIn>", on_focus_in)
            search_entry.bind("<FocusOut>", on_focus_out)
            search_var.trace_add("write", on_type)

            
            # دالة لإعادة تحميل المحتوى
            def reload_content():
                for widget in content_frame.winfo_children():
                    widget.destroy()
                
                updated_lists = self.data_manager.load_lists()
                updated_products = updated_lists.get(list_name, [])
                
                # تحديث العداد
                count_label.configure(text=f"إجمالي: {len(updated_products)} منتج")
                
                if not updated_products:
                    empty_container = ctk.CTkFrame(content_frame, fg_color="transparent")
                    empty_container.pack(expand=True, fill="both")
                    
                    ctk.CTkLabel(
                        empty_container,
                        text="📭",
                        font=("Cairo", 70, "bold")
                    ).pack(pady=(80, 10))
                    
                    ctk.CTkLabel(
                        empty_container,
                        text="القائمة فارغة",
                        font=("Cairo", 18, "bold"),
                        text_color="gray"
                    ).pack()
                    
                    ctk.CTkLabel(
                        empty_container,
                        text="لا توجد منتجات في هذه القائمة",
                        font=("Cairo", 13, "bold"),
                        text_color="gray"
                    ).pack(pady=5)
                else:
                    for i, product in enumerate(updated_products, 1):
                        self._create_modern_product_card(
                            content_frame, 
                            product, 
                            i, 
                            list_name, 
                            reload_content
                        )
            
            reload_content()
                    
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في عرض محتوى القائمة: {e}")
            logging.error(f"خطأ في عرض محتوى القائمة {list_name}: {e}")

    def _create_modern_product_card(self, parent, product, index, list_name=None, reload_callback=None):
        """إنشاء كارت منتج عصري وجذاب مع زر حذف"""
        try:
            product_name = product.get('name_ar', 'غير معروف')
            product_name_en = product.get('name_en', 'Unknown')
            category = product.get('category', 'غير محددة')
            description = product.get('description', 'لا يوجد وصف')
            code = self.get_final_code(product) if hasattr(self, 'get_final_code') else 'غير محدد'

            # الكارت الرئيسي مع تدرج لوني
            gradient_colors = ["#3498db", "#2ecc71", "#f39c12", "#9b59b6"]
            card_color = gradient_colors[(index - 1) % len(gradient_colors)]
            
            # 🎨 الكارت الرئيسي مع تأثير Hover أنيق
            gradient_colors = ["#3498db", "#2ecc71", "#f39c12", "#9b59b6"]
            card_color = gradient_colors[(index - 1) % len(gradient_colors)]
            hover_color = "#5dade2" if card_color == "#3498db" else "#58d68d" if card_color == "#2ecc71" else "#f8c471" if card_color == "#f39c12" else "#af7ac5"

            product_card = ctk.CTkFrame(parent, corner_radius=12, fg_color=card_color)
            product_card.pack(pady=6, fill="x", padx=8)

            # 🖱️ تغيّر اللون عند مرور الماوس
            def on_enter(event):
                product_card.configure(fg_color=hover_color)

            def on_leave(event):
                product_card.configure(fg_color=card_color)

            product_card.bind("<Enter>", on_enter)
            product_card.bind("<Leave>", on_leave)

            # 🖱️ عند الضغط على الكارت - عرض نافذة تفاصيل المنتج
            final_code = self.get_final_code(product) if hasattr(self, "get_final_code") else "غير محدد"
            product_card.bind("<Button-1>", lambda e: self.show_product_details(
                product.get("name_en", "غير معروف"),
                product,
                final_code
            ))

            # Header الكارت
            header = ctk.CTkFrame(product_card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 8))
            
            # زر الحذف (في أقصى اليسار)
            if list_name and reload_callback:
                def delete_product():
                    confirm = ctk.CTkToplevel(parent)
                    confirm.title("⚠️ تأكيد الحذف")
                    confirm.geometry("450x400")
                    confirm.transient(parent)
                    confirm.grab_set()
                    
                    # توسيط النافذة
                    confirm.update_idletasks()
                    x = (confirm.winfo_screenwidth() // 2) - (confirm.winfo_width() // 2)
                    y = (confirm.winfo_screenheight() // 2) - (confirm.winfo_height() // 2)
                    confirm.geometry(f"+{x}+{y}")

                    frame = ctk.CTkFrame(confirm, fg_color="transparent", corner_radius=15)
                    frame.pack(fill="both", expand=True, padx=15, pady=15)

                    ctk.CTkLabel(frame, text="🗑️", font=("Cairo", 50, "bold")).pack(pady=(15, 5))
                    ctk.CTkLabel(
                        frame, 
                        text="حذف المنتج؟", 
                        font=("Cairo", 16, "bold"),
                        text_color="white"
                    ).pack()
                    ctk.CTkLabel(
                        frame, 
                        text=product_name, 
                        font=("Cairo", 12, "bold"),
                        text_color="white"
                    ).pack(pady=(5, 15))
                    
                    def confirm_delete():
                        lists_data = self.data_manager.load_lists()
                        if list_name in lists_data:
                            # البحث عن المنتج وحذفه
                            products = lists_data[list_name]
                            product_code = self.get_final_code(product)
                            
                            # حذف المنتج بناءً على الكود
                            lists_data[list_name] = [
                                p for p in products 
                                if self.get_final_code(p) != product_code
                            ]
                            
                            if self.data_manager.save_lists(lists_data):
                                self.update_saved_lists_ui()
                                self.root.update_idletasks()
                                confirm.destroy()
                                reload_callback()
                                
                                # ✅ مزامنة الحذف مع Google Sheets
                                if hasattr(self, "sync_manager") and self.sync_manager:
                                    threading.Thread(target=self.sync_manager.sync_all, daemon=True).start()
                                    print(f"🧩 تم تحديث Google Sheets بعد حذف منتج من '{list_name}'.")

                    
                    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                    btn_frame.pack(pady=(0, 15), padx=20, fill="x")
                    
                    ctk.CTkButton(
                        btn_frame, text="🗑️ حذف", command=confirm_delete,
                        fg_color="#c0392b", hover_color="#a93226",
                        height=35, corner_radius=8, font=("Cairo", 12, "bold")
                    ).pack(side="left", fill="x", expand=True, padx=(0, 5))
                    
                    ctk.CTkButton(
                        btn_frame, text="↩️ إلغاء", command=confirm.destroy,
                        fg_color="white", text_color="#e74c3c", hover_color="#ecf0f1",
                        height=35, corner_radius=8, font=("Cairo", 12, "bold")
                    ).pack(side="left", fill="x", expand=True, padx=(5, 0))
                
                delete_btn = ctk.CTkButton(
                    header,
                    text="🗑️",
                    command=delete_product,
                    width=40,
                    height=40,
                    corner_radius=20,
                    fg_color="#c0392b",
                    hover_color="#a93226",
                    font=("Cairo", 16, "bold")
                )
                delete_btn.pack(side="left", padx=(0, 10))
            
            # رقم المنتج
            number_badge = ctk.CTkFrame(header, corner_radius=20, fg_color="white", width=45, height=45)
            number_badge.pack(side="left")
            number_badge.pack_propagate(False)
            
            ctk.CTkLabel(
                number_badge,
                text=f"#{index}",
                font=("Cairo", 14, "bold"),
                text_color=card_color
            ).pack(expand=True)
            
            # اسم المنتج
            name_frame = ctk.CTkFrame(header, fg_color="transparent")
            name_frame.pack(side="right", fill="x", expand=True, padx=(10, 0))
            
            ctk.CTkLabel(
                name_frame,
                text=f"📦 {product_name}",
                font=("Cairo", 15, "bold"),
                text_color="white",
                anchor="e"
            ).pack(anchor="e")
            
            ctk.CTkLabel(
                name_frame,
                text=product_name_en,
                font=("Cairo", 11, "bold"),
                text_color="white",
                anchor="e"
            ).pack(anchor="e", pady=(2, 0))
            
            # فاصل
            separator = ctk.CTkFrame(product_card, height=2, fg_color="white")
            separator.pack(fill="x", padx=15, pady=5)
            
            # تفاصيل المنتج
            details_container = ctk.CTkFrame(product_card, fg_color="transparent")
            details_container.pack(fill="x", padx=15, pady=(5, 12))
            
            details = [
                ("🔖", "الفئة", category),
                ("💻", "الكود", code),
                ("📋", "الوصف", description[:50] + "..." if len(description) > 50 else description)
            ]
            
            for icon, label, value in details:
                detail_row = ctk.CTkFrame(details_container, fg_color="transparent")
                detail_row.pack(fill="x", pady=3)
                
                icon_label = ctk.CTkLabel(
                    detail_row,
                    text=icon,
                    font=("Cairo", 14, "bold"),
                    width=30
                )
                icon_label.pack(side="right")
                
                text_label = ctk.CTkLabel(
                    detail_row,
                    text=f"{label}: {value}",
                    font=("Cairo", 11, "bold"),
                    text_color="white",
                    anchor="e"
                )
                text_label.pack(side="right", fill="x", expand=True)
                
            
                        # ===== زر عرض التفاصيل =====
            buttons_frame = ctk.CTkFrame(product_card, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=15, pady=(5, 12))

            final_code = self.get_final_code(product) if hasattr(self, "get_final_code") else "غير محدد"

            def on_details_click(event=None):
                self.show_product_details(
                    product.get("name_en", "غير معروف"),
                    product,
                    final_code
                )

            details_btn = ctk.CTkButton(
                buttons_frame,
                text="👁️ عرض التفاصيل",
                height=38,
                corner_radius=10,
                font=("Cairo", 13, "bold"),
                fg_color="#1abc9c",
                hover_color="#16a085",
                text_color="white"
            )
            details_btn.pack(side="right", padx=(5, 0))

            # نربط الحدث Click بالزر
            details_btn.bind("<Button-1>", on_details_click)


                        
        except Exception as e:
            logging.error(f"خطأ في إنشاء كارت المنتج: {e}")
            
            # عرض بطاقة خطأ أنيقة
            error_card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#e74c3c")
            error_card.pack(pady=6, fill="x", padx=8)
            
            error_content = ctk.CTkFrame(error_card, fg_color="transparent")
            error_content.pack(pady=15)
            
            ctk.CTkLabel(
                error_content,
                text="⚠️",
                font=("Cairo", 30, "bold")
            ).pack()
            
            ctk.CTkLabel(
                error_content,
                text=f"خطأ في عرض المنتج #{index}",
                font=("Cairo", 12, "bold"),
                text_color="white"
            ).pack(pady=5)
    
    def _show_modern_success(self, title, message):
        """عرض رسالة نجاح أنيقة"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("✅")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # توسيط النافذة
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color="#2ecc71", corner_radius=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            frame,
            text="✅",
            font=("Cairo", 50, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=("Cairo", 16, "bold"),
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            frame,
            text=message,
            font=("Cairo", 12, "bold"),
            text_color="white"
        ).pack(pady=(5, 20))
        
        dialog.after(2000, dialog.destroy)
    
    def _show_modern_warning(self, title, message):
        """عرض رسالة تحذير أنيقة"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("⚠️")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # توسيط النافذة
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color="#f39c12", corner_radius=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            frame,
            text="⚠️",
            font=("Cairo", 50, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=("Cairo", 16, "bold"),
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            frame,
            text=message,
            font=("Cairo", 12, "bold"),
            text_color="white"
        ).pack(pady=(5, 15))
        
        ctk.CTkButton(
            frame,
            text="حسناً",
            command=dialog.destroy,
            fg_color="white",
            text_color="#f39c12",
            hover_color="#ecf0f1",
            height=35,
            width=100,
            corner_radius=8,
            font=("Cairo", 12, "bold")
        ).pack(pady=(0, 15))