import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageFilter, ImageEnhance
import threading
import time
import os
import json
import bcrypt
from typing import Callable, Optional
from pathlib import Path

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

        self.footer_label = ctk.CTkLabel(
            self.blur_frame,
            text="CREATED BY ENG ESLAM GAMAL",
            font=("Helvetica Neue", 12,"bold"),
            text_color=("#1276D4", "#D6E7F7")
        )
        self.footer_label.pack(side="bottom", pady=(0,10))


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
    
    def load_data_from_google(self, local_path):
        self.sync_thread = threading.Thread(target=self.sync_manager.download_from_google, args=(local_path,))
        self.sync_thread.start()


    def update_message(self, message):
        self.message_label.configure(text=message)
    
    def destroy(self):
        self.is_active = False
        self.overlay.destroy()


class LoginScreen:

    def _timepoint(self, label: str):
        now = time.time()
        diff = now - self._last_time
        print(f"[⏱ Login] {label}: {diff:.4f}s")
        self._last_time = now


    #ADMIN_PASSWORD = "admin@123"
    
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

    # def __init__(self, root: ctk.CTk, app_ref, on_success_callback: Callable):
    #     self.root = root
    #     self.app_ref = app_ref
    #     self.on_success = on_success_callback
        
    #     self.data_manager = DataManager()
    #     self.local_file = os.path.join(self.data_manager.safe_data_dir, "login.json")
        
    #     self._animation_running = True
    #     self.loading_overlay = None
    #     self._init_ui()
    #     self._init_loading_overlay()   # ← السطر الجديد ده
    #     self.loading_overlay.overlay.place_forget()  # نخفيه من البداية        self._load_saved_credentials()
    #     self._bind_events()
    #     self._start_animations()

    def __init__(self, root: ctk.CTk, app_ref, on_success_callback: Callable):
        # بداية قياس زمن تحميل شاشة تسجيل الدخول
        self._last_time = time.time()
        self._timepoint("Start LoginScreen")

        self.root = root
        self.app_ref = app_ref
        self.on_success = on_success_callback
        self.data_manager = DataManager()
        self.local_file = os.path.join(self.data_manager.safe_data_dir, "login.json")
        self._animation_running = True

        self._timepoint("Init variables")

        self.loading_overlay = None
        self._init_ui()
        self._timepoint("_init_ui done")

        self._init_loading_overlay()   
        self._timepoint("Loading overlay init")

        self.loading_overlay.overlay.place_forget()
        self._load_saved_credentials()
        self._timepoint("Load saved credentials")

        self._bind_events()
        self._timepoint("Bind events")

        self._start_animations()
        self._timepoint("Start entrance animations")

        total = time.time() - self._last_time
        print(f"🟢 LoginScreen finished building in: {total:.4f}s")



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
            text="Code Manager",
            font=("Helvetica Neue", 13),
            text_color=(self.COLORS["text_secondary"], "#95A5A6")
        ).pack()

                
        ctk.CTkLabel(
            header_frame,
            text="CREATED BY ENG ESLAM GAMAL",
            font=("Helvetica Neue", 15, "bold"),
            text_color=("#8F8585", "#ACA2A2")
        ).pack(expand=True, fill="both")
        
        
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
        # self.add_user_btn = ctk.CTkButton(
        #     button_frame,
        #     text="➕  إنشاء مستخدم جديد",
        #     height=46,
        #     corner_radius=12,
        #     font=("Cairo", 14, "bold"),
        #     fg_color="transparent",
        #     hover_color=(self.COLORS["border"], "#2C3E50"),
        #     border_width=1,
        #     border_color=(self.COLORS["border"], self.COLORS["border_dark"]),
        #     text_color=(self.COLORS["text_primary"], "#FFFFFF"),
        #     command=self._open_add_user_dialog
        # )
        # self.add_user_btn.pack(fill="x")

    def _create_footer(self) -> None:
        footer = ctk.CTkFrame(
            self.main_card,
            fg_color="transparent"
        )
        footer.pack(side="bottom",fill="both", expand=True, pady=20)

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
        width = int(450 * progress)
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


    def _save_credentials(self, username: str, password: str, role: str = "user") -> None:
        try:
            remember = self.remember_check.get() == 1
            if not remember:
                if os.path.exists(self.local_file):
                    os.remove(self.local_file)
                return

            # تشفير كلمة المرور (محدودة 72 بايت)
            pw_hash = bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")

            data = {
                "last_user": username,
                "password_hash": pw_hash,
                "role": role,  # حفظ الدور مهم جدًا
                "last_login": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "remember": True
            }

            with open(self.local_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Save credentials error: {e}")
            

    def _verify_offline(self, username: str, password: str):
        """التحقق من login.json (وضع تذكرني) مع إرجاع الدور"""
        try:
            if not os.path.exists(self.local_file):
                return False, None

            with open(self.local_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("last_user") != username:
                return False, None

            stored_hash = data.get("password_hash", "")
            if not stored_hash:
                return False, None

            password_bytes = password.encode("utf-8")[:72]  # bcrypt max 72 bytes
            if bcrypt.checkpw(password_bytes, stored_hash.encode("utf-8")):
                return True, data.get("role", "user")  # أهم سطر: نرجع الدور
            return False, None

        except Exception as e:
            print(f"Offline verify error: {e}")
            return False, None
        
    # def _show_loading(self, message: str = "جاري التحميل...") -> None:
    #     """Show premium loading overlay"""
    #     if self.loading_overlay:
    #         self.loading_overlay.destroy()
    #     self.loading_overlay = LoadingOverlay(self.container, message)


    def _init_loading_overlay(self):
        """ننشئ اللودينج مرة واحدة فقط ونخليه جاهز دايمًا"""
        self.loading_overlay = LoadingOverlay(self.container, "جاري التحميل...")
        self.loading_overlay.overlay.place_forget()  # نخفيه من الأول

    def _show_loading(self, message: str = "جاري التحميل...") -> None:
        """نظهر اللودينج فورًا بدون إعادة بناء"""
        if not hasattr(self, 'loading_overlay') or not self.loading_overlay:
            self._init_loading_overlay()
        
        # نغير الرسالة فقط ونظهره بسرعة البرق
        self.loading_overlay.message_label.configure(text=message)
        self.loading_overlay.dots_count = 0  # نرجّع النقط المتحركة من الصفر
        self.loading_overlay.is_active = True
        self.loading_overlay.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _hide_loading(self) -> None:
        """نخفي اللودينج بدون تدمير"""
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.loading_overlay.is_active = False
            self.loading_overlay.overlay.place_forget()


    # def _hide_loading(self) -> None:
    #     """Hide loading overlay"""
    #     if self.loading_overlay:
    #         self.loading_overlay.destroy()
    #         self.loading_overlay = None

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

        self._show_loading("جاري التحقق من بيانات الدخول...")

        # Disable inputs and show loading
        self.login_btn.configure(state="disabled")
        #self.add_user_btn.configure(state="disabled")
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        #self._show_loading("جاري التحقق من بيانات الدخول...")

        threading.Thread(
                target=self._authenticate,
                args=(username, password),
                daemon=True,
                name="AuthThread"
            ).start()

    def _authenticate(self, username: str, password: str) -> None:
        try:
            time.sleep(0.8)  # تحسين تجربة المستخدم

            # 1. التحقق أونلاين من Google Sheets
            success, role = verify_user(username, password)

            from sync.sync_items_form import SyncManager_form
            base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "EuroTools" / "data"
            self.SYNC_FILE = str(base_dir / "my-tools-sync.json")

            def start_sync_manager(self):

                self.sync_manager = SyncManager_form(creds_path=self.SYNC_FILE)

            # إذا نجح التحقق أونلاين
            if success and role:
                self.app_ref.logged_in_user = username
                self.app_ref.logged_in_role = role
                self.data_manager.current_user = username
                self.root.after(0, lambda: self.loading_overlay.update_message("تم التحقق بنجاح"))
                time.sleep(0.5)
                self._save_credentials(username, password)
                self.root.after(0, self._complete_login)

                
                threading.Thread(target=lambda: start_sync_manager(self), daemon=True).start()


                return

            # 2. إذا فشل الاتصال → جرب الوضع Offline
            offline_success, offline_role = self._verify_offline(username, password)
            if offline_success:
                self.app_ref.logged_in_user = username
                self.app_ref.logged_in_role = offline_role 
                self.data_manager.current_user = username
                #print("nfehsdn65+++46 offf",offline_role)
                self.root.after(0, lambda: self.loading_overlay.update_message("تم التحقق (وضع Offline)"))
                time.sleep(0.5)
                self.root.after(0, self._complete_login)
                return

            # 3. كل حاجة فشلت → رفض الدخول
            self.root.after(0, self._hide_loading)
            self.root.after(0, lambda: messagebox.showerror(
                "خطأ في تسجيل الدخول",
                "اسم المستخدم أو كلمة المرور غير صحيحة!"
            ))

        except Exception as exc:  # احفظ الاستثناء في متغير واضح
            error_msg = str(exc)
            print(f"Auth error: {error_msg}")

            def show_error():
                self._hide_loading()
                messagebox.showerror("خطأ غير متوقع", f"حدث خطأ:\n{error_msg}")

            self.root.after(0, show_error)

        finally:
            self.root.after(0, self._re_enable_inputs)


    def _re_enable_inputs(self) -> None:
        if self.login_btn.winfo_exists():
            self.login_btn.configure(state="normal")
        # نفس الشيء لباقي العناصر
        if self.username_entry.winfo_exists():
            self.username_entry.configure(state="normal")
        if self.password_entry.winfo_exists():
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
