import win32ui
import win32print
import win32con
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageWin, ImageDraw, ImageFont
from io import BytesIO
from barcode.codex import Code128
from tkinter import messagebox
import customtkinter as ctk
from functools import partial
class PrinterMixin:
    def generate_barcode_image_in_memory(self, code,  dpi=203):
        # إنشاء الباركود
        barcode_class = Code128
        barcode_obj = barcode_class(code, writer=ImageWriter())
        # إعدادات الكتابة
        options = {
            "module_width": 0.25,
            "module_height": 15.0,
            "font_size": 10,
            "text_distance": 2.0,
            "quiet_zone": 2.0,
            "write_text": False,
        }
        # حفظ في ذاكرة مؤقتة
        image_stream = BytesIO()
        barcode_obj.write(image_stream, options)
        image_stream.seek(0)
        # فتح الصورة باستخدام PIL
        pil_image = Image.open(image_stream).convert("RGB")
        # إضافة النص تحت الباركود
        
        try:
            font = ImageFont.truetype("arial.ttf", 14)  # خط واضح
        except:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(pil_image)
        bbox = draw.textbbox((0, 0), code, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # إنشاء صورة جديدة أطول بمساحة النص
        new_height = pil_image.height + text_h + 5
        new_img = Image.new("RGB", (pil_image.width, new_height), "white")
        new_img.paste(pil_image, (0, 0))
        # رسم الكود تحت الباركود
        draw = ImageDraw.Draw(new_img)
        draw.text(
            ((new_img.width - text_w) // 2, pil_image.height + 2),
            code,
            font=font,
            fill="black",
        )
        # ضبط DPI
        new_img.info["dpi"] = (dpi, dpi)
        return new_img
    
    def generate_and_print_barcode(self, code, copies=1):
        # توليد الباركود بجودة عالية (تم حذف copies=1 لأنه غير ضروري هنا)
        width_inches = 1.97  # ← العرض الحقيقي للاستيكر
        height_inches = 0.98  # ← الارتفاع
        dpi=203
        img = self.generate_barcode_image_in_memory(code, dpi=dpi)
        if img:
            self.print_barcode(
                pil_image=img, 
                printer_name=None,  # يستخدم الافتراضية
                copies=copies,      
                width_inches=width_inches,
                height_inches=height_inches,
                dpi=dpi
            )
    def print_barcode(self, pil_image, printer_name=None, copies=1, width_inches=1.97, height_inches=0.98, dpi=203):
        width_px = int(width_inches * dpi)
        height_px = int(height_inches * dpi)

        if printer_name is None:
            printer_name = win32print.GetDefaultPrinter()

        pil_image = pil_image.resize((width_px, height_px), Image.Resampling.LANCZOS)

        hprinter = win32print.OpenPrinter(printer_name)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc("Barcode Print")

        for _ in range(copies):
            pdc.StartPage()
            dib = ImageWin.Dib(pil_image)
            dib.draw(pdc.GetHandleOutput(), (0, 0, width_px, height_px))
            pdc.EndPage()

        # ✅ ورقة إضافية للـ Feed
        pdc.StartPage()
        pdc.EndPage()

        pdc.EndDoc()
        pdc.DeleteDC()
        win32print.ClosePrinter(hprinter)


    def get_available_printers(self):
        try:
            printers = [p[2] for p in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )]
            return printers
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في الحصول على قائمة الطابعات:\n{str(e)}")
            return []
    def show_printer_selection_dialog(self):
        """عرض نافذة اختيار الطابعة"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("اختيار الطابعة")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        ctk.CTkLabel(
            dialog, 
            text="اختر الطابعة الافتراضية:", 
            font=("Arial", 14, "bold")
        ).pack(pady=15)
        
        printers = self.get_available_printers()
        
        if not printers:
            messagebox.showerror("خطأ", "لا توجد طابعات متاحة على هذا الجهاز.")
            dialog.destroy()
            return
        
        try:
            current_printer = win32print.GetDefaultPrinter()
        except:
            current_printer = printers[0] if printers else ""
        
        printer_var = ctk.StringVar(value=current_printer)
        printer_menu = ctk.CTkOptionMenu(
            dialog, 
            variable=printer_var, 
            values=printers,
            width=350
        )
        printer_menu.pack(pady=10)
        
        # عرض الطابعة الحالية
        current_label = ctk.CTkLabel(
            dialog,
            text=f"الطابعة الحالية: {current_printer}",
            font=("Arial", 10),
            text_color="gray"
        )
        current_label.pack(pady=5)
        def set_default_printer():
            try:
                selected_printer = printer_var.get()
                win32print.SetDefaultPrinter(selected_printer)
                messagebox.showinfo(
                    "✅ نجاح", 
                    f"تم تحديد الطابعة:\n'{selected_printer}'\nكطابعة افتراضية."
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في تعيين الطابعة:\n{str(e)}")
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=15)
        
        ctk.CTkButton(
            button_frame, 
            text="✅ تأكيد", 
            command=set_default_printer, 
            font=("Arial", 12),
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ إلغاء",
            command=dialog.destroy,
            font=("Arial", 12),
            width=120,
            fg_color="gray"
        ).pack(side="left", padx=5)
    def show_print_dialog(self, code):
        """عرض نافذة إعدادات الطباعة (عدد النسخ فقط)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("إعدادات الطباعة")
        dialog.geometry("350x220")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        # عنوان
        ctk.CTkLabel(
            dialog, 
            text="⚙️ إعدادات الطباعة", 
            font=("Arial", 16, "bold")
        ).pack(pady=15)
        # عدد النسخ
        ctk.CTkLabel(dialog, text="عدد النسخ:", font=("Arial", 12)).pack(pady=5)
        copies_entry = ctk.CTkEntry(dialog, placeholder_text="1", width=120)
        copies_entry.pack(pady=5)
        copies_entry.insert(0, "1")
        def start_printing():
            try:
                print(f"copies_entry value: {copies_entry.get()}")
                print(f"Raw: {copies_entry.get()}, Stripped: '{copies_entry.get().strip()}', Type: {type(copies_entry.get())}")
                copies = int(copies_entry.get().strip())
                if copies <= 0:
                    messagebox.showerror("خطأ", "العدد يجب أن يكون أكبر من صفر.")
                    copies_entry.focus()
                    return
                
                dialog.destroy()
                self.generate_and_print_barcode(code, copies)
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح.")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {e}")
        # أزرار
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="🖨️ طباعة",
            command=start_printing,
            font=("Arial", 13, "bold"),
            width=120,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ إلغاء",
            command=dialog.destroy,
            font=("Arial", 13),
            width=120,
            height=35,
            fg_color="gray"
        ).pack(side="left", padx=5)
# Example of usage
#printer_mixin = PrinterMixin()
#printer_mixin.generate_and_print_barcode("123456789", "Product123", copies=1)






