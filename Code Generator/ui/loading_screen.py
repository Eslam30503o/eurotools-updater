import customtkinter as ctk
import threading
import time
import requests
import os
from PIL import Image
from typing import Literal, Optional
from config import AppConfig


class LoadingScreen:

    def __init__(self, parent: ctk.CTk):
        self.parent = parent
        self.is_destroyed = False
        self._icon_index = 0
        self._animation_icons = ["⚡", "⭐", "🔷", "💎"]
        
        self._init_container()
        self._init_content()
        self._init_connection_monitor()
        self._start_animations()

    def _init_container(self) -> None:
        self.container = ctk.CTkFrame(
            self.parent,
            fg_color=("#F8F9FA", "#0A0E27"),
            corner_radius=0
        )
        self.container.pack(fill="both", expand=True)

    def _init_content(self) -> None:
        self.content_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

        self._create_logo()
        self._create_title_section()
        self._create_progress_section()

    def _create_logo(self) -> None:
        try:
            logo_path = AppConfig.LOGO_IMAGE
            if os.path.exists(logo_path):
                image = Image.open(logo_path)
                logo = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(140, 140)
                )
                label = ctk.CTkLabel(self.content_frame, image=logo, text="")
            else:
                label = ctk.CTkLabel(
                    self.content_frame,
                    text="🛠️",
                    font=("Segoe UI", 80),
                    text_color=("#3498DB", "#5DADE2")
                )
            label.pack(pady=(0, 10))
        except Exception as e:
            print(f"Logo error: {e}")

    def _create_title_section(self) -> None:
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="EURO TOOLS",
            font=("Segoe UI", 42, "bold"),
            text_color=("#2C3E50", "#ECF0F1")
        )
        self.title_label.pack(pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text="Code Manager Pro",
            font=("Segoe UI", 18),
            text_color=("#5D6D7E", "#ABB2B9")
        )
        self.subtitle_label.pack(pady=(0, 5))

        self.dev_label = ctk.CTkLabel(
            self.content_frame,
            text="Developed by Eslam Gamal",
            font=("Segoe UI", 18, "italic"),
            text_color=("#95A5A6", "#7F8C8D")
        )
        self.dev_label.pack(pady=(0, 30))

    def _create_progress_section(self) -> None:
        self.progress_bar = ctk.CTkProgressBar(
            self.content_frame,
            width=380,
            height=8,
            corner_radius=4,
            progress_color=("#3498DB", "#5DADE2"),
            fg_color=("#E8EEF2", "#1C2833")
        )
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)

        self.percent_label = ctk.CTkLabel(
            self.content_frame,
            text="0%",
            font=("Segoe UI", 13, "bold"),
            text_color=("#7F8C8D", "#95A5A6")
        )
        self.percent_label.pack(pady=(0, 20))

    def _init_connection_monitor(self) -> None:
        self.conn_frame = ctk.CTkFrame(
            self.container,
            fg_color="#1E1E1E",
            height=28,
            corner_radius=0
        )
        self.conn_frame.pack(side="top", fill="x")

        self.conn_label = ctk.CTkLabel(
            self.conn_frame,
            text="🔄 جاري فحص الاتصال...",
            font=("Cairo", 13, "bold"),
            text_color="white"
        )
        self.conn_label.pack(pady=2)

    def _start_animations(self) -> None:
        self._animate_icon()
        threading.Thread(
            target=self._connection_status_loop,
            daemon=True,
            name="ConnectionMonitor"
        ).start()

    def _animate_icon(self) -> None:
        if self.is_destroyed:
            return

        icon = self._animation_icons[self._icon_index % len(self._animation_icons)]
        self.title_label.configure(text=f"EURO TOOLS {icon}")
        self._icon_index += 1
        
        self.parent.after(500, self._animate_icon)

    def _connection_status_loop(self) -> None:
        while not self.is_destroyed:
            status = self._check_internet()
            self.parent.after(0, lambda s=status: self._update_connection_ui(s))
            time.sleep(5)

    def _update_connection_ui(self, status: str) -> None:
        if not hasattr(self, "conn_frame") or not self.conn_frame.winfo_exists():
            return

        try:
            config_map = {
                "ok": ("#1E8449", "🟢 متصل بالإنترنت"),
                "weak": ("#F39C12", "🟠 الاتصال ضعيف"),
                "offline": ("#922B21", "🔴 غير متصل بالإنترنت")
            }
            
            color, text = config_map.get(status, ("#922B21", "🔴 غير متصل بالإنترنت"))
            self.conn_frame.configure(fg_color=color)
            self.conn_label.configure(text=text)
        except:
            pass

    def _check_internet(self, timeout: int = 3) -> Literal["ok", "weak", "offline"]:
        try:
            start = time.time()
            requests.get("https://www.google.com", timeout=timeout)
            ping = time.time() - start
            return "weak" if ping > 1.5 else "ok"
        except:
            return "offline"

    def update_progress(self, value: float, message: str = "") -> None:
        if self.is_destroyed:
            return
        
        self.progress_bar.set(value)
        self.percent_label.configure(text=f"{int(value * 100)}%")
        self.parent.update_idletasks()

    def fade_out(self, steps: int = 10, delay: int = 50) -> None:
        if self.is_destroyed:
            return

        window = self.container.winfo_toplevel()

        def _fade_step(step: int) -> None:
            if step <= 0:
                try:
                    window.attributes("-alpha", 1.0)
                    self.destroy()
                except Exception as e:
                    print(f"Fade-out error: {e}")
                return

            alpha = step / steps
            try:
                light_color = f"#{int(0xF8 * alpha):02x}{int(0xF9 * alpha):02x}{int(0xFA * alpha):02x}"
                dark_color = f"#{int(0x0A * alpha):02x}{int(0x0E * alpha):02x}{int(0x27 * alpha):02x}"
                self.container.configure(fg_color=(light_color, dark_color))
            except:
                pass

            self.container.after(delay, lambda: _fade_step(step - 1))

        _fade_step(steps)

    def destroy(self) -> None:
        self.is_destroyed = True
        try:
            self.container.destroy()
        except:
            pass