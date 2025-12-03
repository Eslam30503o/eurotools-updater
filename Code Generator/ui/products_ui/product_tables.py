import customtkinter as ctk
from functools import partial
from tkinter import messagebox,filedialog
import tkinter as tk
import json
from pathlib import Path
from ui.history_screen import HistoryScreen
from sync.manager import SyncManager
import threading
from categories import CATEGORIES
import pyperclip
import pandas as pd

CATEGORIES = CATEGORIES

class ProductTablesMixin:
    
    def _display_products(self, filtered_data):
        """عرض المنتجات ببطاقات احترافية - يدعم dict و list"""

        # ✅ تأكد أن الإطار الخاص بالقائمة موجود (أو أعد إنشاؤه لو اختفى)
        if not hasattr(self, "products_list_frame") or not self.products_list_frame.winfo_exists():
            self.products_list_frame = ctk.CTkScrollableFrame(
                self.products_frame,
                fg_color=("gray92", "gray14"),
                corner_radius=15,
                scrollbar_button_color=("#1ABC9C", "#16A085"),
                scrollbar_button_hover_color=("#16A085", "#138D75")
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
            messagebox.showerror("خطأ", "نوع البيانات غير مدعوم في عرض المنتجات.")
            return

        # ✅ لو مفيش أدوات
        if not iterable_data:
            self._show_empty_state()
            return

        # ✅ عرض كل أداة كبطاقة احترافية
        for idx, (tool_name_en, tool_data) in enumerate(iterable_data):
            final_code = self.get_final_code(tool_data)
            self._create_premium_product_card(tool_name_en, tool_data, final_code, idx)

    def create_pagination_controls(self):
        """إنشاء أزرار التصفح بتصميم احترافي"""

        self.pagination_frame = ctk.CTkFrame(
            self.products_frame, 
            fg_color=("gray90", "gray16"),
            corner_radius=15,
            border_width=2,
            border_color=("#D5E8F0", "#2A3F54")
        )
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 15))

        inner = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        inner.pack(anchor="center", pady=15)

        # ➕ زر تحديد الكل
        select_all_btn = ctk.CTkButton(
            inner,
            text="✅ تصدير الكل",
            width=120,
            height=40,
            corner_radius=10,
            fg_color=("#27AE60", "#145A32"),
            hover_color=("#2ECC71", "#1E8449"),
            font=("Cairo", 13, "bold"),
            text_color="#FFFFFF",
            command=self.toggle_select_all
        )
        select_all_btn.pack(side="left", padx=(25, 0))



        # ⬅️ زر السابق
        prev_container = ctk.CTkFrame(
            inner,
            fg_color=("#D5F4EC", "#0B5345"),
            corner_radius=12
        )
        prev_container.pack(side="left", padx=6)
        
        self.prev_btn = ctk.CTkButton(
            prev_container,
            text="⬅️  السابق",
            width=100,
            height=40,
            command=self.go_to_prev_page,
            fg_color=("#195C4E", "#135F50"),
            hover_color=("#16A085", "#138D75"),
            font=("Cairo", 13, "bold"),
            corner_radius=10,
            text_color="#FFFFFF"
        )

        self.prev_btn.pack(padx=2, pady=2)

        # 📄 عداد الصفحات
        page_container = ctk.CTkFrame(
            inner,
            fg_color=("#ECF0F1", "#34495E"),
            corner_radius=12,
            border_width=2,
            border_color=("#BDC3C7", "#7F8C8D")
        )
        page_container.pack(side="left", padx=12)
        
        self.page_label = ctk.CTkLabel(
            page_container,
            text="صفحة 1 من 1",
            font=("Cairo", 14, "bold"),
            text_color=("#2C3E50", "#ECF0F1")
        )
        self.page_label.pack(padx=25, pady=10)

        # ➡️ زر التالي
        next_container = ctk.CTkFrame(
            inner,
            fg_color=("#D5F4EC", "#0B5345"),
            corner_radius=12
        )
        next_container.pack(side="left", padx=6)
        
        self.next_btn = ctk.CTkButton(
            next_container,
            text="التالي  ➡️",
            width=100,
            height=40,
            command=self.go_to_next_page,
            fg_color=("#08362D", "#123D34"),
            hover_color=("#16A085", "#138D75"),
            font=("Cairo", 13, "bold"),
            corner_radius=10,
            text_color="#FFFFFF"
        )
        self.next_btn.pack(padx=2, pady=2)

        # 🔢 اختيار عدد العناصر
        ctk.CTkLabel(
            inner,
            text="عدد العناصر:",
            font=("Cairo", 12, "bold"),
            text_color=("#5D6D7E", "#95A5A6")
        ).pack(side="left", padx=(25, 8))
        
        items_container = ctk.CTkFrame(
            inner,
            fg_color=("#E8DAEF", "#232B5A"),
            corner_radius=12
        )
        items_container.pack(side="left")
        
        self.items_combo = ctk.CTkOptionMenu(
            items_container,
            values=["25", "50", "75", "100"],
            command=self.change_items_per_page,
            width=100,
            height=38,
            corner_radius=10,
            fg_color=("#595FB6", "#4471AD"),
            button_color=("#4494AD", "#3C5998"),
            button_hover_color=("#3C6198", "#345083"),
            dropdown_fg_color=("#595FB6", "#44A6AD"),
            font=("Cairo", 12, "bold")
        )
        self.items_combo.set(str(self.items_per_page))
        self.items_combo.pack(padx=2, pady=2)

    def toggle_select_all(self):
        """تحديد أو إلغاء تحديد جميع العناصر"""
        if not hasattr(self, "selected_items"):
            self.selected_items = {}

        # لو الكل محدد بالفعل → نلغي التحديد
        all_selected = len(self.selected_items) == len(self._last_filtered_data or [])
        if all_selected:
            self.selected_items.clear()
        else:
            self.selected_items = {
                tool.get("final_code", f"Tool_{i+1}"): tool
                for i, tool in enumerate(self._last_filtered_data or [])
            }

            try:
                self.export_selected_to_excel()
                #df = pd.DataFrame(list(self.selected_items.values()))
                #messagebox.showinfo("تم الحفظ", f"تم حفظ {len(df)} عنصر  ")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ الملف:\n{e}")

        # # إعادة تحديث العرض لتحديث الـ CheckBoxes
        # self.update_products_display()




    def update_products_display(self):
        """عرض أو تحديث الكروت الحالية"""
        data = self._last_filtered_data or []

        def safe_get_created_at(tool):
            value = tool.get("created_at")
            try:
                return float(value) if value is not None else 0.0
            except (TypeError, ValueError):
                return 0.0

        #data.sort(key=lambda t: safe_get_created_at(t), reverse=True)
        data = list(reversed(self._last_filtered_data or []))
        total_items = len(data)
        
        if total_items == 0:
            for widget in self.products_list_frame.winfo_children():
                widget.destroy()
            self.products_count_label.configure(text=f"عدد المنتجات: 0")
            self.page_label.configure(text="صفحة 0 من 0")
            self._show_empty_state()
            return

        # حساب الصفحات والنطاق
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        self.current_page = max(0, min(self.current_page, self.total_pages - 1))

        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        visible_data = data[start:end]

        # ✅ إعادة بناء الكروت
        for w in self.products_list_frame.winfo_children():
            w.destroy()

        for idx, tool_data in enumerate(visible_data):
            tool_name_en = tool_data.get("name_en", f"Tool_{idx+1}")
            final_code = self.get_final_code(tool_data)
            self._create_premium_product_card(tool_name_en, tool_data, final_code, start + idx)
            
        self.products_list_frame.update_idletasks()
        # تحديث عداد الصفحة
        self.page_label.configure(text=f"صفحة {self.current_page + 1} من {self.total_pages}")
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if (self.current_page + 1) < self.total_pages else "disabled")

    def _update_product_card(self, card_widget, tool_data):
        """تحديث محتوى كارت موجود"""
        final_code = self.get_final_code(tool_data)
        for child in card_widget.winfo_children():
            if isinstance(child, ctk.CTkLabel) and "📦" in child.cget("text"):
                child.configure(text=f"📦 {tool_data.get('name_ar', 'غير محدد')}")
            elif isinstance(child, ctk.CTkFrame):
                for sub in child.winfo_children():
                    if isinstance(sub, ctk.CTkLabel) and "💻" in sub.cget("text"):
                        sub.configure(text=f"💻 {final_code}")

    def go_to_next_page(self):
        """انتقال للصفحة التالية"""
        if (self.current_page + 1) < self.total_pages:
            self.current_page += 1
            self.update_products_display()

    def go_to_prev_page(self):
        """انتقال للصفحة السابقة"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_products_display()

    def change_items_per_page(self, value):
        """تغيير عدد العناصر في الصفحة"""
        try:
            self.items_per_page = int(value)
        except Exception:
            self.items_per_page = 25
        self.current_page = 0
        self.update_products_display()

    def _create_premium_product_card(self, tool_name_en, tool_data, final_code, index):
        """بطاقة منتج بتصميم Ultra Premium مع تأثيرات بصرية مذهلة"""
        card_container = ctk.CTkFrame(
            self.products_list_frame,
            fg_color="transparent"
        )
        card_container.pack(padx=15, pady=12, fill="x")
        
        # 🌟 Outer glow effect
        glow_frame = ctk.CTkFrame(
            card_container,
            fg_color=("#E8F4F8", "#1A2332"),
            corner_radius=22,
            border_width=2
        )
        glow_frame.pack(fill="x", padx=2, pady=2)
        
        # # 🎨 Main card with gradient-like appearance
        card = ctk.CTkFrame(
            glow_frame,
            fg_color=("#FFFFFF", "#1E2A38"),
            corner_radius=22,
            border_width=2,
            border_color=("#D5E8F0", "#2A3F54")
        )
        card.pack(fill="x", padx=2, pady=2)

        # 🖱️ Hover effects
        def on_enter(e):
            card.configure(border_color=("#1ABC9C", "#16A085"), border_width=3)
            glow_frame.configure(fg_color=("#D5F4EC", "#0F3D30"))
        
        def on_leave(e):
            card.configure(border_color=("#D5E8F0", "#2A3F54"), border_width=2)
            glow_frame.configure(fg_color=("#E8F4F8", "#1A2332"))
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Double-Button-1>", lambda e: self.show_product_details(tool_name_en, tool_data, final_code))

        # 🎯 Content sections
        top_section = ctk.CTkFrame(card, fg_color="transparent")
        top_section.pack(fill="x", padx=28, pady=(18, 12))
        
        self._create_premium_checkbox(top_section, tool_name_en, tool_data)
        self._create_premium_product_info(top_section, tool_name_en, tool_data, final_code)
        
        # 📏 Elegant divider
        divider = ctk.CTkFrame(
            card,
            fg_color=("#E5E7E9", "#34495E"),
            height=1
        )
        divider.pack(fill="x", padx=28, pady=8)
        
        actions_section = ctk.CTkFrame(card, fg_color="transparent")
        actions_section.pack(fill="x", padx=22, pady=(8, 18))

        self._create_premium_action_buttons(actions_section, tool_name_en, tool_data, final_code)

    def _show_empty_state(self):
        """عرض شاشة فارغة احترافية"""
        try:
            empty_container = ctk.CTkFrame(
                self.products_list_frame,
                fg_color="transparent"
            )
            empty_container.pack(expand=True, fill="both", pady=80)

            appearance_mode = ctk.get_appearance_mode()

            if appearance_mode == "Dark":
                icon_bg = "#1ABC9C"
                text_main = "#ECF0F1"
                text_sub = "#BDC3C7"
                outer_glow = "#0F3D30"
            else:
                icon_bg = "#1ABC9C"
                text_main = "#2C3E50"
                text_sub = "#7F8C8D"
                outer_glow = "#E8F4F8"

            # 🌟 Glow effect
            glow = ctk.CTkFrame(
                empty_container,
                fg_color=outer_glow,
                corner_radius=120,
                width=180,
                height=180
            )
            glow.pack(pady=(0, 20))
            glow.pack_propagate(False)

            # 🎨 أيقونة كبيرة
            icon_frame = ctk.CTkFrame(
                glow,
                fg_color=icon_bg,
                corner_radius=110,
                width=160,
                height=160
            )
            icon_frame.place(relx=0.5, rely=0.5, anchor="center")
            icon_frame.pack_propagate(False)

            ctk.CTkLabel(
                icon_frame,
                text="📦",
                font=("Arial", 75)
            ).pack(expand=True)

            # 📝 النصوص
            ctk.CTkLabel(
                empty_container,
                text="لا توجد منتجات ",
                font=("Cairo", 28, "bold"),
                text_color=text_main
            ).pack(pady=(0, 10))

            ctk.CTkLabel(
                empty_container,
                text="جرب الضغط علي زر المزامنة",
                font=("Cairo", 16),
                text_color=text_sub
            ).pack()

        except Exception as e:
            print("⚠️ خطأ أثناء عرض الحالة الفارغة:", e)

    def _create_premium_checkbox(self, parent, tool_name_en, tool_data):
        """Checkbox احترافي بتصميم عصري"""
        selected_var = ctk.BooleanVar(value=tool_name_en in self.selected_items)
        
        def on_select():
            if selected_var.get():
                self.selected_items[tool_name_en] = tool_data
            else:
                self.selected_items.pop(tool_name_en, None)
        
        checkbox_container = ctk.CTkFrame(
            parent,
            corner_radius=12,
            width=50,
            height=50
        )
        checkbox_container.pack(side="left", padx=(0, 22))
        checkbox_container.pack_propagate(False)
        
        checkbox = ctk.CTkCheckBox(
            checkbox_container,
            text="",
            variable=selected_var,
            command=on_select,
            width=38,
            height=38,
            corner_radius=10,
            border_width=3,
            fg_color=("#1ABC9C", "#16A085"),
            hover_color=("#16A085", "#138D75"),
            border_color=("#398388", "#41858A"),
            checkmark_color="#FFFFFF"
        )
        checkbox.pack(expand=True)

    def _create_premium_product_info(self, parent, tool_name_en, tool_data, final_code):
        """معلومات المنتج بتنسيق Ultra Premium"""
        info_container = ctk.CTkFrame(parent, fg_color="transparent")
        info_container.pack(side="right", fill="x", expand=True)
        
        tool_name_ar = tool_data.get("name_ar", "الاسم العربي غير متوفر")
        # 🎨 الاسم الانجليزي مع أيقونة مميزة
        name_frame = ctk.CTkFrame(
            info_container,
            fg_color=("#F0F4F8", "#283747"),
            corner_radius=5
        )
        name_frame.pack(anchor="e", fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            name_frame,
            text=f"📦  {tool_data.get('name_en', 'غير محدد')}",
            font=("Cairo", 19, "bold"),
            text_color=("#1A237E", "#E8F5E9"),
            anchor="e"
        ).pack(padx=20, pady=10, side="right")
        
        # الاسم الإنجليزي والفئة في صف واحد
        details_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        details_frame.pack(anchor="e", pady=(0, 8))
        
        # 🏷️ Badge للفئة بتصميم مميز
        category_colors = {
            "BOM": ("#E74C3C", "#C0392B", "🔴"),
            "CNC Cutting Tools": ("#3498DB", "#2980B9", "⚙️"),
            "Hand Tools": ("#F39C12", "#E67E22", "🔧"),
            "Machine Spare Parts": ("#9B59B6", "#8E44AD", "⚡"),
            "Oil & Lubricants": ("#5FC5B1", "#559487", "🛢️"),
            "Stationary": ("#95A5A6", "#7F8C8D", "📎"),
            "Standard Components": ("#34495E", "#2C3E50", "🔩")
        }
        
        category = tool_data.get('category', 'غير محددة')
        cat_color, cat_hover, cat_icon = category_colors.get(category, ("#7F8C8D", "#566573", "📦"))
        
        category_badge = ctk.CTkFrame(
            details_frame,
            fg_color=cat_color,
            corner_radius=10,
            height=10
        )
        category_badge.pack(side="right", padx=(0, 10))
        
        ctk.CTkLabel(
            category_badge,
            text=f"{cat_icon}  {category}  ",
            font=("Cairo", 12, "bold"),
            text_color="#FFFFFF"
        ).pack(padx=15, pady=4)
        
        # الاسم الإنجليزي بخلفية خفيفة
        ar_name_frame = ctk.CTkFrame(
            details_frame,
            fg_color=("#ECF0F1", "#34495E"),
            corner_radius=8
        )
        ar_name_frame.pack(side="right")
        
        ctk.CTkLabel(
            ar_name_frame,
            text=f"🌐 {tool_name_ar}",
            font=("Arial", 11, "bold"),
            text_color=("#5D6D7E", "#BDC3C7")
        ).pack(padx=12, pady=4)
        
        # 🎯 اسم المشروع (إن وُجد)
        if tool_data.get("project_name"):
            project_frame = ctk.CTkFrame(
                info_container,
                fg_color=("#FEF5E7", "#7D6608"),
                corner_radius=10
            )
            project_frame.pack(anchor="e", pady=(0, 8), fill="x")
            
            ctk.CTkLabel(
                project_frame,
                text=f"🎯  مشروع او مكنة: {tool_data.get('project_name')}",
                font=("Cairo", 12, "bold"),
                text_color=("#7D6608", "#FDEBD0")
            ).pack(padx=18, pady=6, anchor="e")
        
        # 💻 الكود النهائي بتصميم Code Block احترافي
        code_frame = ctk.CTkFrame(
            info_container,
            fg_color=("#1E3A5F", "#0D1B2A"),
            corner_radius=12,
            border_width=2,
            border_color=("#3498DB", "#2874A6")
        )
        code_frame.pack(anchor="e", fill="x")
        
        code_inner = ctk.CTkFrame(code_frame, fg_color="transparent")
        code_inner.pack(fill="x", padx=3, pady=3)
        
        ctk.CTkLabel(
            code_inner,
            text="💻",
            font=("Arial", 16)
        ).pack(side="right", padx=(10, 5))
        
        ctk.CTkLabel(
            code_inner,
            text=final_code,
            font=("Consolas", 12, "bold"),
            text_color=("#5DADE2", "#AED6F1")
        ).pack(side="right", padx=(15, 0), pady=10)

        def copy_to_clipboard():
            pyperclip.copy(final_code)
            #messagebox.showinfo("تم النسخ", "تم نسخ الكود إلى الحافظة!")

        copy_button = ctk.CTkButton(
            code_inner,
            text="نسخ",
            command=copy_to_clipboard,
            width=60,
            height=30,
            corner_radius=8,
            fg_color=("#3498DB", "#2874A6"),
            hover_color=("#2980B9", "#1F618D"),
            font=("Cairo", 12, "bold"),
            text_color="#FFFFFF"
        )
        copy_button.pack(side="right", padx=(10, 0))

    def _create_premium_action_buttons(self, parent, tool_name_en, tool_data, final_code):
        """أزرار الإجراءات بتصميم Ultra Modern"""
        # الجانب الأيمن - الأزرار الرئيسية
        main_actions = ctk.CTkFrame(parent, fg_color="transparent")
        main_actions.pack(side="right")

        actions_data = [
            ("🖨️", "طباعة", "#5DADE2", "#3498DB", lambda: self.show_print_dialog(final_code)),
            #("📤", "رفع", "#58D68D", "#28B463", lambda: self.gsu.save_to_google_sheet(tool_data, final_code)),
            ("✏️", "تعديل", "#F8B739", "#F39C12", lambda: self.edit_tool_window(tool_name_en)),
            ("🗑️", "حذف", "#EC7063", "#E74C3C", lambda: self.delete_tool(tool_name_en)),
            ("👁️", "تفاصيل", "#1ABC9C", "#16A085", lambda: self.show_product_details(tool_name_en, tool_data, final_code)),
            ("➕", "إضافة للقائمة", "#201044", "#2D1252", lambda: self.show_add_to_list_dialog(tool_data)),

        ]

        for icon, text, color, hover, cmd in actions_data:
            btn = ctk.CTkButton(
                main_actions,
                text=f"{icon}  {text}",
                command=cmd,
                width=100,
                height=40,
                corner_radius=12,
                fg_color=color,
                hover_color=hover,
                font=("Cairo", 12, "bold"),
                text_color="#FFFFFF",
                border_width=0
            )
            btn.pack(side="right", padx=4)
