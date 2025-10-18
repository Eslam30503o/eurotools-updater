import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageFilter, ImageEnhance
import threading
import time
import os
import json
import bcrypt
from typing import Callable, Optional

from config import AppConfig
from data_manager import DataManager
from google_users import verify_user, add_user


class LoadingOverlay:
    """Premium loading overlay with smooth animations"""
    
    def __init__(self, parent, message="جاري التحميل..."):
        # Semi-transparent dark overlay
        self.overlay = ctk.CTkFrame(
            parent,
            fg_color=("#1A1A1A", "#0A0A0A"),
            corner_radius=0
        )
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Loading container with blur effect simulation
        self.blur_frame = ctk.CTkFrame(
            self.overlay,
            fg_color=("#2C2C2C", "#1A1A1A"),
            corner_radius=16,
            border_width=1,
            border_color=("#3A3A3A", "#2A2A2A")
        )
        self.blur_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        loading_frame = ctk.CTkFrame(
            self.blur_frame,
            fg_color="transparent",
            width=320,
            height=200
        )
        loading_frame.pack(padx=40, pady=30)
        loading_frame.pack_propagate(False)
        
        # Animated spinner
        self.spinner_label = ctk.CTkLabel(
            loading_frame,
            text="",
            font=("Segoe UI", 45),
            text_color=("#3498DB", "#3498DB")
        )
        self.spinner_label.pack(pady=(20, 15))
        
        # Loading message
        self.message_label = ctk.CTkLabel(
            loading_frame,
            text=message,
            font=("Cairo", 15, "bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        )
        self.message_label.pack(pady=8)
        
        # Progress dots
        self.dots_label = ctk.CTkLabel(
            loading_frame,
            text="",
            font=("Cairo", 14),
            text_color=("#95A5A6", "#95A5A6")
        )
        self.dots_label.pack(pady=(5, 15))
        
        self.is_active = True
        self.spinner_frames = ["◐", "◓", "◑", "◒"]
        self.current_frame = 0
        self.dots_count = 0
        
        self._animate()
    
    def _animate(self):
        if not self.is_active:
            return
        
        # Spinner animation
        self.spinner_label.configure(text=self.spinner_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.spinner_frames)
        
        # Dots animation
        dots = "." * (self.dots_count % 4)
        self.dots_label.configure(text=dots)
        self.dots_count += 1
        
        self.overlay.after(150, self._animate)
    
    def update_message(self, message):
        self.message_label.configure(text=message)
    
    def destroy(self):
        self.is_active = False
        self.overlay.destroy()


class LoginScreen:

    ADMIN_PASSWORD = "admin@123"
    
    COLORS = {
        "primary": "#2C3E50",
        "primary_hover": "#34495E",
        "success": "#27AE60",
        "success_hover": "#229954",
        "danger": "#E74C3C",
        "accent": "#3498DB",
        "bg_light": "#F8F9FA",
        "bg_dark": "#0F1729",
        "card_light": "#FFFFFF",
        "card_dark": "#1A1A2E",
        "text_primary": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "border": "#E8E8E8",
        "border_dark": "#2C3E50"
    }

    def __init__(self, root: ctk.CTk, app_ref, on_success_callback: Callable):
        self.root = root
        self.app_ref = app_ref
        self.on_success = on_success_callback
        
        self.data_manager = DataManager()
        self.local_file = os.path.join(self.data_manager.safe_data_dir, "login.json")
        
        self._animation_running = True
        self.loading_overlay = None
        self._init_ui()
        self._load_saved_credentials()
        self._bind_events()
        self._start_animations()

    def _init_ui(self) -> None:
        # Main container with gradient background
        self.container = ctk.CTkFrame(
            self.root,
            fg_color=(self.COLORS["bg_light"], self.COLORS["bg_dark"])
        )
        self.container.pack(fill="both", expand=True)
        
        # Subtle background pattern
        self._create_background_pattern()
        
        # Main card with premium shadow
        self.main_card = ctk.CTkFrame(
            self.container,
            fg_color=(self.COLORS["card_light"], self.COLORS["card_dark"]),
            corner_radius=24,
            border_width=1,
            border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
            width=460,
            height=620
        )
        self.main_card.place(relx=0.5, rely=0.5, anchor="center")
        self.main_card.pack_propagate(False)
        
        self._create_header()
        self._create_input_fields()
        self._create_action_buttons()
        self._create_footer()

    def _create_background_pattern(self) -> None:
        """Subtle geometric pattern"""
        bg_canvas = ctk.CTkCanvas(
            self.container,
            bg=(self.COLORS["bg_light"] if ctk.get_appearance_mode() == "Light" else self.COLORS["bg_dark"]),
            highlightthickness=0
        )
        bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Minimal geometric shapes
        color = "#E8E8E8" if ctk.get_appearance_mode() == "Light" else "#1A1A2E"
        for i in range(8):
            x = 100 + i * 180
            y = 80 + (i % 3) * 200
            bg_canvas.create_rectangle(
                x, y, x + 60, y + 60,
                fill="", outline=color, width=1
            )

    def _create_header(self) -> None:
        header_frame = ctk.CTkFrame(
            self.main_card,
            fg_color="transparent"
        )
        header_frame.pack(pady=(30, 15), padx=40)
        
        # Logo
        self._load_logo(header_frame)
        
        # Title with elegant typography
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="EURO TOOLS",
            font=("Helvetica Neue", 34, "bold"),
            text_color=(self.COLORS["primary"], "#FFFFFF")
        )
        self.title_label.pack(pady=(15, 5))
        
        # Subtitle
        ctk.CTkLabel(
            header_frame,
            text="Code Manager Pro",
            font=("Helvetica Neue", 13),
            text_color=(self.COLORS["text_secondary"], "#95A5A6")
        ).pack()
        
        # Divider line
        divider = ctk.CTkFrame(
            header_frame,
            height=2,
            width=80,
            fg_color=(self.COLORS["accent"], self.COLORS["accent"])
        )
        divider.pack(pady=(12, 0))

    def _load_logo(self, parent) -> None:
        try:
            logo_path = AppConfig.LOGO_IMAGE
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                
                # Subtle shadow effect
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)
                
                logo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                logo_label = ctk.CTkLabel(parent, image=logo, text="")
                logo_label.image = logo
            else:
                logo_label = ctk.CTkLabel(
                    parent,
                    text="🛠️",
                    font=("Segoe UI Emoji", 50)
                )
            logo_label.pack()
            
        except Exception as e:
            print(f"Logo error: {e}")

    def _create_input_fields(self) -> None:
        self.input_frame = ctk.CTkFrame(
            self.main_card,
            fg_color="transparent"
        )
        self.input_frame.pack(pady=18, padx=40)

        # Username field
        username_container = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        username_container.pack(pady=(0, 12), fill="x")

        ctk.CTkLabel(
            username_container,
            text="اسم المستخدم",
            font=("Cairo", 12, "bold"),
            text_color=(self.COLORS["text_primary"], "#FFFFFF"),
            anchor="w"
        ).pack(fill="x", pady=(0, 6))

        self.username_entry = self._create_premium_entry(
            username_container,
            "أدخل اسم المستخدم",
            False
        )
        self.username_entry.pack(fill="x")

        # Password field
        password_container = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        password_container.pack(pady=(0, 8), fill="x")

        ctk.CTkLabel(
            password_container,
            text="كلمة المرور",
            font=("Cairo", 12, "bold"),
            text_color=(self.COLORS["text_primary"], "#FFFFFF"),
            anchor="w"
        ).pack(fill="x", pady=(0, 6))

        password_input_frame = ctk.CTkFrame(password_container, fg_color="transparent")
        password_input_frame.pack(fill="x")

        self.password_entry = self._create_premium_entry(
            password_input_frame,
            "أدخل كلمة المرور",
            True
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        # Toggle password button
        self._show_pass = False
        self.toggle_btn = ctk.CTkButton(
            password_input_frame,
            text="👁",
            width=46,
            height=46,
            corner_radius=12,
            fg_color="transparent",
            hover_color=(self.COLORS["border"], "#2C3E50"),
            border_width=1,
            border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
            command=self._toggle_password,
            font=("Segoe UI", 16)
        )
        self.toggle_btn.pack(side="left", padx=(8, 0))

        # ✅ CheckBox: Remember Me
        self.remember_check = ctk.CTkCheckBox(
            self.input_frame,
            text="تذكرني",
            font=("Cairo", 12),
            text_color=(self.COLORS["text_primary"], "#FFFFFF")
        )
        self.remember_check.pack(pady=(6, 2), anchor="w")

        # Status label
        self.status_label = ctk.CTkLabel(
            self.input_frame,
            text="",
            font=("Cairo", 11),
            text_color=self.COLORS["text_secondary"],
            height=20
        )
        self.status_label.pack(pady=(12, 0))


    def _create_premium_entry(self, parent, placeholder: str, is_password: bool) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=46,
            corner_radius=12,
            border_width=1,
            border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
            fg_color=(self.COLORS["card_light"], "#0F1729"),
            font=("Cairo", 13),
            show="●" if is_password else ""
        )
        
        # Elegant focus effects
        def on_focus_in(e):
            entry.configure(
                border_color=(self.COLORS["accent"], self.COLORS["accent"]),
                border_width=2
            )
        
        def on_focus_out(e):
            entry.configure(
                border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
                border_width=1
            )
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
        return entry

    def _create_action_buttons(self) -> None:
        button_frame = ctk.CTkFrame(
            self.main_card,
            fg_color="transparent"
        )
        button_frame.pack(pady=15, padx=40, fill="x")
        
        # Primary login button
        self.login_btn = ctk.CTkButton(
            button_frame,
            text="تسجيل الدخول",
            height=50,
            corner_radius=12,
            font=("Cairo", 15, "bold"),
            fg_color=(self.COLORS["primary"], self.COLORS["primary"]),
            hover_color=(self.COLORS["primary_hover"], self.COLORS["primary_hover"]),
            command=self._handle_login,
            border_width=0
        )
        self.login_btn.pack(fill="x", pady=(0, 10))
        
        # Secondary add user button - WITH CLEAR TEXT AND ICON
        self.add_user_btn = ctk.CTkButton(
            button_frame,
            text="➕  إنشاء مستخدم جديد",
            height=46,
            corner_radius=12,
            font=("Cairo", 14, "bold"),
            fg_color="transparent",
            hover_color=(self.COLORS["border"], "#2C3E50"),
            border_width=1,
            border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
            text_color=(self.COLORS["text_primary"], "#FFFFFF"),
            command=self._open_add_user_dialog
        )
        self.add_user_btn.pack(fill="x")

    def _create_footer(self) -> None:
        footer = ctk.CTkFrame(
            self.main_card,
            fg_color="transparent"
        )
        footer.pack(side="bottom", pady=20)
        
        ctk.CTkLabel(
            footer,
            text="Developed by Eslam Gamal",
            font=("Helvetica Neue", 10),
            text_color=(self.COLORS["text_secondary"], "#7F8C8D")
        ).pack()
        
        ctk.CTkLabel(
            footer,
            text=f"v{AppConfig.VERSION}",
            font=("Helvetica Neue", 9),
            text_color=(self.COLORS["text_secondary"], "#6C7A7A")
        ).pack(pady=(4, 0))

    def _start_animations(self) -> None:
        """Subtle entrance animation"""
        self.main_card.configure(width=0, height=0)
        self._animate_entrance(0)

    def _animate_entrance(self, step: int) -> None:
        if step > 20:
            return
        
        progress = step / 20
        width = int(460 * progress)
        height = int(620 * progress)
        
        try:
            self.main_card.configure(width=max(1, width), height=max(1, height))
            self.root.after(15, lambda: self._animate_entrance(step + 1))
        except:
            pass

    def _bind_events(self) -> None:
        self.root.bind("<Return>", lambda e: self._handle_login())
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def _toggle_password(self) -> None:
        if self._show_pass:
            self.password_entry.configure(show="●")
            self.toggle_btn.configure(text="👁")
            self._show_pass = False
        else:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="🙈")
            self._show_pass = True

    def _load_saved_credentials(self) -> None:
        try:
            if not os.path.exists(self.local_file):
                return

            with open(self.local_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            last_user = data.get("last_user", "")
            remember = data.get("remember", False)

            if last_user:
                self.username_entry.insert(0, last_user)
            if remember:
                self.remember_check.select()

        except Exception as e:
            print(f"Load credentials error: {e}")


    def _save_credentials(self, username: str, password: str) -> None:
        try:
            remember = getattr(self, "remember_check", None)
            if remember and remember.get() == 1:
                password = password[:72]
                pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                with open(self.local_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "last_user": username,
                        "password_hash": pw_hash,
                        "last_login": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "remember": True
                    }, f, ensure_ascii=False, indent=2)
            else:
                if os.path.exists(self.local_file):
                    os.remove(self.local_file)
        except Exception as e:
            print(f"Save credentials error: {e}")


    def _verify_offline(self, username: str, password: str) -> bool:
        try:
            if not os.path.exists(self.local_file):
                return False
                
            with open(self.local_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if data.get("last_user") != username:
                return False
                
            stored_hash = data.get("password_hash", "")
            password = password[:72]
            return bcrypt.checkpw(
                password.encode("utf-8"),
                stored_hash.encode("utf-8")
            )
        except Exception as e:
            print(f"Offline verify error: {e}")
            return False

    def _show_loading(self, message: str = "جاري التحميل...") -> None:
        """Show premium loading overlay"""
        if self.loading_overlay:
            self.loading_overlay.destroy()
        self.loading_overlay = LoadingOverlay(self.container, message)

    def _hide_loading(self) -> None:
        """Hide loading overlay"""
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    def _update_status(self, text: str, color: Optional[str] = None) -> None:
        def update():
            self.status_label.configure(text=text)
            if color:
                self.status_label.configure(text_color=color)
        self.root.after(0, update)

    def _handle_login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("⚠️ تنبيه", "الرجاء إدخال اسم المستخدم وكلمة المرور.")
            return

        # Disable inputs and show loading
        self.login_btn.configure(state="disabled")
        self.add_user_btn.configure(state="disabled")
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self._show_loading("جاري التحقق من بيانات الدخول...")

        threading.Thread(
            target=self._authenticate,
            args=(username, password),
            daemon=True,
            name="AuthThread"
        ).start()

    def _authenticate(self, username: str, password: str) -> None:
        try:
            # Simulate minimum loading time for UX
            time.sleep(0.8)
            
            if verify_user(username, password):
                self.data_manager.current_user = username
                self.logged_in_user = username  # ← هذا السطر الجديد
                self.app_ref.logged_in_user = username


                self.root.after(0, lambda: self.loading_overlay.update_message("✓ تم التحقق بنجاح"))
                time.sleep(0)
                
                self._save_credentials(username, password)
                self.root.after(0, self._complete_login)
                return

            if self._verify_offline(username, password):
                self.data_manager.current_user = username
                self.logged_in_user = username  # ← هذا السطر الجديد
                self.app_ref.logged_in_user = username
                #print(f"[Login Successful] User: {self.app_ref.logged_in_user}")

                self.root.after(0, lambda: self.loading_overlay.update_message("✓ تم التحقق (وضع Offline)"))
                time.sleep(0.5)
                
                self.root.after(0, self._complete_login)
                return

            # Failed authentication
            self.root.after(0, self._hide_loading)
            self.root.after(0, lambda: messagebox.showerror("❌ خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة!"))
            
        except Exception as e:
            print(f"Auth error: {e}")
            self.root.after(0, self._hide_loading)
            self.root.after(0, lambda: messagebox.showerror("❌ خطأ", str(e)))
            
        finally:
            self.root.after(0, self._re_enable_inputs)

    def _re_enable_inputs(self) -> None:
        """Re-enable all inputs after operation"""
        self.login_btn.configure(state="normal")
        self.add_user_btn.configure(state="normal")
        self.username_entry.configure(state="normal")
        self.password_entry.configure(state="normal")

    def _complete_login(self) -> None:
        self._animation_running = False
        self._hide_loading()
        
        # Success animation
        self.main_card.configure(
            border_color=(self.COLORS["success"], self.COLORS["success"]),
            border_width=2
        )
        
        self.root.after(400, self._fade_out_and_complete)

    def _fade_out_and_complete(self) -> None:
        try:
            self.container.destroy()
        except:
            pass
            
        try:
            self.root.unbind("<Return>")
        except:
            pass
            
        if callable(self.on_success):
            self.on_success()

    def _open_add_user_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("إضافة مستخدم جديد")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")

        self._create_add_user_ui(dialog)

    def _create_add_user_ui(self, dialog: ctk.CTkToplevel) -> None:
        main_frame = ctk.CTkFrame(dialog, fg_color=(self.COLORS["card_light"], self.COLORS["card_dark"]))
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        ctk.CTkLabel(
            main_frame,
            text="إضافة مستخدم جديد",
            font=("Cairo", 24, "bold"),
            text_color=(self.COLORS["primary"], "#FFFFFF")
        ).pack(pady=(10, 20))

        # Entry creator
        def create_entry(label, is_pass=False):
            frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            frame.pack(pady=10, fill="x")
            ctk.CTkLabel(
                frame,
                text=label,
                font=("Cairo", 13),
                text_color=(self.COLORS["text_primary"], "#FFFFFF"),
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            input_frame = ctk.CTkFrame(frame, fg_color="transparent")
            input_frame.pack(fill="x")
            entry = self._create_premium_entry(input_frame, f"أدخل {label}", is_pass)
            entry.pack(side="left", fill="x", expand=True)
            toggle_btn = None
            if is_pass:
                toggle_btn = ctk.CTkButton(
                    input_frame,
                    text="👁",
                    width=40,
                    height=40,
                    corner_radius=10,
                    fg_color="transparent",
                    command=lambda e=entry: e.configure(show="" if e.cget("show") else "●"),
                    font=("Segoe UI", 16)
                )
                toggle_btn.pack(side="left", padx=(8, 0))
            return entry

        admin_entry = create_entry("كلمة مرور المدير", is_pass=True)
        username_entry = create_entry("اسم المستخدم الجديد")
        password_entry = create_entry("كلمة المرور الجديدة", is_pass=True)

        # Role
        ctk.CTkLabel(
            main_frame,
            text="نوع الحساب",
            font=("Cairo", 13),
            text_color=(self.COLORS["text_primary"], "#FFFFFF"),
            anchor="w"
        ).pack(pady=(20, 5), fill="x")

        role_option = ctk.CTkOptionMenu(
            main_frame,
            values=["مستخدم", "مدير"],
            width=200,
            height=45,
            corner_radius=12,
            font=("Cairo", 14),
            fg_color=(self.COLORS["primary"], self.COLORS["primary"]),
            button_color=(self.COLORS["primary_hover"], self.COLORS["primary_hover"]),
            button_hover_color=(self.COLORS["primary_hover"], self.COLORS["primary_hover"])
        )
        role_option.set("مستخدم")
        role_option.pack(fill="x", pady=(0, 30))

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        add_btn = ctk.CTkButton(
            btn_frame,
            text="✅ إضافة المستخدم",
            command=lambda: self._process_add_user(
                admin_entry,
                username_entry,
                password_entry,
                role_option,
                dialog,
                add_btn,
                cancel_btn
            ),
            height=52,
            corner_radius=12,
            font=("Cairo", 15, "bold"),
            fg_color=(self.COLORS["success"], self.COLORS["success"]),
            hover_color=(self.COLORS["success_hover"], self.COLORS["success_hover"])
        )
        add_btn.pack(fill="x", pady=(0, 10))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ إلغاء",
            command=dialog.destroy,
            height=48,
            corner_radius=12,
            font=("Cairo", 14),
            fg_color="transparent",
            hover_color=(self.COLORS["border"], "#2C3E50"),
            border_width=1,
            border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
            text_color=(self.COLORS["text_primary"], "#FFFFFF")
        )
        cancel_btn.pack(fill="x")


    def _process_add_user(
        self,
        admin_entry: ctk.CTkEntry,
        username_entry: ctk.CTkEntry,
        password_entry: ctk.CTkEntry,
        role_option: ctk.CTkOptionMenu,
        dialog: ctk.CTkToplevel,
        add_btn: ctk.CTkButton,
        cancel_btn: ctk.CTkButton
    ) -> None:
        admin_input = admin_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        role = "admin" if role_option.get() == "مدير" else "user"

        if admin_input != self.ADMIN_PASSWORD:
            messagebox.showerror("❌ مرفوض", "كلمة مرور المدير غير صحيحة!")
            return

        if not username or not password:
            messagebox.showwarning("⚠️ تنبيه", "الرجاء إدخال جميع البيانات.")
            return

        # Disable inputs and show loading
        add_btn.configure(state="disabled")
        cancel_btn.configure(state="disabled")
        admin_entry.configure(state="disabled")
        username_entry.configure(state="disabled")
        password_entry.configure(state="disabled")
        role_option.configure(state="disabled")
        
        loading = LoadingOverlay(dialog, "جاري إضافة المستخدم...")

        def process():
            try:
                time.sleep(0.8)  # Simulate processing
                
                if add_user(username, password, role):
                    dialog.after(0, loading.destroy)
                    dialog.after(0, lambda: messagebox.showinfo("✓ نجح", f"تم إضافة المستخدم '{username}' بنجاح!"))
                    dialog.after(100, dialog.destroy)
                else:
                    dialog.after(0, loading.destroy)
                    dialog.after(0, lambda: messagebox.showwarning("⚠️ موجود", f"المستخدم '{username}' موجود مسبقًا."))
                    
            except Exception as e:
                dialog.after(0, loading.destroy)
                dialog.after(0, lambda: messagebox.showerror("❌ خطأ", f"حدث خطأ أثناء الإضافة:\n{e}"))
            
            finally:
                def re_enable():
                    add_btn.configure(state="normal")
                    cancel_btn.configure(state="normal")
                    admin_entry.configure(state="normal")
                    username_entry.configure(state="normal")
                    password_entry.configure(state="normal")
                    role_option.configure(state="normal")
                
                dialog.after(0, re_enable)
        
        threading.Thread(target=process, daemon=True).start()