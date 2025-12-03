import customtkinter as ctk
from tkinter import messagebox
import json
import os
import platform
import threading
from pathlib import Path
import operator

from sync.sync_items_form import SyncManager_form
from data_manager import DataManager


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


if platform.system() == "Windows":
    base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "EuroTools" / "data"
else:
    base_dir = Path.home() / ".local" / "share" / "EuroTools" / "data"

base_dir.mkdir(parents=True, exist_ok=True)
DATA_FILE = base_dir / "items_data.json"


# =================== Modern Color Palette ===================
COLORS = {
    "primary": "#6366f1",       # Indigo
    "primary_hover": "#4f46e5",
    "secondary": "#8b5cf6",     # Purple
    "success": "#10b981",       # Green
    "success_hover": "#059669",
    "danger": "#ef4444",        # Red
    "danger_hover": "#dc2626",
    "warning": "#f59e0b",       # Orange
    "info": "#3b82f6",          # Blue
    "dark_bg": "#0f172a",       # Slate 900
    "card_bg": "#1e293b",       # Slate 800
    "card_hover": "#334155",    # Slate 700
    "border": "#475569",        # Slate 600
    "text": "#f1f5f9",          # Slate 100
    "text_muted": "#ffffff",    # Slate 400
}


class SearchableDropdown(ctk.CTkFrame):
    def __init__(self, parent, values, width=200, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.values = values
        self.width = width
        self.selected_value = None
        self.dropdown_visible = False

        # Modern Entry with gradient effect
        self.entry = ctk.CTkEntry(
            self, 
            width=self.width, 
            placeholder_text="🔍 اضغط للبحث...",
            height=40,
            corner_radius=12,
            border_width=2,
            border_color=COLORS["border"],
            fg_color=COLORS["card_bg"],
            text_color=COLORS["text"]
        )
        self.entry.pack(pady=(0, 2))
        self.entry.bind("<KeyRelease>", self.filter_list)
        self.entry.bind("<Button-1>", self.show_list)
        self.entry.bind("<FocusOut>", self.schedule_hide)

        # إنشاء Toplevel للـ dropdown
        self.dropdown_window = None

    def schedule_hide(self, event=None):
        """تأخير الإخفاء للسماح بالنقر على العناصر"""
        self.after(20, self.hide_list)

    def show_list(self, event=None):
        if self.dropdown_visible:
            return
            
        # إنشاء نافذة منبثقة
        self.dropdown_window = ctk.CTkToplevel(self)
        self.dropdown_window.withdraw()  # إخفاء مؤقت
        self.dropdown_window.overrideredirect(True)  # بدون إطار النافذة
        
        # حساب الموقع
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
        
        self.dropdown_window.geometry(f"+{x}+{y}")
        
        # Frame المحتوى
        self.dropdown_frame = ctk.CTkScrollableFrame(
            self.dropdown_window,
            fg_color=COLORS["card_bg"],
            corner_radius=12,
            border_width=2,
            border_color=COLORS["border"],
            width=self.width - 10,
            height=min(5, 10)
        )
        self.dropdown_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.populate_list(self.values)
        
        # إظهار النافذة
        self.dropdown_window.deiconify()
        self.dropdown_visible = True
        
        # ربط إغلاق النافذة
        self.dropdown_window.bind("<FocusOut>", lambda e: self.hide_list())

    def hide_list(self):
        if self.dropdown_window and self.dropdown_visible:
            try:
                self.dropdown_window.destroy()
                self.dropdown_window = None
                self.dropdown_visible = False
            except:
                pass

    def populate_list(self, data):
        if not hasattr(self, "dropdown_frame") or self.dropdown_frame is None:
            return
            
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()
            
        for item in data:
            btn = ctk.CTkButton(
                self.dropdown_frame,
                text=item,
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=COLORS["text"],
                hover_color=COLORS["primary"],
                anchor="w",
                command=lambda i=item: self.select_value(i)
            )
            btn.pack(fill="x", pady=2, padx=5)

                
    def filter_list(self, event=None):
        if not self.dropdown_visible:
            self.show_list()
            
        search = self.entry.get().lower()
        filtered = [val for val in self.values if search in val.lower()]
        self.populate_list(filtered if filtered else ["❌ لا توجد نتائج"])

    def select_value(self, value):
        if value != "❌ لا توجد نتائج":
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
            self.selected_value = value
        self.hide_list()

    def get(self):
        return self.selected_value


class ModernButton(ctk.CTkButton):
    """Custom modern button with enhanced styling"""
    def __init__(self, parent, icon="", **kwargs):
        defaults = {
            "corner_radius": 12,
            "height": 45,
            "font": ("Cairo", 14, "bold"),
            "border_width": 0,
        }
        defaults.update(kwargs)
        
        if icon:
            defaults["text"] = f"{icon} {defaults.get('text', '')}"
        
        super().__init__(parent, **defaults)


class DynamicFormApp(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS["dark_bg"])
        self.pack(fill="both", expand=True)
        
        # Data Manager & Sync
        self.dm = DataManager()
        self.creds_path = self.dm.SYNC_FILE
        self.sync_manager = SyncManager_form(
            self.creds_path, 
            filter_callback=self.filter_items, 
            ui_root=self
        )

        self.init_ui()
        self.data = self.load_data()
        self.items_per_page = 10
        self.current_page = 1
        self.filtered_items = []

    def init_ui(self):
        # =================== Header Bar ===================
        header = ctk.CTkFrame(self, height=80, fg_color=COLORS["card_bg"], corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Logo/Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=15)
        
        ctk.CTkLabel(
            title_frame,
            text="⚡ Items Form",
            font=("Cairo", 28, "bold"),
            text_color=COLORS["primary"]
        ).pack(fill="y")
        
        # ctk.CTkLabel(
        #     title_frame,
        #     text="إدارة العناصر والخصائص بشكل احترافي",
        #     font=("Cairo", 12),
        #     text_color=COLORS["text_muted"]
        # ).pack(anchor="w")

        # Main Container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # =================== Left Panel - Items List ===================
        left_panel = ctk.CTkFrame(
            main_container, 
            fg_color=COLORS["card_bg"],
            corner_radius=20,
            border_width=1,
            border_color=COLORS["border"]
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Search Bar with modern design
        search_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_container.pack(fill="x", padx=20, pady=20)

        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="🔍 ابحث عن العناصر...",
            height=50,
            corner_radius=15,
            border_width=2,
            border_color=COLORS["border"],
            fg_color=COLORS["dark_bg"],
            font=("Cairo", 14)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_items)

        # Add Item Button - Modern Style
        self.add_item_button = ModernButton(
            search_container,
            text="إضافة",
            icon="➕",
            width=120,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=self.show_add_item_panel
        )
        self.add_item_button.pack(side="left")

        # Items Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            corner_radius=15
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # =================== Right Panel - Input Panel ===================
        self.right_panel = ctk.CTkFrame(
            main_container,
            width=420,
            fg_color=COLORS["card_bg"],
            corner_radius=20,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.right_panel.pack_propagate(False)

        # Panel Header
        panel_header = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=70)
        panel_header.pack(fill="x", padx=20, pady=(20, 10))
        panel_header.pack_propagate(False)

        self.input_panel_title = ctk.CTkLabel(
            panel_header,
            text="📝 لوحة الإدخال",
            font=("Cairo", 22, "bold"),
            text_color=COLORS["text"]
        )
        self.input_panel_title.pack(side="left", anchor="w")

        close_btn = ctk.CTkButton(
            panel_header,
            text="✖",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            font=("Cairo", 16, "bold"),
            command=self.hide_input_panel
        )
        close_btn.pack(side="right")

        # Separator Line
        ctk.CTkFrame(
            self.right_panel, 
            height=2, 
            fg_color=COLORS["border"]
        ).pack(fill="x", padx=20, pady=10)

        # Content Frame
        self.input_content_frame = ctk.CTkScrollableFrame(
            self.right_panel,
            fg_color="transparent"
        )
        self.input_content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.items_data = {}
        self.panel_visible = False
        self.load_data()

    def show_input_panel(self):
        if not self.panel_visible:
            self.right_panel.pack(side="right", fill="both", padx=(0, 0), pady=0)
            self.panel_visible = True

    def hide_input_panel(self):
        if self.panel_visible:
            self.right_panel.pack_forget()
            self.panel_visible = False

    def clear_input_panel(self):
        for widget in self.input_content_frame.winfo_children():
            widget.destroy()

    def create_modern_label_entry(self, parent, label_text, placeholder=""):
        """Helper to create modern label + entry combo"""
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Cairo", 14, "bold"),
            text_color=COLORS["text"]
        ).pack(pady=(15, 5), anchor="w")

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=45,
            corner_radius=12,
            border_width=2,
            border_color=COLORS["border"],
            fg_color=COLORS["dark_bg"],
            font=("Cairo", 13)
        )
        entry.pack(fill="x", pady=(0, 10))
        return entry

    def show_add_item_panel(self):
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text="➕ إضافة عنصر جديد")

        english_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "📝 الاسم بالإنجليزية:",
            "English name (A-Z only)"
        )
        english_entry.focus()

        arabic_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "📝 الاسم بالعربية:",
            "الاسم العربي"
        )

        # Modern Button Frame
        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="x")

        def add_item():
            arabic_name = arabic_entry.get().strip()
            english_name = english_entry.get().strip()

            if not arabic_name or not english_name:
                messagebox.showwarning("⚠️ تنبيه", "من فضلك أدخل الاسمين!")
                return

            # if not english_name.replace(" ", "").isalpha():
            #     messagebox.showwarning("⚠️ تنبيه", "الاسم الإنجليزي يجب أن يحتوي على حروف فقط!")
            #     return

            for key, data in self.items_data.items():
                if key.lower() == english_name.lower() and data.get("arabic_name") == arabic_name:
                    messagebox.showwarning("⚠️ تنبيه", "الاسمين مكررين!")
                    return
                elif key.lower() == english_name.lower():
                    messagebox.showwarning("⚠️ تنبيه", "الاسم الانجليزي متكرر!")
                    return
                elif data.get("arabic_name") == arabic_name:
                    messagebox.showwarning("⚠️ تنبيه", "الاسم العربي متكرر!")
                    return

            self.items_data[english_name] = {
                "arabic_name": arabic_name,
                "properties": [],
                "code_template": "",
                "code_template_2":""
            }

            self.save_data()
            #self.filter_items()

            new_item_frame = self.create_item_frame(english_name, insert_at_top=True)
            self.show_property_type_panel(new_item_frame, english_name)

        ModernButton(
            btn_frame,
            text="إضافة",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=add_item
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

    def create_item_frame(self, item_name, insert_at_top=False):
        """Create modern card for each item"""
        # Modern Card Container
        item_frame = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=16,
            fg_color=COLORS["card_bg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        
        children = self.scroll_frame.winfo_children()
        if insert_at_top and len(children) > 0:
            try:
                first_child = children[0]
                if first_child.winfo_manager():
                    item_frame.pack(fill="x", pady=8, before=first_child)
                else:
                    item_frame.pack(fill="x", pady=8)
            except:
                item_frame.pack(fill="x", pady=8)
        else:
            item_frame.pack(fill="x", pady=8)

        # Header with gradient-like effect
        header_frame = ctk.CTkFrame(
            item_frame,
            fg_color=COLORS["primary"],
            corner_radius=15,
            height=70
        )
        header_frame.pack(fill="x", padx=3, pady=3)
        header_frame.pack_propagate(False)

        # Get names
        english_name = item_name
        arabic_name = self.items_data[item_name].get("arabic_name", item_name)
        
        # Title Section
        title_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_section.pack(side="left", fill="both", expand=True, padx=20)

        ctk.CTkLabel(
            title_section,
            text=english_name,
            font=("Cairo", 18, "bold"),
            text_color="white",
            anchor="w"
        ).pack(anchor="w", pady=(10, 0))

        ctk.CTkLabel(
            title_section,
            text=f"🏷️ {arabic_name}",
            font=("Cairo", 12),
            text_color="#ffffff",
            anchor="w"
        ).pack(anchor="w")

        # Action Buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=15)

        btn_style = {
            "width": 40,
            "height": 40,
            "corner_radius": 10,
            "font": ("Cairo", 16),
            "border_width": 0
        }

        # Content Area (يجب إنشاؤه قبل زر الإخفاء)
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        content_frame.pack_forget()  # ✅ إخفاء الخصائص عند التشغيل

        # زر إخفاء/إظهار المحتوى
        toggle_btn = ctk.CTkButton(
            actions_frame,
            text="🔽",
            fg_color="#f59e0b",
            hover_color="#d97706",
            **btn_style
        )
        toggle_btn.pack(side="left", padx=2)

        # دالة إخفاء/إظهار
        def toggle_content():
            if content_frame.winfo_viewable():
                content_frame.pack_forget()
                toggle_btn.configure(text="🔽")
            else:
                content_frame.pack(fill="both", expand=True, padx=15, pady=15)
                toggle_btn.configure(text="🔼")

        toggle_btn.configure(command=toggle_content)

        # ctk.CTkButton(
        #     actions_frame,
        #     text="Code 🧩",
        #     fg_color="#8b5cf6",
        #     hover_color="#7c3aed",
        #     command=lambda: self.show_edit_code_panel(item_name),
        #     **btn_style
        # ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame,
            text="➕ إضافة خاصية",
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=lambda: self.show_property_type_panel(item_frame, item_name),
            **btn_style
        ).pack(side="left", padx=2)


        ctk.CTkButton(
            actions_frame,
            text="Edit✏️",
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=lambda: self.show_rename_item_panel(item_name),
            **btn_style
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame,
            text="🗑️",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=lambda: self.delete_item(item_name, item_frame),
            **btn_style
        ).pack(side="left", padx=2)

        # Add Property Button
        ModernButton(
            content_frame,
            text="إضافة خاصية",
            icon="➕",
            height=40,
            fg_color=COLORS["secondary"],
            hover_color="#7c3aed",
            command=lambda: self.show_property_type_panel(item_frame, item_name)
        ).pack(fill="x", pady=(0, 15))




        # Properties Container
        properties_frame = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["dark_bg"],
            corner_radius=12
        )
        properties_frame.pack(fill="x", pady=(0, 15))

        if item_name in self.items_data:
            for prop in self.items_data[item_name]["properties"]:
                self.add_property_frame(
                    properties_frame,
                    item_name,
                    prop['name'],
                    prop['type'],
                    prop.get('values'),
                    prop.get('data_type')
                )

        # Code Preview Section
        code_section = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["dark_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        code_section.pack(fill="x")

        ctk.CTkLabel(
            code_section,
            text="💻 الكود المُنشأ",
            font=("Cairo", 14, "bold"),
            text_color=COLORS["primary"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        code_display = ctk.CTkTextbox(
            code_section,
            height=40,
            corner_radius=8,
            fg_color="#0a0f1e",
            text_color="#a5f3fc",
            font=("Consolas", 12),
            wrap="word"
        )
        code_display.pack(fill="both", padx=10, pady=(0, 10))
        
        current_code = self.items_data[item_name].get("code_template", " لا يوجد كود بعد")
        code_display.insert("1.0", current_code)
        code_display.configure(state="normal") #disabled

        def save_inline_code(event=None):
            new_code = code_display.get("1.0", "end-1c").strip()
            self.items_data[item_name]["code_template"] = new_code
            self.save_data()
            messagebox.showinfo("تم", "تم حفظ  الكود")
            content_frame.pack_forget()
            return "break"  

        code_display.bind("<Return>", save_inline_code)


        item_frame.properties_frame = properties_frame
        return item_frame

    def add_property_frame(self, parent_frame, item_name, prop_name, prop_type, values=None, data_type=None):
        """Create modern property frame"""
        if not parent_frame.winfo_exists():
            return  # أو يمكنك إعادة بناء الإطار تلقائيًا

        # ===================== تحديد الـ origin =====================
        origin = "natural"
        condition_data = None
        for p in self.items_data[item_name]["properties"]:
            if p["name"] == prop_name:
                origin = p.get("origin", "natural")
                condition_data = p
                break

        # ===================== شكل الخاصية حسب origin =====================
        display_name = prop_name
        if origin == "condition":
            display_name = f"{prop_name} ⚡"   # تمييز خاصية condition

        
        prop_frame = ctk.CTkFrame(
            parent_frame,
            fg_color=COLORS["card_bg"],
            corner_radius=15,
            height=50
        )
        prop_frame.pack(fill="x", pady=2, padx=(5,5))
        prop_frame.pack_propagate(False)

        # Label
        label = ctk.CTkLabel(
            prop_frame,
            text=f"🔹 {display_name}",
            font=("Cairo", 13, "bold"),
            width=50,
            anchor="w"
        )
        label.pack(side="left", padx=15)


        # Action Buttons
        btns_frame = ctk.CTkFrame(prop_frame, fg_color="transparent")
        btns_frame.pack(side="right", padx=(5), pady=5)

        ctk.CTkButton(
            btns_frame,
            text="✏️",
            width=35,
            height=35,
            corner_radius=10,
            fg_color=COLORS["info"],
            hover_color="#2563eb",
            command=lambda: self.show_edit_property_panel(prop_frame, item_name, prop_name, prop_type, values)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btns_frame,
            text="🗑️",
            width=35,
            height=35,
            corner_radius=10,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=lambda: self.delete_property(prop_frame, item_name, prop_name)
        ).pack(side="left", padx=2)



        # Input Field
        if prop_type == "entry":
            entry = ctk.CTkEntry(
                prop_frame,
                placeholder_text=f"{prop_name} أدخل ",
                height=30,
                corner_radius=15,
                border_width=1,
                border_color=COLORS["border"]
            )
            entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            def validate_input(new_value):
                if data_type == "letters":
                    return new_value.isalpha() or new_value == ""
                elif data_type == "int":
                    return new_value.isdigit() or new_value == ""
                elif data_type == "float":
                    if new_value in ("", "-", ".", "-."):
                        return True
                    try:
                        float(new_value)
                        return True
                    except ValueError:
                        return False
                return True

            entry.configure(validate="key", validatecommand=(self.register(validate_input), "%P"))
        
        elif prop_type == "dropdown":
            dropdown = SearchableDropdown(prop_frame, values=values, width=200)
            dropdown.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # elif prop_type == "Condition":

        #     # =========== الإطار الخارجي =============
        #     condition_frame = ctk.CTkFrame(
        #         prop_frame,
        #         fg_color=COLORS["dark_bg"],
        #         corner_radius=15
        #     )
        #     condition_frame.pack(fill="x", padx=(0, 10), pady=5)

        #     # ---------------- الحصول على بيانات ال Condition ----------------
        #     condition_data = None
        #     for p in self.items_data[item_name]["properties"]:
        #         if p["name"] == prop_name:
        #             condition_data = p
        #             break

        #     if not condition_data:
        #         return

        #     # ---------------- الصف الأول: الخاصية + الشرط + القيمة ----------------
        #     row1 = ctk.CTkFrame(condition_frame, fg_color="transparent")
        #     row1.pack(fill="x", padx=10, pady=(5, 2))

        #     ctk.CTkLabel(
        #         row1,
        #         text=f"📌 الخاصية: {condition_data.get('property', '')}",
        #         font=("Cairo", 12),
        #         text_color=COLORS["info"]
        #     ).pack(side="left", padx=10)

        #     # رمز الشرط
        #     condition_symbols = {
        #         '==': '⚖️',
        #         '!=': '❌',
        #         '>': '📈',
        #         '<': '📉',
        #         '>=': '🔼',
        #         '<=': '🔽'
        #     }
        #     icon = condition_symbols.get(condition_data.get("condition", ""), "❓")

        #     ctk.CTkLabel(
        #         row1,
        #         text=f"{icon} {condition_data.get('condition', '')} {condition_data.get('value', '')}",
        #         font=("Cairo", 14, "bold"),
        #         text_color=COLORS["primary"]
        #     ).pack(side="left", padx=10)

        #     # ---------------- الصف الثاني: النتيجة (Action) ----------------
        #     row2 = ctk.CTkFrame(condition_frame, fg_color="transparent")
        #     row2.pack(fill="x", padx=10, pady=(2, 10))

        #     if_action = condition_data.get("if_action")
        #     if not if_action:
        #         ctk.CTkLabel(
        #             row2,
        #             text="لا يوجد Action",
        #             font=("Cairo", 11),
        #             text_color=COLORS["danger"]
        #         ).pack(side="left", padx=10)
        #     else:
        #         action_type = if_action.get("action")
        #         action_text = ""
        #         color = COLORS["primary"]

        #         # ترجمة أكشناتك
        #         if action_type == "add_property_edit_code":
        #             action_text = f"➕ إضافة خاصية + تعديل الكود: {if_action.get('prop_name', '')}"
        #             color = COLORS["success"]

        #         elif action_type == "add_property":
        #             action_text = f"➕ إضافة خاصية: {if_action.get('prop_name', '')}"
        #             color = COLORS["info"]

        #         elif action_type == "edit_code":
        #             action_text = "💻 تعديل الكود"
        #             color = COLORS["secondary"]

        #         ctk.CTkLabel(
        #             row2,
        #             text=action_text,
        #             font=("Cairo", 11, "bold"),
        #             text_color=color
        #         ).pack(side="left", padx=10)

        #         # حالة التنفيذ (ثابتة أو حتخليها متغيرة)
        #         ctk.CTkLabel(
        #             row2,
        #             text="⚡ Condition",
        #             font=("Cairo", 12),
        #             text_color=COLORS["warning"]
        #         ).pack(side="left", padx=10)

        elif prop_type == "Condition":

            # الإطار الخارجي
            condition_frame = ctk.CTkFrame(
                prop_frame,
                fg_color=COLORS["dark_bg"],
                corner_radius=15
            )
            condition_frame.pack(fill="x", padx=(0, 10), pady=5)

            # الحصول على بيانات الـ Condition
            condition_data = None
            for p in self.items_data[item_name]["properties"]:
                if p["name"] == prop_name:
                    condition_data = p
                    break

            if not condition_data:
                return

            # جمع بيانات الـ Condition
            prop_type_text = "condition"
            action_data = condition_data.get("if_action", {})
            condition_type = condition_data.get("condition", "")
            condition_value = condition_data.get("value", "")

            # بناء نص الـ Action و الـ Result
            action_type = action_data.get("action", "")
            result_text = ""

            if action_type == "add_property_edit_code":
                new_prop = action_data.get("prop_name", "")
                new_code =  self.items_data[item_name].get("code_template_2", "")  # افترض وجود هذا المفتاح للكود الجديد
                result_text = f"➕  {new_prop}  | اسم الخاصية : {new_code} الكود : "
            elif action_type == "add_property":
                new_prop = action_data.get("prop_name", "")
                result_text = f"➕ {new_prop} اسم الخاصية:"
            elif action_type == "edit_code":
                new_code = self.items_data[item_name].get("code_template_2", "")  # افترض وجود هذا المفتاح للكود الجديد
                result_text = f"💻 {new_code} الكود:"
            else:
                result_text = "لا يوجد إجراء معروف"

            # عرض المعلومات كاملة في Label واحد أو عدة Labels حسب التصميم
            info_text = (
                f"Action: {action_type}  |  "
                f"Condition: {condition_type}  |  "
                f"Value: {condition_value}  |  "
                f"Result: {result_text}"
            )

            ctk.CTkLabel(
                condition_frame,
                text=info_text,
                font=("Cairo", 13),
                text_color="#ffee00",
                wraplength=prop_frame.winfo_width() - 40  # لتجنب القص لو طويل
            ).pack(padx=10, pady=10)


        else :
            ctk.CTkLabel(
                prop_frame,
                text="نوع غير معروف",
                text_color=COLORS["danger"],
                font=("Cairo", 13, "bold")
            ).pack(side="left", padx=10)




    def show_edit_code_panel(self, item_name):
        """Modern code editor panel"""
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text=f"💻 تعديل الكود: {item_name}")

        current_code = self.items_data[item_name].get("code_template", "")

        ctk.CTkLabel(
            self.input_content_frame,
            text="✨ استخدم {اسم_الخاصية} كمتغيرات",
            font=("Cairo", 13),
            text_color=COLORS["text_muted"]
        ).pack(pady=(5, 10), anchor="w")

        code_box = ctk.CTkTextbox(
            self.input_content_frame,
            height=30,
            corner_radius=12,
            fg_color=COLORS["dark_bg"],
            border_width=2,
            border_color=COLORS["border"],
            font=("Consolas", 13),
            wrap="none"
        )
        code_box.insert("1.0", current_code)
        code_box.pack(fill="both", expand=True, pady=10)

        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=15, fill="x")

        def save_code():
            new_code = code_box.get("1.0", "end").strip()
            self.items_data[item_name]["code_template"] = new_code
            self.hide_input_panel()

            self.save_data()
            item_data = self.items_data[item_name]
            threading.Thread(target=lambda: self.sync_manager.update_item_in_google(item_name, item_data),
                daemon=True
                ).start() 
            self.filter_items()
           

        ModernButton(
            btn_frame,
            text="حفظ",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=save_code
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

    def show_edit_code_panel_2(self, item_name):
        """لوحة تحرير الكود الثاني لكل عنصر"""
        # self.show_input_panel()
        # self.clear_input_panel()
        # self.input_panel_title.configure(text=f"💻 إضافة/تعديل الكود الثاني: {item_name}")

        # الكود الحالي للكود الثاني إذا موجود
        current_code = self.items_data[item_name].get("code_template_2", "")

        ctk.CTkLabel(
            self.input_content_frame,
            text="✨ استخدم {اسم_الخاصية} كمتغيرات",
            font=("Cairo", 13),
            text_color=COLORS["text_muted"]
        ).pack(pady=(5, 10), anchor="w")

        code_box = ctk.CTkTextbox(
            self.input_content_frame,
            height=30,
            corner_radius=12,
            fg_color=COLORS["dark_bg"],
            border_width=2,
            border_color=COLORS["border"],
            font=("Consolas", 13),
            wrap="none"
        )
        code_box.insert("1.0", current_code)
        code_box.pack(fill="both", expand=True, pady=10)

        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=15, fill="x")

        def save_code_2():

            new_code = code_box.get("1.0", "end-1c").strip()
            self.items_data[item_name]["code_template_2"] = new_code
            self.hide_input_panel()
            self.save_data()
            self.sync_manager.update_item_in_google(item_name, self.items_data[item_name].copy())
            self.filter_items()

        ModernButton(
            btn_frame,
            text="حفظ",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=save_code_2
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

    def show_rename_item_panel(self, old_name):
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text="✏️ تعديل العنصر")

        current_data = self.items_data[old_name]
        
        english_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "📝 الاسم بالإنجليزية:",
            ""
        )
        english_entry.insert(0, old_name)
        english_entry.focus()

        arabic_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "📝 الاسم بالعربية:",
            ""
        )
        arabic_entry.insert(0, current_data.get("arabic_name", ""))

        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="x")

        def rename():
            new_english = english_entry.get().strip()
            new_arabic = arabic_entry.get().strip()
            
            if not new_arabic or not new_english:
                messagebox.showwarning("⚠️ تنبيه", "أدخل الاسمين!")
                return

            # if not new_english.replace(" ", "").isalpha():
            #     messagebox.showwarning("⚠️ تنبيه", "الاسم الإنجليزي حروف فقط!")
            #     return

            for key, data in self.items_data.items():
                if key.lower() == new_english.lower() and key != old_name:
                    messagebox.showwarning("⚠️ تنبيه", "الاسم موجود!")
                    return

            item_data = self.items_data.pop(old_name)
            item_data["arabic_name"] = new_arabic
            self.items_data[new_english] = item_data

            self.hide_input_panel()
            self.save_data()
            threading.Thread(
                target=lambda: self.sync_manager.update_item_in_google(new_english, item_data),
                daemon=True
            ).start()
            self.filter_items()
            
        ModernButton(
            btn_frame,
            text="حفظ",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=rename
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

    def show_property_type_panel(self, parent_frame, item_name):
        self.clear_input_panel()
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text="🎯 اختر نوع الخاصية")

        ctk.CTkLabel(
            self.input_content_frame,
            text="اختر نوع الحقل المناسب:",
            font=("Cairo", 14),
            text_color=COLORS["text_muted"]
        ).pack(pady=20)

        ModernButton(
            self.input_content_frame,
            text="Entry",
            icon="📝",
            height=60,
            fg_color=COLORS["info"],
            hover_color="#2563eb",
            command=lambda: self.show_add_property_panel(parent_frame, item_name, "entry")
        ).pack(fill="x", pady=10)

        ModernButton(
            self.input_content_frame,
            text="Dropdown",
            icon="🔽",
            height=60,
            fg_color=COLORS["secondary"],
            hover_color="#7c3aed",
            command=lambda: self.show_add_property_panel(parent_frame, item_name, "dropdown")
        ).pack(fill="x", pady=10)

        ModernButton(
            self.input_content_frame,
            text="Condition",
            icon="📑",
            height=60,
            fg_color=COLORS["info"],
            hover_color="#074132",
            command=lambda: self.show_add_property_panel(parent_frame, item_name, "Condition")
        ).pack(fill="x", pady=10)


        ModernButton(
            self.input_content_frame,
            text="إلغاء",
            icon="❌",
            height=50,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(fill="x", pady=20)

    def show_add_property_panel(self, parent_frame, item_name, prop_type):
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text=f"➕ إضافة خاصية ({prop_type})")

        prop_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "🏷️ اسم الخاصية:",
            "اسم الخاصية"
        )
        prop_entry.focus()

        data_type_var = None
        values_entry = None

        if prop_type == "entry":
            ctk.CTkLabel(
                self.input_content_frame,
                text="📊 نوع البيانات:",
                font=("Cairo", 14, "bold"),
                text_color=COLORS["text"]
            ).pack(pady=(15, 10), anchor="w")

            data_type_var = ctk.StringVar(value="any")
            
            radio_frame = ctk.CTkFrame(
                self.input_content_frame,
                fg_color=COLORS["dark_bg"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border"]
            )
            radio_frame.pack(fill="x", pady=10)

            options = [
                ("🅰️ حروف فقط", "letters"),
                ("🔢 أرقام صحيحة", "int"),
                ("🔣 أرقام عشرية", "float"),
                ("🌐 أي نوع", "any")
            ]

            for text, value in options:
                ctk.CTkRadioButton(
                    radio_frame,
                    text=text,
                    variable=data_type_var,
                    value=value,
                    font=("Cairo", 13),
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"]
                ).pack(anchor="w", pady=8, padx=15)

        elif prop_type == "dropdown":
            values_entry = self.create_modern_label_entry(
                self.input_content_frame,
                "📋 القيم (مفصولة بفواصل):",
                "قيمة1, قيمة2, قيمة3"
            )

        elif prop_type == "Condition":
            #messagebox.showinfo("تم", "انت دلوقتي عند show_add_property_panel بره add_property في  ال Condition 992 ")
            if not self.can_add_condition_property(item_name):
                self.hide_input_panel()
                messagebox.showwarning("تنبيه", "هذا العنصر يحتوي على  Condition بالفعل!")
                #return
            else:
                self.show_add_ifelse_property(parent_frame, item_name)
            return

        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="x")

        def add_property():
            prop_name = prop_entry.get().strip()
            if not prop_name:
                messagebox.showwarning("⚠️ تنبيه", "أدخل اسم الخاصية!")
                return

            existing_names = [p['name'] for p in self.items_data.get(item_name, {}).get("properties", [])]
            if prop_name in existing_names:
                messagebox.showwarning("⚠️ تنبيه", "الخاصية موجودة!")
                return

            if prop_type == "entry":
                data_type = data_type_var.get()
                self.add_property_frame(parent_frame, item_name, prop_name, "entry", data_type=data_type)
                self.items_data[item_name]["properties"].append({
                    'name': prop_name,
                    'type': 'entry',
                    'data_type': data_type,
                    "origin": "natural"

                })
            elif prop_type == "dropdown":
                values_str = values_entry.get().strip()
                if not values_str:
                    messagebox.showerror("❌ خطأ", "أدخل قيمة واحدة على الأقل!")
                    return
                values = [v.strip() for v in values_str.split(",") if v.strip()]
                self.add_property_frame(parent_frame, item_name, prop_name, "dropdown", values=values)
                self.items_data[item_name]["properties"].append({
                    'name': prop_name,
                    'type': 'dropdown',
                    'values': values,
                    "origin": "natural"

                })

            elif prop_type == "Condition":
                messagebox.showinfo("تم", "انت دلوقتي عند show_add_property_panel جوه add_property في  ال  1032 Condition  ")



            self.hide_input_panel()
            self.save_data()
            self.filter_items()

        ModernButton(
            btn_frame,
            text="إضافة",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=add_property
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

    def show_edit_property_panel(self, prop_frame, item_name, old_name, prop_type, old_values=None):
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text="✏️ تعديل الخاصية")

        prop_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "🏷️ اسم الخاصية:",
            ""
        )
        prop_entry.insert(0, old_name)
        prop_entry.focus()
        prop_entry.select_range(0, "end")

        values_entry = None
        if prop_type == "dropdown":
            values_entry = self.create_modern_label_entry(
                self.input_content_frame,
                "📋 القيم (مفصولة بفواصل):",
                ""
            )
            if old_values:
                values_entry.insert(0, ", ".join(old_values))

        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="x")

        def save_edit():
            new_name = prop_entry.get().strip()
            if not new_name:
                return

            existing_names = [p['name'] for p in self.items_data[item_name]["properties"] if p['name'] != old_name]
            if new_name in existing_names:
                messagebox.showwarning("⚠️ تنبيه", "الخاصية موجودة!")
                return

            for widget in prop_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text=f"🔹 {new_name}")
                    break

            if prop_type == "dropdown" and values_entry:
                values_str = values_entry.get().strip()
                if values_str:
                    values = [v.strip() for v in values_str.split(",") if v.strip()]
                    for widget in prop_frame.winfo_children():
                        if isinstance(widget, SearchableDropdown):
                            widget.values = values
                            widget.populate_list(values)

                            # ✅ تحديث نص الـ Entry كمان تلقائيًا لو فيه قيمة مختارة قديمة
                            if values:
                                current_text = widget.entry.get().strip()
                                if current_text not in values:
                                    widget.entry.delete(0, "end")
                                    widget.entry.insert(0, values[0])  # أول قيمة كافتراضي

                            break
                    for p in self.items_data[item_name]["properties"]:
                        if p['name'] == old_name:
                            p['name'] = new_name
                            p['values'] = values
                            break
            else:
                for p in self.items_data[item_name]["properties"]:
                    if p['name'] == old_name:
                        p['name'] = new_name
                        break

            self.hide_input_panel()
            self.save_data()
            item_data = self.items_data[item_name]
            threading.Thread(
                target=lambda: self.sync_manager.update_item_in_google(item_name, item_data),
                daemon=True
            ).start()
            self.filter_items()


        ModernButton(
            btn_frame,
            text="حفظ",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=save_edit
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

    def delete_property(self, frame, item_name, prop_name):
        if messagebox.askyesno("🗑️ تأكيد الحذف", f"حذف الخاصية '{prop_name}'؟"):
            frame.destroy()
            self.items_data[item_name]["properties"] = [
                p for p in self.items_data[item_name]["properties"] if p['name'] != prop_name
            ]
            self.save_data()
            item_data = self.items_data[item_name]
            threading.Thread(
                target=lambda: self.sync_manager.update_item_in_google(item_name, item_data),
                daemon=True
            ).start()
            self.filter_items()

    def delete_item(self, item_name, frame):
        if messagebox.askyesno("🗑️ تأكيد الحذف", f"حذف '{item_name}' نهائياً؟"):
            frame.destroy()
            del self.items_data[item_name]

            self.hide_input_panel()
            self.save_data()
            threading.Thread(
                target=lambda: self.sync_manager.delete_item_from_google(item_name),
                daemon=True
            ).start()        
            self.filter_items()

    def filter_items(self, event=None):
        # نلغي أي فلترة مجدولة سابقًا لتجنب تنفيذ متكرر
        if hasattr(self, "_after_id"):
            self.after_cancel(self._after_id)

        # نأجل الفلترة 300 مللي ثانية بعد آخر ضغطة مفتاح
        self._after_id = self.after(300, self._do_filter)

    def _do_filter(self):
        search_term = self.search_entry.get().strip().lower()

        self.filtered_items = []
        for key, data in reversed(self.items_data.items()):
            arabic = data.get("arabic_name", "").lower()
            english = key.lower()
            if not search_term or search_term in arabic or search_term in english:
                self.filtered_items.append(key)

        # العودة لأول صفحة عند تغيير الفلتر
        self.current_page = 1
        self.display_page()

    def display_page(self):
        # مسح العناصر
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        total_items = len(self.filtered_items)
        if total_items == 0:
            ctk.CTkLabel(
                self.scroll_frame,
                text="⚠ لا توجد نتائج",
                font=("Cairo", 40),
                text_color="#df0d0d"
            ).pack(fill='both', expand=True, padx=5, pady=5)
            return

        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page

        for item_name in self.filtered_items[start:end]:
            self.create_item_frame(item_name)

        # ====== أزرار التنقل بين الصفحات ======
        nav_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        nav_frame.pack(pady=15)

        # زر السابق
        if self.current_page > 1:
            ctk.CTkButton(
                nav_frame,
                text="⬅ السابق",
                width=120,
                command=self.prev_page
            ).pack(side="left", padx=10)

        # زر التالي
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            ctk.CTkButton(
                nav_frame,
                text="التالي ➡",
                width=120,
                command=self.next_page
            ).pack(side="left", padx=10)

        # رقم الصفحة
        ctk.CTkLabel(
            nav_frame,
            text=f"صفحة {self.current_page} من {total_pages}",
            font=("Cairo", 13),
            text_color="white"
        ).pack(side="left", padx=10)

    def next_page(self):
        self.current_page += 1
        self.display_page()

    def prev_page(self):
        self.current_page -= 1
        self.display_page()

    def save_data(self):
        try:
            data = dict(self.items_data)
            self.sync_manager.save_file(data, DATA_FILE)
            def thread_upload():
                self.sync_manager.upload_file(data)
            threading.Thread(
                target=thread_upload,
                daemon=True
            ).start()

        except Exception as e:
            print(f"⚠️ خطأ في الحفظ: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                if os.path.getsize(DATA_FILE) > 0:
                    self.items_data = json.load(f)
                else:
                    self.items_data = {}

            updated = {}
            for key, value in self.items_data.items():
                if isinstance(value, list):
                    updated[key.replace(" ", "_")] = {
                        "arabic_name": key,
                        "properties": value,
                        "code_template": ""
                    }
                else:
                    updated[key] = value
            self.items_data = dict(list(updated.items()))
            #self.filter_items()

    def get_final_code(self, item_name):
        item = self.items_data.get(item_name, {})
        final_code = item.get("code_template", "")
        props = {p['name']: p.get('value', '') for p in item.get("properties", [])}

        for prop_name, prop_value in props.items():
            final_code = final_code.replace("{" + prop_name + "}", str(prop_value))
        
        return final_code.strip()

    def get_final_code_2(self, item_name):
        item = self.items_data.get(item_name, {})
        final_code = item.get("code_template_2", "")
        props = {p['name']: p.get('value', '') for p in item.get("properties", [])}

        for prop_name, prop_value in props.items():
            final_code = final_code.replace("{" + prop_name + "}", str(prop_value))
        
        return final_code.strip()

#---------------------------اضافه خاصيه مع الكود ---------------------------

    def new_show_property_type_panel(self, parent_frame, item_name ):
        # self.show_input_panel()
        # self.clear_input_panel()
        self.input_panel_title.configure(text="🎯 اختر نوع الخاصية")

        ctk.CTkLabel(
            self.input_content_frame,
            text="اختر نوع الحقل المناسب:",
            font=("Cairo", 14),
            text_color=COLORS["text_muted"]
        ).pack(pady=20)

        ModernButton(
            self.input_content_frame,
            text="Entry",
            icon="📝",
            height=60,
            fg_color=COLORS["info"],
            hover_color="#2563eb",
            command=lambda: self.new_show_add_property_panel(parent_frame, item_name, "entry", open_code_after=True)
        ).pack(fill="x", pady=10)

        ModernButton(
            self.input_content_frame,
            text="Dropdown",
            icon="🔽",
            height=60,
            fg_color=COLORS["secondary"],
            hover_color="#7c3aed",
            command=lambda: self.new_show_add_property_panel(parent_frame, item_name, "dropdown", open_code_after=True)
        ).pack(fill="x", pady=10)

        ModernButton(
            self.input_content_frame,
            text="إلغاء",
            icon="❌",
            height=50,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(fill="x", pady=20)

    def new_show_add_property_panel(self, parent_frame, item_name, prop_type, open_code_after=False):
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text=f"➕ إضافة خاصية ({prop_type})")

        prop_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "🏷️ اسم الخاصية:",
            "اسم الخاصية"
        )
        prop_entry.focus()

        data_type_var = None
        values_entry = None

        if prop_type == "entry":
            ctk.CTkLabel(
                self.input_content_frame,
                text="📊 نوع البيانات:",
                font=("Cairo", 14, "bold"),
                text_color=COLORS["text"]
            ).pack(pady=(15, 10), anchor="w")

            data_type_var = ctk.StringVar(value="any")
            
            radio_frame = ctk.CTkFrame(
                self.input_content_frame,
                fg_color=COLORS["dark_bg"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border"]
            )
            radio_frame.pack(fill="x", pady=10)

            options = [
                ("🅰️ حروف فقط", "letters"),
                ("🔢 أرقام صحيحة", "int"),
                ("🔣 أرقام عشرية", "float"),
                ("🌐 أي نوع", "any")
            ]

            for text, value in options:
                ctk.CTkRadioButton(
                    radio_frame,
                    text=text,
                    variable=data_type_var,
                    value=value,
                    font=("Cairo", 13),
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"]
                ).pack(anchor="w", pady=8, padx=15)

        elif prop_type == "dropdown":
            values_entry = self.create_modern_label_entry(
                self.input_content_frame,
                "📋 القيم (مفصولة بفواصل):",
                "قيمة1, قيمة2, قيمة3"
            )

        # elif prop_type == "Condition":
        #     messagebox.showinfo("تم", "انت دلوقتي عند show_add_property_panel بره add_property في  ال Condition 992 ")

            

        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="x")

        def add_property():
            prop_name = prop_entry.get().strip()
            if not prop_name:
                messagebox.showwarning("⚠️ تنبيه", "أدخل اسم الخاصية!")
                return

            existing_names = [p['name'] for p in self.items_data.get(item_name, {}).get("properties", [])]
            if prop_name in existing_names:
                messagebox.showwarning("⚠️ تنبيه", "الخاصية موجودة!")
                return

            if prop_type == "entry":
                data_type = data_type_var.get()
                self.add_property_frame(parent_frame, item_name, prop_name, "entry", data_type=data_type)
                self.items_data[item_name]["properties"].append({
                    'name': prop_name,
                    'type': 'entry',
                    'data_type': data_type,
                    "origin": "condition"
                })
            elif prop_type == "dropdown":
                values_str = values_entry.get().strip()
                if not values_str:
                    messagebox.showerror("❌ خطأ", "أدخل قيمة واحدة على الأقل!")
                    return
                values = [v.strip() for v in values_str.split(",") if v.strip()]
                self.add_property_frame(parent_frame, item_name, prop_name, "dropdown", values=values)
                self.items_data[item_name]["properties"].append({
                    'name': prop_name,
                    'type': 'dropdown',
                    'values': values,
                    "origin": "condition"
                })

            # elif prop_type == "Condition":
            #     messagebox.showinfo("تم", "انت دلوقتي عند show_add_property_panel جوه add_property في  ال  1032 Condition  ")

            if open_code_after:
                self.show_edit_code_panel_2(item_name)
                return

        ModernButton(
            btn_frame,
            text="إضافة",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=add_property
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

#----------------------------------------------------------------------------------------------------------

    def show_add_ifelse_property(self, parent_frame, item_name):
        
            # 🔥 تحقق أنه يوجد Properties قبل السماح بعمل Condition
        if len(self.items_data[item_name]["properties"]) == 0:
            self.hide_input_panel()
            messagebox.showerror("❌ لا يمكن إضافة شرط", 
                                "يجب إضافة خاصية واحدة على الأقل قبل إنشاء Condition.")
            return
        
        self.show_input_panel()
        self.clear_input_panel()
        self.input_panel_title.configure(text="➕ Condition إضافة  ")

        # -------- اختيار الخاصية --------
        ctk.CTkLabel(
            self.input_content_frame,
            text="اختر الخاصية:",
            font=("Cairo", 14, "bold"),
            text_color=COLORS["text"]
        ).pack(pady=(15, 5), anchor="w")

        existing_props = [p['name'] for p in self.items_data[item_name]["properties"]]
        props_dropdown = SearchableDropdown(self.input_content_frame, existing_props, width=200)
        props_dropdown.pack(fill="x", pady=5)

        # -------- اختيار الشرط --------
        ctk.CTkLabel(
            self.input_content_frame,
            text="الشرط:",
            font=("Cairo", 14, "bold"),
            text_color=COLORS["text"]
        ).pack(pady=(15, 5), anchor="w")

        conditions = [
            ("equal", "=="),
            ("not equal", "!="),
            ("greater", ">"),
            ("less", "<"),
            ("greater or equal", ">="),
            ("less or equal", "<=")
        ]
        cond_dropdown = SearchableDropdown(self.input_content_frame, [c[0] for c in conditions], width=200)
        cond_dropdown.pack(fill="x", pady=5)

        # -------- إدخال القيمة --------
        value_entry = self.create_modern_label_entry(
            self.input_content_frame,
            "📥 قيمة المقارنة:",
            "قيمة"
        )

        # -------- خيارات IF و ELSE --------
        def create_action_section(label_text):
            section_frame = ctk.CTkFrame(self.input_content_frame, fg_color=COLORS["dark_bg"], corner_radius=12)
            section_frame.pack(fill="x", pady=15)

            ctk.CTkLabel(
                section_frame,
                text=label_text,
                font=("Cairo", 13, "bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w", padx=10, pady=(10, 5))

            action_var = ctk.StringVar(value="nothing")

            # خيارات الإجراء
            actions = [
                ("إضافة خاصية جديدة مع تعديل الكود", "add_property_edit_code"),
                ("إضافة خاصية جديدة", "add_property"),
                ("تعديل الكود فقط", "edit_code")
            ]

            for txt, val in actions:
                ctk.CTkRadioButton(
                    section_frame,
                    text=txt,
                    variable=action_var,
                    value=val,
                    font=("Cairo", 12),
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"]
                ).pack(anchor="w", pady=5, padx=15)

            # مكان إضافي لحقول الإدخال حسب الاختيار
            inputs_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            inputs_frame.pack(fill="x", pady=10, padx=15)

            # دالة لتحديث الحقول ديناميكيًا داخل نفس section
            def update_inputs(*args):
                for widget in inputs_frame.winfo_children():
                    widget.destroy()

                choice = action_var.get()
                new_entries = {}

                # --- داخل update_inputs() وفي مكان add_property / add_property_edit_code فقط ---

                if choice in ("add_property", "add_property_edit_code"):

                    new_entries["prop_type_var"] = ctk.StringVar(value="entry")

                    # إطار اختيار النوع
                    type_frame = ctk.CTkFrame(inputs_frame, fg_color=COLORS["dark_bg"], corner_radius=12,
                                            border_width=1, border_color=COLORS["border"])
                    type_frame.pack(fill="x", pady=5)

                    ctk.CTkLabel(
                        type_frame,
                        text="📌 اختر نوع الخاصية:",
                        font=("Cairo", 12, "bold"),
                        text_color=COLORS["text"]
                    ).pack(anchor="w", padx=10, pady=5)

                    for t in [("Entry", "entry"), ("Dropdown", "dropdown")]:
                        ctk.CTkRadioButton(
                            type_frame, text=t[0], variable=new_entries["prop_type_var"], value=t[1],
                            font=("Cairo", 12), fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
                        ).pack(anchor="w", pady=2, padx=10)

                    # هنا سيظهر المحتوى الديناميكي بعد اختيار النوع
                    dynamic_container = ctk.CTkFrame(inputs_frame, fg_color="transparent")
                    dynamic_container.pack(fill="x", pady=10)

                    def update_fields(*args):
                        # إفراغ المحتوى
                        for widget in dynamic_container.winfo_children():
                            widget.destroy()

                        selected = new_entries["prop_type_var"].get()

                        # ====== لو Entry ======
                        if selected == "entry":
                            new_entries["prop_name"] = self.create_modern_label_entry(
                                dynamic_container,
                                "🏷️ اسم الخاصية:",
                                "اسم الخاصية"
                            )

                            new_entries["data_type_var"] = ctk.StringVar(value="any")

                            dt_frame = ctk.CTkFrame(dynamic_container, fg_color=COLORS["dark_bg"], corner_radius=12,
                                                    border_width=1, border_color=COLORS["border"])
                            dt_frame.pack(fill="x", pady=5)

                            ctk.CTkLabel(
                                dt_frame,
                                text="📊 نوع البيانات:",
                                font=("Cairo", 12, "bold"),
                                text_color=COLORS["text"]
                            ).pack(anchor="w", padx=10, pady=5)

                            for text, val in [
                                ("🅰️ حروف فقط", "letters"),
                                ("🔢 أرقام صحيحة", "int"),
                                ("🔣 أرقام عشرية", "float"),
                                ("🌐 أي نوع", "any")
                            ]:
                                ctk.CTkRadioButton(
                                    dt_frame, text=text, variable=new_entries["data_type_var"], value=val,
                                    font=("Cairo", 12), fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
                                ).pack(anchor="w", padx=10, pady=3)

                        # ====== لو Dropdown ======
                        else:
                            new_entries["prop_name"] = self.create_modern_label_entry(
                                dynamic_container,
                                "🏷️ اسم الخاصية:",
                                "اسم الخاصية"
                            )

                            new_entries["values"] = self.create_modern_label_entry(
                                dynamic_container,
                                "📋 القيم (مفصولة بفواصل):",
                                "مثال: خيار1, خيار2, خيار3"
                            )

                        # لو الاختيار مع تعديل كود، نضيف صندوق الكود بعد اختيار النوع
                        if choice == "add_property_edit_code":
                            ctk.CTkLabel(dynamic_container, text="💻 الكود الجديد:", font=("Cairo", 12),
                                        text_color=COLORS["text"]).pack(anchor="w", pady=(10, 2))

                            new_entries["code_box"] = ctk.CTkTextbox(
                                dynamic_container,
                                height=40, corner_radius=10,
                                fg_color=COLORS["dark_bg"], border_width=1,
                                border_color=COLORS["border"],
                                font=("Consolas", 12), wrap="none"
                            )
                            new_entries["code_box"].pack(fill="x", pady=5)

                    new_entries["prop_type_var"].trace_add("write", update_fields)
                    update_fields()

                elif choice == "edit_code":
                    ctk.CTkLabel(inputs_frame, text="💻 الكود الجديد :", font=("Cairo", 12), text_color=COLORS["text"]).pack(anchor="w", pady=(10, 2))
                    new_entries["code_box"] = ctk.CTkTextbox(inputs_frame, height=40, corner_radius=10,
                                                            fg_color=COLORS["dark_bg"], border_width=1,
                                                            border_color=COLORS["border"], font=("Consolas", 12), wrap="none")
                    new_entries["code_box"].pack(fill="x", pady=5)

                section_frame.new_entries = new_entries

            action_var.trace_add("write", lambda *a: update_inputs())
            update_inputs()  # لتحديث أولي

            return section_frame, action_var

        if_frame, if_var = create_action_section("🎯 Condition")
        #else_frame, else_var = create_action_section("🔁 حالة ELSE:")

        # -------- زر الحفظ --------
        btn_frame = ctk.CTkFrame(self.input_content_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="x")

        def save_ifelse():
            # تحقق من اختيار الخاصية
            prop_name_sel = props_dropdown.get().strip()
            if not prop_name_sel:
                messagebox.showerror("❌ خطأ", "يجب اختيار خاصية أولاً!")
                return

            # تحقق من اختيار الشرط
            cond_value = cond_dropdown.get().strip()
            if not cond_value:
                messagebox.showerror("❌ خطأ", "يجب اختيار الشرط أولاً!")
                return

            # تحقق من إدخال قيمة المقارنة
            compare_value = value_entry.get().strip()
            if not compare_value:
                messagebox.showerror("❌ خطأ", "يجب إدخال قيمة المقارنة!")
                return

            selected_label = cond_dropdown.get()

            # الحصول على الرمز الحقيقي بناءً على الكلمة
            real_condition = next((c[1] for c in conditions if c[0] == selected_label), "==")

            # بناء dict الشرط
            new_entry = {
                "name": f"IF_{prop_name_sel}",
                "type": "Condition",
                "property": prop_name_sel,
                "condition": real_condition,
                "value": value_entry.get().strip(),
                "if_action": None,
                "origin": "condition"
            }

            # if action
            if if_var.get() == "add_property_edit_code":
                entries = if_frame.new_entries
                if not entries:
                    messagebox.showerror("❌", "أكمل بيانات IF!")
                    return
                pname = entries["prop_name"].get().strip()
                ptype = entries["prop_type_var"].get()
                code = entries["code_box"].get("1.0", "end").strip()
                
                if not code:
                    messagebox.showerror("❌", "الرجاء كتابة الكود أولاً!")
                    return
                
                self.items_data[item_name]["code_template_2"] = code

                # 🔥 رفعه فورًا إلى Google Sheet
                self.save_data()
                self.sync_manager.update_item_in_google(item_name, self.items_data[item_name].copy())


                new_entry["if_action"] = {
                    "action": "add_property_edit_code",
                    "prop_name": pname,
                    "prop_type": ptype,
                    "data_type": entries["data_type_var"].get(),   # ← الجديد
                    "values": entries["values"].get().split(",") if ptype == "dropdown" else None,
                    "origin": "condition"

                }
            
            elif if_var.get() == "add_property":
                entries = if_frame.new_entries
                if not entries:
                    messagebox.showerror("❌", "Condition  أكمل بيانات ")
                    return
                pname = entries["prop_name"].get().strip()
                ptype = entries["prop_type_var"].get()
                
                if ptype == "dropdown":
                    if not entries["values"].get().strip():
                        messagebox.showerror("❌", "أدخل قيم أولاً!")
                        return

                
                new_entry["if_action"] = {
                    "action": "add_property",
                    "prop_name": pname,
                    "prop_type": ptype,
                    "data_type": entries.get("data_type_var", ctk.StringVar(value="any")).get(),
                    "values": entries["values"].get().split(",") if ptype == "dropdown" else None,
                    "origin": "condition"
                }

            elif if_var.get() == "edit_code":
                entries = if_frame.new_entries
                if not entries:
                    messagebox.showerror("❌", "أكمل بيانات IF!")
                    return

                code = entries["code_box"].get("1.0", "end").strip()
                if not code:
                    messagebox.showerror("❌", "الرجاء كتابة الكود أولاً!")
                    return
                # 🔥 حفظ الكود في code_template_2 بدل properties
                self.items_data[item_name]["code_template_2"] = code

                # 🔥 رفعه مباشرة إلى Google Sheet

                self.save_data()
                self.sync_manager.update_item_in_google(item_name, self.items_data[item_name].copy())
                new_entry["if_action"] = {
                    "action": "edit_code",
                    "origin": "condition"

                }
                #return

                # لا نضيف أي IF action للخاصية
                #new_entry["if_action"] = None

            # else:
            #     new_entry["if_action"] = None

            # else action
            # if else_var.get() == "add_property_edit_code":
            #     entries = else_frame.new_entries
            #     if not entries:
            #         messagebox.showerror("❌", "أكمل بيانات IF!")
            #         return
            #     pname = entries["prop_name"].get().strip()
            #     ptype = entries["prop_type_var"].get()
            #     code = entries["code_box"].get("1.0", "end").strip()
                
            #     if not code:
            #         messagebox.showerror("❌", "الرجاء كتابة الكود أولاً!")
            #         return
                
            #     self.items_data[item_name]["code_template_2"] = code

            #     # 🔥 رفعه فورًا إلى Google Sheet
            #     self.save_data()
            #     self.sync_manager.update_item_in_google(item_name, self.items_data[item_name].copy())


            #     new_entry["else_action"] = {
            #         "action": "add_property_edit_code",
            #         "prop_name": pname,
            #         "prop_type": ptype,
            #         "data_type": entries["data_type_var"].get(),   # ← الجديد
            #         "origin": "condition"

            #     }
            
            # elif else_var.get() == "add_property":
            #     entries = else_frame.new_entries
            #     if not entries:
            #         messagebox.showerror("❌", "أكمل بيانات ELSE!")
            #         return
            #     pname = entries["prop_name"].get().strip()
            #     ptype = entries["prop_type_var"].get()
            #     new_entry["else_action"] = {
            #         "action": "add_property",
            #         "prop_name": pname,
            #         "prop_type": ptype,
            #         "origin": "condition"
            #     }

            # elif else_var.get() == "edit_code":
            #     entries = else_frame.new_entries
            #     if not entries:
            #         messagebox.showerror("❌", "أكمل بيانات ELSE!")
            #         return

            #     code = entries["code_box"].get("1.0", "end").strip()
                
            #     if not code:
            #         messagebox.showerror("❌", "الرجاء كتابة الكود أولاً!")
            #         return
            #     # 🔥 حفظ الكود في code_template_2 مباشرة
            #     self.items_data[item_name]["code_template_2"] = code

            #     # 🔥 رفعه فورًا لجوجل شيت
            #     self.save_data()
            #     self.sync_manager.update_item_in_google(item_name, self.items_data[item_name].copy())

            #     # بدون إضافة action
            #     new_entry["else_action"] = None

            # else:
            #     new_entry["else_action"] = None

            # إضافة الخاصية الجديدة (ifelse) إلى بيانات العنصر
            self.items_data[item_name]["properties"].append(new_entry)

            # إضافة إطار العرض في الواجهة
            self.add_property_frame(parent_frame, item_name, new_entry["name"], "Condition 🔗 ")

            self.hide_input_panel()
            self.save_data()
            self.filter_items()

        ModernButton(
            btn_frame,
            text="إضافة",
            icon="✅",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=save_ifelse
        ).pack(side="left", expand=True, padx=(0, 5))

        ModernButton(
            btn_frame,
            text="إلغاء",
            icon="❌",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.hide_input_panel
        ).pack(side="left", expand=True, padx=(5, 0))

    def can_add_condition_property(self, item_name):
        for prop in self.items_data[item_name]["properties"]:
            if prop.get("type") == "Condition":
                return False  # بالفعل توجد خاصية Condition
        return True  # لا توجد خاصية Condition بعد
