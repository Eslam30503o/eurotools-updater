import customtkinter as ctk
from functools import partial
from tkinter import messagebox
import tkinter as tk
import json
from pathlib import Path
from ui.history_screen import HistoryScreen
from sync.manager import SyncManager
import threading
from categories import CATEGORIES


CATEGORIES = CATEGORIES
class ProductToastMixin:

    def show_toast(self, message, msg_type="info", duration=3000):
        """رسالة Toast احترافية"""
        # 🧹 إلغاء أي Toast قديم
        if hasattr(self, "_active_toast") and self._active_toast.winfo_exists():
            self._active_toast.destroy()

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
        
        toast_frame = ctk.CTkFrame(toast, fg_color=bg_color, corner_radius=12)
        toast_frame.pack(padx=3, pady=3)
        
        icons = {
            "success": "✅",
            "error": "❌",
            "info": "ℹ️",
            "warning": "⚠️"
        }
        
        content_frame = ctk.CTkFrame(toast_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=15)
        
        ctk.CTkLabel(content_frame, text=icons.get(msg_type, "ℹ️"), font=("Arial", 20)).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(content_frame, text=message, font=("Cairo", 14, "bold"), text_color=text_color).pack(side="left")
        
        toast.update_idletasks()
        width = toast.winfo_reqwidth()
        height = toast.winfo_reqheight()
        screen_width = toast.winfo_screenwidth()
        x = (screen_width // 2) - (width // 2)
        y = 80
        toast.geometry(f"{width}x{height}+{x}+{y}")
        
        toast.deiconify()
        toast.attributes("-topmost", True)
        self._active_toast = toast
        
        toast.after(duration, toast.destroy)
