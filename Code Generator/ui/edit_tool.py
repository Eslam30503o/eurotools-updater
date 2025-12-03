import customtkinter as ctk
from tkinter import messagebox
import json
import threading
import json
from pathlib import Path
import time 
from sync.manager import SyncManager
from categories import CATEGORIES
import os


CATEGORIES = CATEGORIES

class EditToolMixin:
    def edit_tool_window(self, tool_name_en_to_edit):

        """طلب كلمة السر قبل فتح نافذة التعديل"""

        base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "EuroTools" / "data"
        self.SETTING = str(base_dir / "app_settings.json")
        os.makedirs(base_dir, exist_ok=True)

       
        if os.path.exists(self.SETTING):
            with open(self.SETTING, "r", encoding="utf-8") as f:
                settings = json.load(f)
            correct_password = settings.get("admin_password", "Admin@123")
        else:
            correct_password = "Admin@123"


        password_window = ctk.CTkToplevel(self.root)
        password_window.title("🔒 تأكيد الهوية")
        password_window.geometry("420x300")
        password_window.transient(self.root)
        password_window.grab_set()

        # توسيط النافذة
        password_window.update_idletasks()
        x = (password_window.winfo_screenwidth() // 2) - 210
        y = (password_window.winfo_screenheight() // 2) - 125
        password_window.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(password_window, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="🔐",
            font=("Arial", 13, "bold"),
            text_color="white"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            frame,
            text="أدخل كلمة السر لتعديل البيانات",
            font=("Arial", 13, "bold"),
            text_color="white"
        ).pack(pady=(0, 18))

        password_entry = ctk.CTkEntry(
            frame, 
            placeholder_text="كلمة السر", 
            show="*", 
            height=42,
            font=("Arial", 13, "bold"),
            text_color="white",
            corner_radius=8
        )
        password_entry.pack(fill="x", padx=40, pady=(0, 18))
        password_entry.focus()

        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 10))

        def verify_password():
            password = password_entry.get().strip()
            print(f"🔑 دخلت كلمة السر: '{password}'")
            print(f"📦 كلمة السر الصحيحة من الملف: '{correct_password}'")

            if password == correct_password:
                print("✅ كلمة السر صحيحة")
                password_window.destroy()
                self._open_edit_tool_window(tool_name_en_to_edit)
            else:
                print("❌ كلمة السر خاطئة")
                messagebox.showerror("خطأ", "❌ كلمة السر غير صحيحة!")


        ctk.CTkButton(
            buttons_frame,
            text="✅ تأكيد",
            fg_color="#27ae60",
            hover_color="#219150",
            width=130,
            height=42,
            font=("Arial", 13, "bold"),
            text_color="white",
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
            font=("Arial", 13, "bold"),
            text_color="white",
            corner_radius=8,
            command=password_window.destroy
        ).pack(side="left", padx=5)

        password_entry.bind("<Return>", lambda e: verify_password())

    def _open_edit_tool_window(self, tool_name_en_to_edit):
        tools_data = self.data_manager.load_tools()

        # ✅ دعم list
        if isinstance(tools_data, dict):
            selected_tool_data = tools_data.get(tool_name_en_to_edit, {})
        else:
            selected_tool_data = next(
                (t for t in tools_data if t.get("name_en", "") == tool_name_en_to_edit), 
                {}
            )
                
        if not selected_tool_data:
            messagebox.showerror("خطأ", "لم يتم العثور على الأداة للتعديل.")
            return

        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title(f"✍️ تعديل: {selected_tool_data['name_ar']}")
        edit_window.geometry("600x750")
        edit_window.resizable(True, True)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # توسيط النافذة
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - 300
        y = (edit_window.winfo_screenheight() // 2) - 375
        edit_window.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkScrollableFrame(edit_window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # العنوان الرئيسي
        header_frame = ctk.CTkFrame(main_frame, fg_color=("#e67e22", "#d35400"), corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            header_frame, 
            text=f"{selected_tool_data['name_en']} : ✍️تعديل", 
            font=("Arial", 22, "bold"),
            text_color="white"
        ).pack(pady=15)

        # قسم الأسماء
        names_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        names_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            names_frame, 
            text="📝 الاسم بالإنجليزية:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        name_en_label = ctk.CTkLabel(
            names_frame, 
            text=selected_tool_data.get("name_en", tool_name_en_to_edit),
            font=("Arial", 12),
            height=40,
            corner_radius=8,
            fg_color="#2c3e50",  # لون الخلفية
            text_color="white"   # لون النص
            
        )
        name_en_label.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            names_frame, 
            text="📝 الاسم بالعربية:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(5, 5))
        name_ar_label = ctk.CTkLabel(
            names_frame, 
            text=selected_tool_data.get("name_ar", ""),
            font=("Arial", 12),
            height=40,
            corner_radius=8,
            fg_color="#2c3e50",  # لون الخلفية
            text_color="white"   # لون النص
        )
        name_ar_label.pack(fill="x", padx=15, pady=(0, 15))

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
            values=CATEGORIES[1:],
            height=40,
            font=("Arial", 12),
            corner_radius=8,
            button_color=("#e67e22", "#d35400"),
            button_hover_color=("#d35400", "#e67e22")
        )
        category_menu.set(selected_tool_data.get("category", "أخرى"))
        category_menu.pack(fill="x", padx=15, pady=(0, 15))

        # حقل المشروع
        project_name_label = ctk.CTkLabel(
            category_frame, 
            text="🔖 اسم المشروع اوالمكنة", 
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        project_name_entry = ctk.CTkEntry(
            category_frame, 
            placeholder_text=" أدخل اسم المشروع او المكنة",
            height=40,
            font=("Arial", 12),
            corner_radius=8
        )

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

        if selected_tool_data.get("category") == "BOM":
            project_name_entry.insert(0, selected_tool_data.get("project_name", ""))
            toggle_project_name_field("BOM")

        elif selected_tool_data.get("category") == "Machine Spare Parts":
            project_name_entry.insert(0, selected_tool_data.get("project_name", ""))
            toggle_project_name_field("Machine Spare Parts")

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
        tool_description_textbox.insert("1.0", selected_tool_data.get("description", ""))
        tool_description_textbox.pack(fill="x", padx=15, pady=(0, 15))

        # قسم صيغة الكود
        template_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        template_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            template_frame, 
            text="🔢 صيغة الكود:", 
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        template_label = ctk.CTkLabel(
            template_frame, 
            text=selected_tool_data.get("template", ""),
            height=40,
            font=("Consolas", 16),
            fg_color=("#1e1e1e", "#1e1e1e"),
            text_color="#00FF7F",
            corner_radius=8   # لون النص
        )
        template_label.pack(fill="y", padx=15, pady=(0, 15))

        # قسم الخصائص
        properties_container = ctk.CTkFrame(main_frame, corner_radius=12)
        properties_container.pack(fill="x", pady=(0, 15))
        
        props_header = ctk.CTkFrame(properties_container, fg_color=("#e67e22", "#d35400"), corner_radius=10)
        props_header.pack(fill="x", padx=10, pady=(10, 10))
        ctk.CTkLabel(
            props_header, 
            text="⚙️ الخصائص", 
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(pady=8)

        existing_props_entries = {}
        new_props_fields = {}

        def add_prop_field(name="", value="", is_existing=False):
            prop_frame = ctk.CTkFrame(properties_container, corner_radius=8)
            prop_frame.pack(fill="x", padx=10, pady=5)

            if is_existing:
                labels_frame = ctk.CTkFrame(prop_frame, fg_color="transparent")
                labels_frame.pack(fill="x", padx=5, pady=(8, 2))
                
                ctk.CTkLabel(
                    labels_frame, 
                    text=name, 
                    font=("Arial", 11, "bold")
                ).pack(side="right", padx=5)
                
                fields_frame = ctk.CTkFrame(prop_frame, fg_color="transparent")
                fields_frame.pack(fill="x", padx=5, pady=(0, 8))
                
                value_entry = ctk.CTkEntry(
                    fields_frame, 
                    font=("Arial", 12),
                    height=38,
                    corner_radius=6
                    #,state="enabled"
                )
                value_entry.insert(0, value)
                value_entry.pack(side="right", expand=True, fill="x", padx=2)
                existing_props_entries[name] = value_entry
            else:
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

                new_props_fields[name_entry] = value_entry

        for name, value in selected_tool_data.get("properties", {}).items():
            add_prop_field(name, value, is_existing=True)


        def save_changes():
            nonlocal tool_name_en_to_edit

            # 🔹 تحميل البيانات الأصلية من JSON
            tools_data = self.data_manager.load_tools()
            original_tool = None

            # البحث عن الأداة الأصلية
            if isinstance(tools_data, dict):
                original_tool = tools_data.get(tool_name_en_to_edit)
            else:
                original_tool = next((t for t in tools_data if t.get("name_en") == tool_name_en_to_edit), None)

            if not original_tool:
                messagebox.showerror("خطأ", "❌ لم يتم العثور على الأداة الأصلية في البيانات.")
                return

            # 🔹 تجميع الخصائص القديمة والجديدة
            properties_dict = {}
            for name, entry in existing_props_entries.items():
                properties_dict[name] = entry.get().strip()

            for name_entry, value_entry in new_props_fields.items():
                prop_name = name_entry.get().strip()
                if not prop_name:
                    continue
                if prop_name in properties_dict:
                    messagebox.showerror("خطأ", f"الخاصية '{prop_name}' مكررة.")
                    return
                properties_dict[prop_name] = value_entry.get().strip()

            # 🔹 البيانات الجديدة المقترحة
            # 🔹 البيانات الجديدة المقترحة
            new_name_en = name_en_label.cget("text").strip()  # استخدم cget بدلاً من get()
            if not new_name_en:
                messagebox.showerror("خطأ", "يجب إدخال اسم إنجليزي.")
                return

            created_at = original_tool.get("created_at", time.time())

            updated_tool_data = {
                "name_en": new_name_en,
                "name_ar": name_ar_label.cget("text").strip(),  # أيضاً استخدم cget للحصول على النص
                "category": category_menu.get(),
                "description": tool_description_textbox.get("1.0", "end-1c").strip(),
                "properties": properties_dict,
                "template": template_label.cget("text").strip(),  # نفس الشيء مع template_label
                "updated_at": time.time(),
                "created_at": created_at
            }


            if category_menu.get() == "BOM" or "Machine Spare Parts":
                updated_tool_data["project_name"] = project_name_entry.get().strip()

            # 🔹 مقارنة النسخة الجديدة بالقديمة
            def normalize(d):
                """تحويل dict إلى شكل موحّد للمقارنة."""
                return json.dumps(d, sort_keys=True, ensure_ascii=False)

            if normalize(original_tool) == normalize(updated_tool_data):
                # لا يوجد أي تغيير فعلي
                messagebox.showinfo("ℹ️ لا تغيير", "لم يتم تعديل أي بيانات، لم يتم الحفظ.")
                edit_window.destroy()
                return

            # 🔹 تحديث JSON محليًا
            if isinstance(tools_data, dict):
                tools_data[new_name_en] = updated_tool_data
                if new_name_en != tool_name_en_to_edit:
                    del tools_data[tool_name_en_to_edit]
            else:
                for i, tool in enumerate(tools_data):
                    if tool.get("name_en") == tool_name_en_to_edit:
                        tools_data[i] = updated_tool_data
                        break
                else:
                    tools_data.append(updated_tool_data)

            # ✅ حفظ البيانات محليًا
            if self.data_manager.save_tools(tools_data):
                #messagebox.showinfo("✅ نجاح", "تم حفظ التعديلات بنجاح.")
                self.update_products_list()
                edit_window.destroy()

                # ✅ تحديث الأداة في Google Sheets (في خيط منفصل)
                try:
                    if hasattr(self, "sync_manager") and self.sync_manager:
                        final_code = self.get_final_code(updated_tool_data).strip().lower()

                        def update_in_sheet():
                            print(f"📝 جارٍ تحديث الأداة في Google Sheets ({final_code})...")
                            # 🧠 قبل التحديث — احفظ القيم القديمة من الشيت
                            try:
                                ws = self.sync_manager.sheet.worksheet("ProductsData")  # ← استبدل "Tools" باسم الورقة الحقيقي
                                all_rows = ws.get_all_records()
                                old_row = next((r for r in all_rows if str(r.get("final_code")) == str(final_code)), None)
                            except Exception as e:
                                print(f"⚠️ فشل في جلب القيم القديمة: {e}")
                                old_row = None

                            ok = self.sync_manager.update_product_in_sheet(final_code, updated_tool_data)
                            if ok:

                                # 📄 بعد التحديث — احصل على القيم الجديدة
                                try:
                                    all_rows = ws.get_all_records()
                                    new_row = next((r for r in all_rows if str(r.get("final_code")) == str(final_code)), None)
                                except Exception as e:
                                    print(f"⚠️ فشل في جلب القيم الجديدة: {e}")
                                    new_row = None

                                # 🧩 قارن القيم القديمة والجديدة
                                changes = []
                                if old_row and new_row:
                                    for key in new_row.keys():
                                        if key in ["updated_at", "last_modified", "timestamp"]:
                                            continue
                                        old_val = str(old_row.get(key, "")).strip()
                                        new_val = str(new_row.get(key, "")).strip()
                                        if old_val != new_val:
                                            changes.append(f"{key}:\n {old_val} → {new_val}")

                                change_summary = " | ".join(changes) if changes else "بدون تغييرات"

                                if hasattr(self, "show_toast"):
                                    self.show_toast(" تم تحديث الأداة  ", "success")
                                    #print(self.logged_in_user , "الاسم المتسجل : ")


                                    user = getattr(self, "logged_in_user", None) or getattr(SyncManager, "logged_in_user", None)
                                    #print("👤 logged_in_user =", user)

                                    self.history.log_action(
                                        user = user, 
                                        action="تعديل منتج", 
                                        item=final_code,
                                        details=change_summary,
                                        status="✅ Success"
                                    )

                            else:
                                print("⚠️ لم يتم العثور على الأداة في Google Sheets.")
                                if hasattr(self, "show_toast"):
                                    self.show_toast("⚠️ لم يتم العثور على الأداة  ", "warning")

                        threading.Thread(target=update_in_sheet, daemon=True).start()
                    else:
                        print("⚠️ SyncManager غير جاهز، لن يتم تحديث Google Sheets.")
                except Exception as e:
                    print(f"⚠️ خطأ أثناء تحديث الأداة في Google Sheets: {e}")


        save_button = ctk.CTkButton(
            main_frame, 
            text="💾 حفظ التغييرات", 
            command=save_changes,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color=("#e67e22", "#d35400"),
            hover_color=("#d35400", "#e67e22"),
            corner_radius=12
        )
        save_button.pack(pady=20, fill="x")