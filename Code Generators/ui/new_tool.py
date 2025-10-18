import customtkinter as ctk
from tkinter import messagebox, simpledialog
import threading
from sync.manager import SyncManager
CATEGORIES = ["الكل", "BOM", "CNC Cutting Tools", 
"Hand Tools","Machine Spare Parts", "Oil & Lubricants", 
"Stationary", "Standared Components","أخرى"]


class NewToolMixin:
    def add_new_tool_window(self):
        new_tool_window = ctk.CTkToplevel(self.root)
        new_tool_window.title("➕ إضافة أداة جديدة")
        new_tool_window.geometry("600x750")
        new_tool_window.resizable(True, True)
        new_tool_window.transient(self.root)
        new_tool_window.grab_set()
        
        # توسيط النافذة
        new_tool_window.update_idletasks()
        x = (new_tool_window.winfo_screenwidth() // 2) - 300
        y = (new_tool_window.winfo_screenheight() // 2) - 375
        new_tool_window.geometry(f"+{x}+{y}")
        
        main_frame = ctk.CTkScrollableFrame(new_tool_window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # العنوان الرئيسي
        header_frame = ctk.CTkFrame(main_frame, fg_color=("#2b5797", "#1e3a5f"), corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            header_frame, 
            text="➕ إضافة أداة جديدة", 
            font=("Arial", 22, "bold"),
            text_color="white"
        ).pack(pady=15)
        
        # قسم الأسماء
        names_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        names_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            names_frame, 
            text="📝 الاسم بالعربية:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        tool_name_ar_entry = ctk.CTkEntry(
            names_frame, 
            placeholder_text="أدخل الاسم بالعربية",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )
        tool_name_ar_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            names_frame, 
            text="📝 الاسم بالإنجليزية:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(5, 5))
        tool_name_en_entry = ctk.CTkEntry(
            names_frame, 
            placeholder_text="أدخل الاسم بالإنجليزية",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )
        tool_name_en_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        tool_name_ar_entry.bind("<KeyRelease>", lambda event: load_existing_properties_if_found())
        tool_name_en_entry.bind("<KeyRelease>", lambda event: load_existing_properties_if_found())

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
            text="🔖 كود المشروع:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        project_name_entry = ctk.CTkEntry(
            category_frame, 
            placeholder_text="أدخل كود المشروع",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )
        project_name_label.pack_forget()
        project_name_entry.pack_forget()
        
        def toggle_project_name_field(choice):
            if choice == "BOM":
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
            height=90,
            font=("Arial", 12),
            corner_radius=8
        )
        tool_description_textbox.pack(fill="x", padx=15, pady=(0, 15))

        # قسم الخصائص
        properties_container = ctk.CTkFrame(main_frame, corner_radius=12)
        properties_container.pack(fill="x", pady=(0, 15))
        
        props_header = ctk.CTkFrame(properties_container, fg_color=("#3a7ebf", "#2b5f8f"), corner_radius=10)
        props_header.pack(fill="x", padx=10, pady=(10, 10))
        ctk.CTkLabel(
            props_header, 
            text="⚙️ الخصائص", 
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(pady=8)

# قسم صيغة الكود
        template_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        template_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            template_frame, 
            text="🔢 صيغة الكود (استخدم {اسم_الخاصية}):", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        template_entry_new = ctk.CTkEntry(
            template_frame, 
            placeholder_text="مثال: A-B-{C}-{D}",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )
        template_entry_new.pack(fill="x", padx=15, pady=(0, 15))
        
        props_fields = []
        last_loaded_tool = {"name_ar": "", "name_en": "", "loaded_from_existing": False}
        self.password_button_added = False
        
        def load_existing_properties_if_found():
            name_ar = tool_name_ar_entry.get().strip().lower()
            name_en = tool_name_en_entry.get().strip().lower()

            if name_ar == last_loaded_tool["name_ar"].lower() and name_en == last_loaded_tool["name_en"].lower() and last_loaded_tool["loaded_from_existing"]:
                return

            tools_data = self.data_manager.load_tools()

            # ✅ دعم list أو dict
            if isinstance(tools_data, dict):
                tools_iter = tools_data.values()
            else:
                tools_iter = tools_data

            existing_tool = None
            for value in tools_iter:
                if str(value.get("name_en", "")).lower() == name_en or str(value.get("name_ar", "")).lower() == name_ar:
                    existing_tool = value
                    break


            if existing_tool:
                for frame in list(properties_container.winfo_children())[1:]:
                    frame.destroy()
                props_fields.clear()

                for prop_name, prop_value in existing_tool.get("properties", {}).items():
                    add_prop_field_new(prop_name, prop_value, is_existing=True)

                ctk.CTkButton(
                    properties_container, 
                    text="➕ إضافة خاصية", 
                    command=add_prop_field_new,
                    height=38,
                    font=("Arial", 12, "bold"),
                    fg_color=("#27ae60", "#1e8449"),
                    hover_color=("#1e8449", "#27ae60"),
                    corner_radius=8
                ).pack(padx=10, pady=10)

                category_menu.set(existing_tool.get("category", "اختر الفئة"))
                tool_description_textbox.delete("1.0", "end")
                tool_description_textbox.insert("1.0", existing_tool.get("description", ""))
                template_entry_new.delete(0, "end")
                template_entry_new.insert(0, existing_tool.get("template", ""))
                template_entry_new.configure(state="disabled")

                if not self.password_button_added:
                    def check_password_and_enable_code_field():
                        correct_password = "123"

                        password_window = ctk.CTkToplevel(self.root)
                        password_window.title("🔒 تأكيد الهوية")
                        password_window.geometry("420x300")
                        password_window.transient(self.root)
                        password_window.grab_set()

                        password_window.update_idletasks()
                        x = (password_window.winfo_screenwidth() // 2) - 210
                        y = (password_window.winfo_screenheight() // 2) - 125
                        password_window.geometry(f"+{x}+{y}")

                        frame = ctk.CTkFrame(password_window, corner_radius=15)
                        frame.pack(expand=True, fill="both", padx=20, pady=20)

                        ctk.CTkLabel(frame, text="🔐", font=ctk.CTkFont(size=55)).pack(pady=(15, 5))
                        ctk.CTkLabel(
                            frame, text="من فضلك أدخل كلمة السر", 
                            font=ctk.CTkFont(size=15, weight="bold")
                        ).pack(pady=(0, 18))

                        password_entry = ctk.CTkEntry(
                            frame, 
                            placeholder_text="كلمة السر", 
                            show="*", 
                            height=42, 
                            font=ctk.CTkFont(size=13),
                            corner_radius=8
                        )
                        password_entry.pack(fill="x", padx=40, pady=(0, 18))
                        password_entry.focus()

                        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
                        buttons_frame.pack(pady=(0, 10))

                        def verify_password():
                            password = password_entry.get().strip()
                            if password == correct_password:
                                template_entry_new.configure(state="normal")
                                messagebox.showinfo("تم", "✅ تم تمكين الكتابة في حقل الكود!")
                                password_window.destroy()
                            else:
                                messagebox.showerror("خطأ", "❌ كلمة السر غير صحيحة!")

                        ctk.CTkButton(
                            buttons_frame,
                            text="✅ تأكيد",
                            fg_color="#27ae60",
                            hover_color="#219150",
                            width=130,
                            height=42,
                            font=ctk.CTkFont(size=13, weight="bold"),
                            corner_radius=8,
                            command=verify_password
                        ).pack(side="left", padx=5)

                        ctk.CTkButton(
                            buttons_frame,
                            text="❌ إلغاء",
                            fg_color="#e74c3c",
                            hover_color="#c0392b",
                            width=130,
                            height=42,
                            font=ctk.CTkFont(size=13, weight="bold"),
                            corner_radius=8,
                            command=password_window.destroy
                        ).pack(side="left", padx=5)

                        password_entry.bind("<Return>", lambda e: verify_password())

                    custom_button = ctk.CTkButton(
                        main_frame, 
                        text="🔓 تمكين الكتابة في الكود", 
                        command=check_password_and_enable_code_field, 
                        width=220, 
                        height=45, 
                        font=("Arial", 14, "bold"),
                        fg_color=("#f39c12", "#d68910"),
                        hover_color=("#d68910", "#f39c12"),
                        corner_radius=10,
                        border_width=0
                    )
                    custom_button.pack(pady=15)
                    self.password_button_added = True
                
                if existing_tool.get("category") == "BOM":
                    project_name_entry.delete(0, "end")
                    project_name_entry.insert(0, existing_tool.get("project_name", ""))

                last_loaded_tool["name_ar"] = name_ar
                last_loaded_tool["name_en"] = name_en
                last_loaded_tool["loaded_from_existing"] = True
            else:
                last_loaded_tool["loaded_from_existing"] = False

        def add_prop_field_new(name="", value="", is_existing=False):
            prop_frame = ctk.CTkFrame(properties_container, corner_radius=8)
            prop_frame.pack(fill="x", padx=10, pady=5)

            labels_frame = ctk.CTkFrame(prop_frame, fg_color="transparent")
            labels_frame.pack(fill="x", padx=5, pady=(8, 2))

            ctk.CTkLabel(
                labels_frame, 
                text="اسم الخاصية", 
                font=("Arial", 11, "bold")
            ).pack(side="right", expand=True, fill="x", padx=(0, 5))
            ctk.CTkLabel(
                labels_frame, 
                text="قيمة الخاصية", 
                font=("Arial", 11, "bold")
            ).pack(side="right", expand=True, fill="x", padx=(5, 0))

            fields_frame = ctk.CTkFrame(prop_frame, fg_color="transparent")
            fields_frame.pack(fill="x", padx=5, pady=(0, 8))

            if is_existing:
                name_label = ctk.CTkLabel(
                    fields_frame, 
                    text=name, 
                    font=("Arial", 12, "bold"),
                    fg_color=("#e8f4f8", "#2d4a5c"),
                    corner_radius=6,
                    height=38
                )
                name_label.pack(side="right", expand=True, fill="x", padx=2)
                name_entry = None
            else:
                name_entry = ctk.CTkEntry(
                    fields_frame, 
                    font=("Arial", 12),
                    height=38,
                    corner_radius=6
                )
                name_entry.insert(0, name)
                name_entry.pack(side="right", expand=True, fill="x", padx=2)

            value_entry = ctk.CTkEntry(
                fields_frame, 
                font=("Arial", 12),
                height=38,
                corner_radius=6
            )
            value_entry.insert(0, value)
            value_entry.pack(side="right", expand=True, fill="x", padx=2)

            if not is_existing:
                delete_btn = ctk.CTkButton(
                    fields_frame, 
                    text="✖", 
                    width=38,
                    height=38,
                    command=lambda: [props_fields.remove((name_entry, value_entry)), prop_frame.destroy()],
                    fg_color="#e74c3c", 
                    hover_color="#c0392b",
                    corner_radius=6,
                    font=("Arial", 14, "bold")
                )
                delete_btn.pack(side="left", padx=2)

            props_fields.append((name_entry if name_entry else name, value_entry))

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



                                # ✅ تحقق من إدخال صيغة الكود قبل الحفظ مع تأثيرات بصرية و focus تلقائي
            if not template_entry_new.get().strip():
                # حفظ اللون الأصلي
                original_color = template_entry_new.cget("fg_color")

                # تغيير اللون مؤقتًا للأحمر
                template_entry_new.configure(fg_color="#ff4d4d")

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
                    template_entry_new.configure(fg_color=original_color)
                    template_entry_new.focus_set()

                new_tool_window.after(600, reset_field_color)

                messagebox.showerror("❌ خطأ", "الرجاء إدخال صيغة الكود قبل حفظ الأداة.")
                return


            properties_dict = {}
            for name_widget, value_entry in props_fields:
                if isinstance(name_widget, str):
                    prop_name = name_widget
                else:
                    prop_name = name_widget.get().strip()
                    if not prop_name:
                        continue

                if prop_name in properties_dict:
                    messagebox.showerror("خطأ", f"الخاصية '{prop_name}' مكررة.")
                    return

                properties_dict[prop_name] = value_entry.get().strip()

            if not properties_dict:
                messagebox.showerror("خطأ", "الرجاء إدخال خاصية واحدة على الأقل.")
                return
           
            new_tool_data = {
                "name_ar": tool_name_ar,
                "name_en": tool_name_en,
                "category": category_menu.get(),
                "description": tool_description_textbox.get("1.0", "end-1c").strip(),
                "properties": properties_dict,
                "template": template_entry_new.get().strip()
            }

            if category_menu.get() == "BOM":
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
                messagebox.showinfo("✅ نجاح", "تمت إضافة الأداة بنجاح كمنتج جديد.")
                user = getattr(self, "logged_in_user", None) or getattr(SyncManager, "logged_in_user", None)

                self.history.log_action(
                    user = user, 
                    action="اضافة منتج", 
                    item=new_final_code,
                    details=None,
                    status="✅ Success"
                )
                #self.history.log_action(self.data_manager.current_user, "Added Product", new_tool_data.get("name", "Unknown"), "Success")

                if hasattr(self, "ui_manager"):
                    self.ui_manager.reload_data()
                elif hasattr(self, "reload_data"):
                    self.reload_data()
                else:
                    self.update_products_list()
                    

                # ✅ استدعاء المزامنة التلقائية مع Google Sheets من خلال SyncManager
                if hasattr(self, "sync_manager") and self.sync_manager:
                    threading.Thread(target=self.sync_manager.sync_all, daemon=True).start()
                    print("🚀 تم رفع الأداة الجديدة تلقائيًا إلى Google Sheets.")
                else:
                    print("⚠️ لم يتم تهيئة SyncManager بعد، لن يتم رفع الأداة.")
    
                new_tool_window.destroy()




        ctk.CTkButton(
            properties_container, 
            text="➕ إضافة خاصية", 
            command=add_prop_field_new,
            height=38,
            font=("Arial", 12, "bold"),
            fg_color=("#27ae60", "#1e8449"),
            hover_color=("#1e8449", "#27ae60"),
            corner_radius=8
        ).pack(padx=10, pady=10)
        
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