import customtkinter as ctk
from functools import partial
from tkinter import messagebox
import tkinter as tk
import json
from pathlib import Path
from ui.history_screen import HistoryScreen
from sync.manager import SyncManager
import threading
import time
from categories import CATEGORIES


CATEGORIES = CATEGORIES

class ProductFiltersMixin  :

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
        #self.search_entry.bind("<Return>", lambda e: self.update_products_list())
        
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
            # إلغاء أي عملية تحديث سابقة
            if hasattr(self, "_search_after_id"):
                try:
                    self.root.after_cancel(self._search_after_id)
                except Exception:
                    pass

            # تأخير تحديث القائمة 300 مللي ثانية بعد المسح
            self._search_after_id = self.root.after(3, self.update_products_list)

            # طباعة للتصحيح
            print("🧹 _clear_search: search_var =", getattr(self, "search_var", None) and self.search_var.get())

        except Exception as e:
            print("⚠️ خطأ في _clear_search:", e)

    def _on_search_change(self, *args):
        # إلغاء أي مؤقت سابق
        if hasattr(self, "_search_after_id"):
            self.root.after_cancel(self._search_after_id)

        # تأجيل التحديث نصف ثانية لتقليل الحمل
        try:
            self._search_after_id = self.root.after(500, self.update_products_list)
        except Exception:
            pass


        # 1. تحديث دالة update_products_list
    
    def update_products_list(self, category_choice=None):
        start = time.time()
        """تحديث قائمة المنتجات — يمنع تكرار الخيوط لتجنب التجميد."""
        # لو فيه Thread شغال للبحث حاليًا، تجاهله
        if getattr(self, "_filter_thread_active", False):
            print("⏳ تجاهل نداء مكرر للبحث...")
            return

        self._filter_thread_active = True

        if category_choice and self.category_filter_menu.get() != category_choice:
            self.category_filter_menu.set(category_choice)

        def run_in_background():
            try:
                tools_data = self.data_manager.load_tools()
                filtered_data = self._get_filtered_products(tools_data)
                count = len(filtered_data)
                self.root.after(0, lambda: self._finalize_ui_update(filtered_data, count))
            except Exception as e:
                print(f"⚠️ خطأ في خيط التصفية: {e}")
            finally:
                # بعد الانتهاء من البحث — اسمح باستدعاء جديد
                self._filter_thread_active = False

        threading.Thread(target=run_in_background, daemon=True).start()

        print("⏱️ التصفية استغرقت:", time.time() - start, "ثانية")
        # 2. إضافة دالة _run_filtering_and_display لتنفيذ العمل في الخلفية
    
    def _run_filtering_and_display(self):
        try:           
            tools_data = self.data_manager.load_tools()           
            filtered_data = self._get_filtered_products(tools_data)           
            count = len(filtered_data)           
            self.root.after(0, lambda: self._finalize_ui_update(filtered_data, count))

        except Exception as e:
            print(f"خطأ في خيط التصفية: {e}")

    def _get_filtered_products(self, tools_data):
        """الحصول على المنتجات المفلترة (يدعم list و dict)"""
        search_query = self.search_var.get().strip().lower()
        selected_category = self.category_filter_menu.get().strip()

        #print(f"🔍 البحث: '{search_query}' | الفئة: '{selected_category}'")
        #print(f"✅ get_final_code متاحة: {hasattr(self, 'get_final_code')}")

        # 1. تهيئة البيانات: تحويل أي dict إلى list
        if isinstance(tools_data, dict):
            tools_list = list(tools_data.values())
            #print(f"📊 تم تحويل dict إلى list: {len(tools_list)} عنصر")
        elif isinstance(tools_data, list):
            tools_list = tools_data
            #print(f"📊 البيانات list: {len(tools_list)} عنصر")
        else:
            tools_list = []
            print("❌ نوع البيانات غير معروف")

        current_data = tools_list

        # 2. 🔎 فلترة حسب الفئة (Category Filter)
        if selected_category != "All":
            original_count = len(current_data)
            current_data = [
                t for t in current_data
                if t.get("category", "").strip().lower() == selected_category.lower()
            ]
            #print(f"🏷️ بعد فلترة الفئة [{selected_category}]: {original_count} → {len(current_data)}")

        # 3. 🔍 فلترة حسب البحث النصي (Text Search Filter)
        if search_query:
            original_count = len(current_data)
            #print(f"🔤 تطبيق البحث النصي: '{search_query}'")
            
            filtered_results = []
            for i, tool in enumerate(current_data):
                name_en = tool.get("name_en", f"tool_{i}")
                if self._matches_search(name_en, tool, search_query):
                    filtered_results.append(tool)
            
            current_data = filtered_results
            #print(f"📈 بعد البحث النصي: {original_count} → {len(current_data)}")
        
        #print(f"✅ النتيجة النهائية: {len(current_data)} منتج مطابق")
        # ✅ ترتيب حسب أحدث تعديل
        
        current_data.sort(key=lambda t: t.get("updated_at", 0), reverse=True)
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

