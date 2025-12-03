import customtkinter as ctk
from tkinter import messagebox, simpledialog
import threading
import json
from pathlib import Path
import time ,datetime
from sync.manager import SyncManager

from categories import CATEGORIES
from pathlib import Path
import os
import platform
#from ui.items_form import SearchableDropdown


CATEGORIES = CATEGORIES

class SearchableDropdown(ctk.CTkFrame):
    def __init__(self, parent, values, width=2000, placeholder_text="اضغط للعرض", font=("Arial", 12), **kwargs):
        super().__init__(parent, **kwargs)
        self.values = values
        self.width = width
        self.selected_value = None

        self.entry = ctk.CTkEntry(self, width=self.width, placeholder_text=placeholder_text, font=font,fg_color="#2c3e50",  # لون الخلفية
                                  text_color="white",   # لون النص
                                  border_color="#13A6D3", # لون الحدود
                                  corner_radius=10)
        self.entry.pack(pady=(0, 2))


        self.entry.bind("<Enter>", lambda e: self.entry.configure(fg_color="#475666", border_color="#16a085"))
        self.entry.bind("<Leave>", lambda e: self.entry.configure(fg_color="#2c3e50", border_color="#2980b9"))


        self.entry.bind("<KeyRelease>", self.filter_list)
        self.entry.bind("<Button-1>", self.show_list)
        self.entry.bind("<FocusOut>", lambda e: self.dropdown_frame.pack_forget())

        self.dropdown_frame = ctk.CTkFrame(self, fg_color=("gray90", "#3293ac"))
        self.dropdown_frame.pack_forget()

    def show_list(self, event=None):

        self.dropdown_frame.configure(fg_color="transparent")  # تدرج لوني مميز عند عرض القائمة
        self.dropdown_frame.pack(pady=(0, 5), fill="x")
        self.populate_list(self.values)

    def populate_list(self, data):
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()
        for item in data:
            btn = ctk.CTkButton(
                self.dropdown_frame,
                text=item,
                height=30,
                fg_color=("white", "#11A165"),
                text_color=("black", "white"),
                hover_color=("#d1f5e0", "#13A6D3"),
                command=lambda i=item: self.select_value(i)
            )
            btn.pack(fill="x", pady=1)

    def filter_list(self, event=None):
        search = self.entry.get().lower()
        filtered = [val for val in self.values if search in val.lower()]
        self.populate_list(filtered if filtered else ["لا توجد نتائج مشابهة"])

    def select_value(self, value):
        if value != "لا توجد نتائج مشابهة":
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
            self.selected_value = value
                    # 🔹 نفّذ أي callback مسجل على الاختيار
            if hasattr(self, "on_select_callback"):
                self.on_select_callback(value)
        self.dropdown_frame.pack_forget()

    def get(self):
        """إرجاع القيمة المختارة أو النص المكتوب"""
        if self.selected_value:
            return self.selected_value
        else:
            return self.entry.get().strip()



class NewToolMixin:


    def add_new_tool_window(self):


        if platform.system() == "Windows":
            base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "EuroTools" / "data"
        else:
            base_dir = Path.home() / ".local" / "share" / "EuroTools" / "data"

        base_dir.mkdir(parents=True, exist_ok=True)
        DATA_FILE = base_dir / "items_data.json"


        # تحميل البيانات من الملف
        def load_item_names():
            if DATA_FILE.exists():
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    english_names = list(data.keys())
                    arabic_names = [v.get("arabic_name", "") for v in data.values()]
                    return english_names, arabic_names
            else:
                print("⚠️ لم يتم العثور على ملف item_data.json في:", DATA_FILE)
                return [], []
            
            
        new_tool_window = ctk.CTkToplevel(self.root)
        new_tool_window.title("➕ إضافة أداة جديدة")
        new_tool_window.geometry("600x750")
        new_tool_window.resizable(True, True)
        new_tool_window.transient(self.root)
        new_tool_window.grab_set()

        new_tool_window.update_idletasks()
        x = (new_tool_window.winfo_screenwidth() // 2) - 300
        y = (new_tool_window.winfo_screenheight() // 2) - 375
        new_tool_window.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkScrollableFrame(new_tool_window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        header_frame = ctk.CTkFrame(main_frame, fg_color=("#2b5797", "#1e3a5f"), corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            header_frame, text="➕ إضافة أداة جديدة",
            font=("Arial", 22, "bold"), text_color="white"
        ).pack(pady=15)

        # 🧩 قسم الأسماء
        names_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        names_frame.pack(fill="x", pady=(0, 15))

        # 🟢 تحميل الأسماء من item_data.json
        item_data_path = DATA_FILE
        name_en_list, name_ar_list = [], []
        item_data = {}

        if item_data_path.exists():
            try:
                with open(item_data_path, "r", encoding="utf-8") as f:
                    item_data = json.load(f)
                    for key, value in item_data.items():
                        name_en_list.append(key)
                        arabic_name = value.get("arabic_name", "").strip()
                        if arabic_name:
                            name_ar_list.append(arabic_name)
            except Exception as e:
                print(f"❌ خطأ في قراءة item_data.json: {e}")
        else:
            print("⚠️ لم يتم العثور على ملف item_data.json")

        # ✅ إزالة التكرار وترتيب القوائم
        name_en_list = sorted(list(set(name_en_list)))
        name_ar_list = sorted(list(set(name_ar_list)))

        # 🔤 الاسم الإنجليزي
        ctk.CTkLabel(
            names_frame, text="📝 الاسم بالإنجليزية:",
            font=("Arial", 13, "bold"), anchor="w"
        ).pack(anchor="w", padx=15, pady=(5, 5))

        tool_name_en_entry = SearchableDropdown(
            names_frame,
            values=name_en_list if name_en_list else ["(لا توجد بيانات)"],
            placeholder_text="أدخل الاسم بالإنجليزية",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )
        tool_name_en_entry.pack(fill="x", padx=15, pady=(0, 15))

        # 🔠 الاسم بالعربية
        ctk.CTkLabel(
            names_frame, text="📝 الاسم بالعربية:",
            font=("Arial", 13, "bold"), anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        tool_name_ar_entry = SearchableDropdown(
            names_frame,
            values=name_ar_list if name_ar_list else ["(لا توجد بيانات)"],
            placeholder_text="أدخل الاسم بالعربية",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )
        tool_name_ar_entry.pack(fill="x", padx=15, pady=(0, 10))

        # 🧠 دوال المزامنة بين القائمتين
        def on_name_en_selected(choice=None):
            """عند اختيار اسم إنجليزي - حدّث الاسم العربي"""
            choice = choice or tool_name_en_entry.get()
            if not choice or choice not in item_data:
                return

            arabic_name = item_data[choice].get("arabic_name", "")
            if arabic_name:
                # تحديث الخانة العربية
                tool_name_ar_entry.entry.delete(0, "end")
                tool_name_ar_entry.entry.insert(0, arabic_name)
            
            # تحميل الخصائص
            load_properties_from_json(choice)



        def on_name_ar_selected(choice=None):
            """عند اختيار اسم عربي - حدّث الاسم الإنجليزي"""
            choice = choice or tool_name_ar_entry.get()
            if not choice:
                return

            # البحث في البيانات عن الاسم العربي
            for en_name, info in item_data.items():
                if info.get("arabic_name", "") == choice:
                    # تحديث الخانة الإنجليزية
                    tool_name_en_entry.entry.delete(0, "end")
                    tool_name_en_entry.entry.insert(0, en_name)

                    # تحميل الخصائص
                    load_properties_from_json(en_name)
                    break


        # ✅ ربط الأوامر بالقوائم
        tool_name_en_entry.entry.bind("<FocusOut>", lambda e: on_name_en_selected())
        tool_name_ar_entry.entry.bind("<FocusOut>", lambda e: on_name_ar_selected())

        tool_name_en_entry.entry.bind("<KeyRelease>", lambda e: on_name_en_selected())
        tool_name_ar_entry.entry.bind("<KeyRelease>", lambda e: on_name_ar_selected())


        # قسم الفئة والمشروع
        category_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        category_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            category_frame, 
            text="🏷️ الفئة:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        category_menu = ctk.CTkOptionMenu(
            category_frame, 
            values=["اختر الفئة"] + CATEGORIES[1:],
            height=40,
            font=("Arial", 12),
            corner_radius=8,
            button_color=("#e67e22", "#d35400"),
            button_hover_color=("#d35400", "#e67e22")
        )
        category_menu.set("اختر الفئة")
        category_menu.pack(fill="x", padx=15, pady=(0, 15))

        project_name_label = ctk.CTkLabel(
            category_frame, 
            text="🔖 كود المشروع او المكنة:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        project_name_entry = ctk.CTkEntry(
            category_frame, 
            placeholder_text="أدخل كود المشروع او المكنة",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )
        project_name_label.pack_forget()
        project_name_entry.pack_forget()

        def load_properties_from_json(selected_key):
            """تحميل الخصائص من item_data.json عند اختيار أداة"""
            if not selected_key or selected_key not in item_data:
                return

            item_info = item_data[selected_key]
            props = item_info.get("properties", [])
            code_template = item_info.get("code_template", "")
            code_template_2 = item_info.get("code_template_2", "")
            # 🧹 مسح أي خصائص سابقة
            for frame in list(self.properties_container.winfo_children()):
                frame.destroy()
            self.props_fields.clear()

            # إعادة تهيئة قائمة الخصائص الشرطية
            if not hasattr(self, "condition_props"):
                self.condition_props = []
            else:
                self.condition_props.clear()

            # 🧩 عرض الخصائص حسب النوع (entry / dropdown)
            for prop in props:
                prop_name = prop.get("name", "")
                prop_type = prop.get("type", "entry")
                data_type = prop.get("data_type", "")
                origin_type = prop.get("origin_type", "natural")
                values = prop.get("values", [])  # لو نوعها dropdown

                # لو الخاصية شرطية
                if prop_type == "Condition":
                    self.condition_props.append(prop)
                    continue  # لا نعرضها في البداية

                prop_frame = ctk.CTkFrame(self.properties_container, corner_radius=8)
                prop_frame.pack(fill="x", padx=10, pady=5)

                name_label = ctk.CTkLabel(
                    prop_frame,
                    text=f"{prop_name}",
                    font=("Arial", 12, "bold"),
                    anchor="w"
                )
                name_label.pack(anchor="w", padx=10, pady=3)

                # ✅ لو نوعها entry → حقل كتابة
                if prop_type == "entry":
                    value_widget = ctk.CTkEntry(
                        prop_frame,
                        placeholder_text=f" {prop_name} أدخل ",
                        font=("Arial", 12),
                        height=35,
                        fg_color="#2c3e50",  # لون الخلفية
                        text_color="white",   # لون النص
                        border_color="#13A6D3", # لون الحدود
                        corner_radius=10
                    )
                    value_widget.pack(fill="x", padx=10, pady=(0, 5))

                    # التحقق أثناء الكتابة + تطبيق الشروط فورًا
                    value_widget.bind(
                        "<KeyRelease>",
                        lambda e, w=value_widget, dtype=data_type: (
                            self.on_entry_change(w, dtype),
                            self.apply_conditions(selected_key, code_template_2)
                        )
                    )
                
                # ✅ لو نوعها dropdown → قائمة خيارات
                elif prop_type == "dropdown":
                    if not values:
                        values = ["(لا توجد قيم محددة)"]
                    value_widget = SearchableDropdown(
                        prop_frame,
                        values=values if values else ["(لا توجد بيانات)"],
                        placeholder_text="اختر",
                        font=("Arial", 12),
                        height=35,
                        corner_radius=8

                    )
                    value_widget.pack(fill="x", padx=10, pady=(0, 5))
                    
                    value_widget.on_select_callback = lambda v=value_widget.get(): self.apply_conditions(selected_key, code_template_2)

                    # التحقق أثناء اختيار قيمة
                    value_widget.entry.bind(
                        "<KeyRelease>",
                        lambda e, w=value_widget, dtype=data_type: self.apply_conditions(selected_key, code_template_2)
                    )

                elif prop_type == "Condition":
                    # إطار خاص للشرط
        
                    pass
                    
                    
                    
                    
                else:
                    # لو نوع غير معروف، نعرضه كـ نص فقط
                    value_widget = ctk.CTkLabel(
                        prop_frame,
                        text=f"(نوع غير معروف: {prop_type})",
                        font=("Arial", 12),
                        text_color="gray"
                    )
                    value_widget.pack(anchor="w", padx=10, pady=5)

                # نخزّن (اسم الخاصية، الـ widget نفسه)
                self.props_fields.append((prop_name, value_widget))

            # 🔒 عرض الكود فقط بدون تعديل
            self.template_entry_new.configure(text=code_template)
                
                
        
        
        # def apply_conditions(self, item_name, code_template_2=None):
        #     """يفحص كل الـ Condition ويضيف الخصائص أو يحدث الكود"""
        #     if not hasattr(self, "condition_props") or not self.condition_props:
        #         return

        #     for cond in self.condition_props:
        #         prop_name = cond.get("property")
        #         operator = cond.get("condition")
        #         compare_value = cond.get("value")
        #         if_action = cond.get("if_action", {})

        #         # الحصول على قيمة الخاصية المرتبطة
        #         current_value = None
        #         for pname, widget in self.props_fields:
        #             if pname == prop_name:
                        
        #                 if isinstance(widget, ctk.CTkEntry) or isinstance(widget, SearchableDropdown):
        #                     current_value = widget.get().strip()
        #                 break
                    
            
        #         if current_value is None:
        #             continue

        #         # فحص الشرط
        #         try:
        #             expr = f"'{current_value}' {operator} '{compare_value}'"
        #             result = eval(expr)
        #         except:
        #             result = False

        #         if result:
        #             # تنفيذ if_action
        #             action_type = if_action.get("action")
        #             if action_type in ("add_property", "add_property_edit_code"):
        #                 prop_name_new = if_action.get("prop_name")
        #                 prop_type_new = if_action.get("prop_type", "entry")
        #                 data_type_new = if_action.get("data_type", "any")
        #                 values_new = if_action.get("values", [])
        #                 if not isinstance(values_new, list):
        #                     values_new = [values_new]
        #         # ✅ التأكد أن الخاصية الجديدة لم تُضاف مسبقًا
        #             #if prop_name_new not in [p for p, _ in self.props_fields]:
        #                 self.add_property_frame(
        #                     self.properties_container,
        #                     item_name,
        #                     prop_name_new,
        #                     prop_type_new,
        #                     data_type_new,
        #                     values_new  # تمرير القيم الجديدة
        #                 )
                        

        #                 # تحديث الكود لو موجود
        #                 if code_template_2:
        #                     self.template_entry_new.configure(text=code_template_2)        
                        
                        
                        
                
                
        def toggle_project_name_field(choice):
            if choice == "BOM":
                project_name_label.pack(anchor="w", padx=15, pady=(5, 5))
                project_name_entry.pack(fill="x", padx=15, pady=(0, 15))
            
            elif choice == "Machine Spare Parts":
                project_name_label.pack(anchor="w", padx=15, pady=(5, 5))
                project_name_entry.pack(fill="x", padx=15, pady=(0, 15))
            

            else:
                project_name_label.pack_forget()
                project_name_entry.pack_forget()
                project_name_entry.delete(0, ctk.END)

        category_menu.configure(command=toggle_project_name_field)
        
        # قسم الوصف
        desc_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        desc_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            desc_frame, 
            text="📄 الوصف:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        tool_description_textbox = ctk.CTkTextbox(
            desc_frame, 
            height=50,
            font=("Arial", 12),
            corner_radius=8
        )
        tool_description_textbox.pack(fill="x", padx=15, pady=(0, 15))

        # 🧩 قسم الخصائص
        ctk.CTkLabel(main_frame, text="الخصائص:", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        self.properties_container = ctk.CTkScrollableFrame(main_frame, height=50)
        self.properties_container.pack(fill="x", padx=10, pady=5)
        self.props_fields = []

        # 🧠 خانة الكود (عرض فقط)
        
        ctk.CTkLabel(main_frame, text="قالب الكود", font=("Arial", 16, "bold")).pack(fill="y", padx=10, pady=(20, 5))
        

        self.template_entry_new = ctk.CTkLabel(
            main_frame,
            text="",  # هيتحدث لاحقًا بالكود
            font=("Consolas", 16),
            justify="left",
            anchor="w",
            height=20,
            fg_color=("#1e1e1e", "#1e1e1e"),
            text_color="#00FF7F",
            corner_radius=8
        )
        

        self.template_entry_new.pack(fill="y", padx=10, pady=5)
        self.template_entry_new.configure(state="disabled")



        def save_tool_data():
            tools_data = self.data_manager.load_tools()
            # ✅ لو البيانات القديمة كانت dict، نحولها إلى list علشان نسمح بالتكرار
            if isinstance(tools_data, dict):
                tools_data = list(tools_data.values())

            # 🟢 نجيب أسماء الأدوات من الحقول
            tool_name_ar = tool_name_ar_entry.get().strip()
            tool_name_en = tool_name_en_entry.get().strip()


            if not tool_name_ar or not tool_name_en:
                messagebox.showerror("خطأ", "الرجاء إدخال اسم الأداة باللغتين.")
                return

            # ✅ تحقق من اختيار الفئة قبل الحفظ
            if category_menu.get() == "اختر الفئة":
                messagebox.showerror("⚠️ خطأ", "الرجاء اختيار الفئة قبل حفظ الأداة.")
                return



                                # ✅ تحقق من إدخال صيغة الكود قبل الحفظ مع تأثيرات بصرية و focus تلقائي
            if not self.template_entry_new.cget("text").strip():
                # حفظ اللون الأصلي
                original_color = self.template_entry_new.cget("fg_color")

                # تغيير اللون مؤقتًا للأحمر
                self.template_entry_new.configure(fg_color="#ff4d4d")

                # عمل اهتزاز بسيط للنافذة
                x, y = new_tool_window.winfo_x(), new_tool_window.winfo_y()
                for i in range(3):
                    new_tool_window.geometry(f"+{x + 10}+{y}")
                    new_tool_window.update()
                    new_tool_window.after(50)
                    new_tool_window.geometry(f"+{x - 10}+{y}")
                    new_tool_window.update()
                    new_tool_window.after(50)
                new_tool_window.geometry(f"+{x}+{y}")  # إرجاع النافذة لمكانها الأصلي

                # بعد ثانية يرجع اللون الطبيعي وياخد focus تلقائي
                def reset_field_color():
                    self.template_entry_new.configure(fg_color=original_color)
                    self.template_entry_new.focus_set()

                new_tool_window.after(300, reset_field_color)

                messagebox.showerror("❌ خطأ", "الرجاء إدخال صيغة الكود قبل حفظ الأداة.")
                return


            # ✅ التحقق من أن جميع الخصائص تم إدخالها
            properties_dict = {}
            missing_fields = []

            for prop_name, widget in self.props_fields:
                value = ""
                if isinstance(widget, ctk.CTkEntry):
                    value = widget.get().strip()
                elif isinstance(widget, SearchableDropdown):
                    value = widget.get().strip()
                elif isinstance(widget, ctk.CTkOptionMenu):
                    value = widget.get().strip()

                # إذا الحقل فاضي → أضفه لقائمة الناقصين
                if not value:
                    missing_fields.append(prop_name)
                else:
                    properties_dict[prop_name] = value

            # ⚠️ لو فيه خصائص ناقصة، نظهر رسالة خطأ ونمنع الحفظ
            if missing_fields:
                fields_str = "\n".join(f"• {f}" for f in missing_fields)
                messagebox.showerror(
                    "❌ خطأ في الإدخال",
                    f"الرجاء إدخال القيم التالية قبل الحفظ:\n\n{fields_str}"
                )

                # ✨ مؤثر بصري بسيط على الحقول الفارغة
                for prop_name, widget in self.props_fields:
                    if prop_name in missing_fields:
                        widget.configure(border_color="red")
                        widget.after(800, lambda w=widget: w.configure(border_color="#13A6D3"))

                return  # إيقاف عملية الحفظ


            new_tool_data = {
                "name_ar": tool_name_ar,
                "name_en": tool_name_en,
                "category": category_menu.get(),
                "description": tool_description_textbox.get("1.0", "end-1c").strip(),
                "properties": properties_dict,
                "template": self.template_entry_new.cget("text").strip(),
                "updated_at": time.time(),
                "created_at": time.time(),  # ✅ إضافة التاريخ

            }

            if category_menu.get() in ["BOM", "Machine Spare Parts"]:
                new_tool_data["project_name"] = project_name_entry.get().strip()


            new_final_code = self.get_final_code(new_tool_data)
            for t in tools_data:
                try:
                    if self.get_final_code(t) == new_final_code:
                        messagebox.showwarning(
                            "⚠️ كود مكرر",
                            f"الأداة '{t.get('name_ar', 'غير معروف')}' موجودة بالفعل بنفس الكود:\n\n{new_final_code}\n\nسيتم عرض تفاصيلها الآن."
                        )
                        self.show_product_details(t.get("name_en", "غير معروف"), t, new_final_code)
                        return
                except Exception:
                    continue


            tools_data.insert(0, new_tool_data)


            if self.data_manager.save_tools(tools_data):
               
                new_tool_window.destroy()
                if hasattr(self, "sync_manager") and self.sync_manager:
                    threading.Thread(target=self.sync_manager.sync_all, daemon=True).start()
                    #print("🚀 تم رفع الأداة الجديدة تلقائيًا إلى Google Sheets.")
                else:
                    print("⚠️ لم يتم تهيئة SyncManager بعد، لن يتم رفع الأداة.")

                messagebox.showinfo("✅ نجاح", "تمت إضافة الأداة بنجاح كمنتج جديد.")
                user = getattr(self, "logged_in_user", None) or getattr(SyncManager, "logged_in_user", None)

                self.history.log_action(
                    user = user, 
                    action="اضافة منتج", 
                    item=new_final_code,
                    details=None,
                    status="✅ Success"
                )

        
        # زر الحفظ
        save_button = ctk.CTkButton(
            main_frame, 
            text="💾 حفظ الأداة", 
            command=save_tool_data,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color=("#2ecc71", "#27ae60"),
            hover_color=("#27ae60", "#2ecc71"),
            corner_radius=12
        )
        save_button.pack(pady=20, fill="x")


    def on_entry_change(self, entry_widget, data_type):
        """
        هذه الدالة تتحقق من القيمة المدخلة في الحقل بناءً على نوع البيانات المختار.
        ولا تسمح بإدخال قيم غير صالحة.
        """
        value = entry_widget.get().strip()

        # التحقق من أن المدخل غير فارغ
        if not value:
            return True  # يمكن ترك الحقل فارغًا إذا كان غير مطلوب

        # التحقق بناءً على نوع البيانات
        if data_type == "int":
            # يسمح فقط بالأرقام الصحيحة أو الحقل الفارغ
            if value.isdigit() or value == "":
                return True  # صالح
            else:
                entry_widget.delete(0, "end")  # مسح الإدخال غير الصحيح
                return False  # غير صالح

        elif data_type == "float":
            # يسمح فقط بالأرقام العشرية أو الحقل الفارغ
            if value in ("", "-", ".", "-.") or self.is_float(value):
                return True  # صالح
            else:
                entry_widget.delete(0, "end")  # مسح الإدخال غير الصحيح
                return False  # غير صالح

        elif data_type == "letters":
            # يسمح فقط بالحروف أو الحقل الفارغ
            if value.isalpha() or value == "":
                return True  # صالح
            else:
                entry_widget.delete(0, "end")  # مسح الإدخال غير الصحيح
                return False  # غير صالح

        elif data_type == "any":
            # أي نوع من البيانات مقبول
            return True  # صالح

        # في حالة عدم وجود نوع بيانات محدد
        entry_widget.delete(0, "end")  # مسح الإدخال غير الصحيح
        
        current_item_name = getattr(self, "current_item", None)
        if current_item_name:
            self.apply_conditions(current_item_name)
            
        return False  # غير صالح


    def is_float(self, value):
        """
        هذه الدالة تتحقق مما إذا كانت القيمة يمكن تحويلها إلى float.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
