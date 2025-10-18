import pandas as pd
from tkinter import messagebox, filedialog

class ExportExcelMixin:
    def export_data_to_excel(self, data_list, file_path, success_message):
            if not data_list:
                messagebox.showwarning("تنبيه", "لا يوجد شيء لتصديره.")
                return False

            try:
                data_to_export = []
                for item in data_list:
                    final_code = self.get_final_code(item)
                    row_data = {
                        "الاسم العربي": item.get("name_ar", ""),
                        "الاسم الإنجليزي": item.get("name_en", ""),
                        "الفئة": item.get("category", ""),
                        "اسم المشروع": item.get("project_name", ""),
                        "الوصف": item.get("description", ""),
                        "الكود النهائي": final_code,
                    }
                    for prop_name, prop_value in item.get("properties", {}).items():
                        row_data[f"خاصية - {prop_name}"] = prop_value
                    data_to_export.append(row_data)
                df = pd.DataFrame(data_to_export)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("✅ نجاح", success_message)
                return True
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل التصدير إلى Excel.\nالخطأ: {e}")
                return False

    def export_selected_to_excel(self):
        if not self.selected_items:
            messagebox.showwarning("تنبيه", "الرجاء اختيار منتج واحد على الأقل.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        items_list = list(self.selected_items.values())
        if self.export_data_to_excel(items_list, file_path, f"تم تصدير {len(items_list)} منتج بنجاح."):
            self.selected_items.clear()
            self.update_products_list()


    def export_named_list_to_excel(self, list_name):
        lists_data = self.data_manager.load_lists()
        products_to_export = lists_data.get(list_name, [])
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile=f"{list_name}.xlsx")
        if not file_path:
            return
        self.export_data_to_excel(products_to_export, file_path, f"تم تصدير {len(products_to_export)} منتج من قائمة '{list_name}' بنجاح.")