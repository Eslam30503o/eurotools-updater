import customtkinter as ctk
import threading
import sys
import time
from tkinter import messagebox
from typing import Optional, Callable
from dataclasses import dataclass

from config import AppConfig
from data_manager import DataManager
from sync.manager import SyncManager
from ui_manager import UIManager
from ui.loading_screen import LoadingScreen
from ui.login_screen import LoginScreen
from sync.history_manager import HistoryManager
from ui.edit_tool import EditToolMixin
from update_checker import UpdateChecker

import warnings
warnings.filterwarnings("ignore")


@dataclass
class AppState:
    is_initializing: bool = True
    is_authenticated: bool = False
    is_syncing: bool = False
    sync_ready: bool = False


class EuroToolsApp:

    def __init__(self):
        self._state = AppState()
        self._init_lock = threading.Lock()
        
        self._setup_ctk_settings()
        self.root = ctk.CTk()
        self._configure_window()

        self.history = HistoryManager()




        self.data_manager: Optional[DataManager] = None
        self.ui_manager: Optional[UIManager] = None
        self.sync_manager: Optional[SyncManager] = None
        self.loading_screen: Optional[LoadingScreen] = None
        self.login_screen: Optional[LoginScreen] = None

        self.logged_in_user = None  # في البداية، قبل تسجيل الدخول
        self._init_login_screen()
        self._apply_window_effects()
        self._start_ui_monitor()


    def _setup_ctk_settings(self) -> None:
        try:
            ctk.set_appearance_mode(AppConfig.APPEARANCE_MODE)
            ctk.set_default_color_theme(AppConfig.COLOR_THEME)
        except Exception as e:
            self._log_error("CTK Setup", e)

    def _configure_window(self) -> None:
        try:
            splash_w, splash_h = AppConfig.SPLASH_SIZE
            self.root.geometry(f"{splash_w}x{splash_h}")
            
            min_w, min_h = AppConfig.MIN_WINDOW_SIZE
            self.root.minsize(min_w, min_h)
            
            self.root.title(f"{AppConfig.APP_NAME} v{AppConfig.VERSION}")
            self.root.resizable(False, False)
            
            self._center_window()
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        except Exception as e:
            self._log_error("Window Configuration", e)
            raise

    def _center_window(self) -> None:
        try:
            self.root.update_idletasks()
            w, h = self.root.winfo_width(), self.root.winfo_height()
            x = (self.root.winfo_screenwidth() - w) // 2
            y = (self.root.winfo_screenheight() - h) // 2
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        except:
            pass

    def _init_login_screen(self) -> None:
        self.login_screen = LoginScreen(
            self.root,
            app_ref=self,
            on_success_callback=self._handle_login_success
        )

    def _apply_window_effects(self) -> None:
        self.root.attributes('-alpha', 0.0)
        self.root.after(AppConfig.LOADING_DELAY, lambda: self._fade_in(0.0))

    def _fade_in(self, alpha: float = 0.0) -> None:
        if alpha < 1.0:
            alpha = min(alpha + 0.1, 1.0)
            self.root.attributes('-alpha', alpha)
            self.root.after(30, lambda: self._fade_in(alpha))

    def _handle_login_success(self) -> None:
        #print(f"✅ Logged in as: {self.logged_in_user}")

        # 🧠 نشر اسم المستخدم في باقي أجزاء النظام
        HistoryManager.logged_in_user = self.logged_in_user
        SyncManager.logged_in_user = self.logged_in_user

        try:
            EditToolMixin.logged_in_user = self.logged_in_user
        except ImportError:
            pass

        self.root.after(0, self._start_app_initialization)

    def _start_app_initialization(self) -> None:
        #print(f"✅ Logged in as: {self.logged_in_user}")

        with self._init_lock:
            self._state.is_authenticated = True
            
            self._cleanup_login_screen()
            self.root.attributes('-alpha', 1.0)
            
            self._show_loading_screen()
            self.root.after(2000, self._begin_resize_animation)

    def _cleanup_login_screen(self) -> None:
        try:
            if self.login_screen:
                self.login_screen = None
        except:
            pass

    def _show_loading_screen(self) -> None:
        try:
            self.loading_screen = LoadingScreen(self.root)
            self.root.update_idletasks()
        except Exception as e:
            self._log_error("Loading Screen", e)
            self.loading_screen = None

    def _begin_resize_animation(self, step: int = 0) -> None:
        if step == 0:
            self._hide_loading_screen()

        max_steps = 20
        if step >= max_steps:
            self._finalize_ui()
            return

        try:
            progress = step / max_steps
            start_w, start_h = AppConfig.SPLASH_SIZE
            target_w, target_h = AppConfig.WINDOW_SIZE

            current_w = int(start_w + (target_w - start_w) * progress)
            current_h = int(start_h + (target_h - start_h) * progress)

            self.root.geometry(f"{current_w}x{current_h}")
            self._center_window()

            self.root.after(AppConfig.ANIMATION_SPEED, lambda: self._begin_resize_animation(step + 1))
        except Exception as e:
            self._log_error("Animation", e)
            self._finalize_ui()

    def _hide_loading_screen(self) -> None:
        try:
            if self.loading_screen:
                self.loading_screen.container.pack_forget()
        except:
            pass

    def _finalize_ui(self) -> None:
        try:
            self.root.resizable(True, True)
            
            self._ensure_data_manager()
            self._ensure_history_manager()

            self._start_sync_manager_initialization() 
            self._wait_for_sync_manager()
            self._setup_update_checker()

        except Exception as e:
            self._log_error("UI Finalization", e)
            self._show_error_and_exit("خطأ نهائي", str(e))

    def _ensure_data_manager(self) -> None:
        if self.data_manager is None:
            try:
                self.data_manager = DataManager()
            except Exception as e:
                self._show_error_and_exit("خطأ في البيانات", f"فشل تهيئة البيانات: {e}")
                raise

    def _wait_for_sync_manager(self, timeout: float = 5.0) -> None:
        start_time = time.time()

        def check_sync() -> None:
            elapsed = time.time() - start_time
            
            if self.sync_manager is not None or elapsed >= timeout:
                self._initialize_ui_manager()
            else:
                self.root.after(100, check_sync)

        check_sync()

    def _initialize_ui_manager(self) -> None:
        try:
            self.ui_manager = UIManager(self.root, self.data_manager, self.sync_manager,
    history_manager=self.history_manager)
            
            if self.sync_manager:
                self.ui_manager.enable_manual_sync_button() # دالة جديدة تضيفها في UIManager
                self._configure_sync_manager()
            
            self.root.after(1500, self._close_loading_screen)
            
        except Exception as e:
            self._log_error("UI Manager", e)
            self._show_error_and_exit("خطأ في الواجهة", str(e))

    def _configure_sync_manager(self) -> None:
        try:
            self.sync_manager.ui_ref = self.ui_manager
            self.sync_manager.start_auto_sync()
            self._state.sync_ready = True
        except Exception as e:
            self._log_error("Sync Manager", e)

    def _close_loading_screen(self) -> None:
        try:
            if self.loading_screen:
                self.loading_screen.fade_out()
                self.loading_screen = None
        except Exception as e:
            self._log_error("Loading Screen Close", e)

    def _show_error_and_exit(self, title: str, message: str) -> None:
        try:
            messagebox.showerror(title, message)
        except:
            print(f"ERROR: {title} - {message}")
        self.root.quit()

    def _on_closing(self) -> None:
        try:
            if self.sync_manager:
                self._perform_final_sync()
        except Exception as e:
            self._log_error("Cleanup", e)
        finally:
            try:
                self.root.destroy()
            except:
                pass

    def _perform_final_sync(self) -> None:
        try:
            self.sync_manager.stop_auto_sync()
            setattr(self.sync_manager, "shutting_down", True)

            def bg_sync() -> None:
                try:
                    with self.sync_manager.sync_lock:
                        self.sync_manager.sync_all()
                except Exception as e:
                    self._log_error("Final Sync", e)

            threading.Thread(target=bg_sync, daemon=True, name="FinalSync").start()
        except:
            pass

    def _start_ui_monitor(self) -> None:
        last_tick = time.time()

        def monitor_thread() -> None:
            nonlocal last_tick
            while True:
                current = time.time()
                delta = current - last_tick
                if delta > 0.4:
                    print(f"⚠️ UI Freeze: {delta:.2f}s")
                last_tick = current
                time.sleep(0.1)

        def update_tick() -> None:
            nonlocal last_tick
            last_tick = time.time()
            self.root.after(100, update_tick)

        threading.Thread(target=monitor_thread, daemon=True, name="UIMonitor").start()
        update_tick()

    @staticmethod
    def _log_error(context: str, error: Exception) -> None:
        print(f"[{context}] Error: {error}")

    def run(self) -> None:
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application interrupted")
        except Exception as e:
            self._log_error("Main Loop", e)
            raise
    def _start_sync_manager_initialization(self) -> None:
        def initialize_sync_manager():
            try:
                from sync.manager import SyncManager
                # ⭐️ لاحظ أن SyncManager يحتاج إلى DataManager تم تهيئته مسبقًا
                self.sync_manager = SyncManager(ui_ref=self.ui_manager) 

                # إرسال إشارة إلى مؤشر ترابط الواجهة بأن SyncManager جاهز
                self.root.after(0, self._handle_sync_manager_ready) 

            except Exception as e:
                self._log_error("SyncManager Init Thread", e)
                self.root.after(0, lambda: self._show_error_and_exit(
                    "خطأ في التهيئة", 
                    f"فشل تهيئة مدير المزامنة (SyncManager): {e}"
                ))

        threading.Thread(target=initialize_sync_manager, daemon=True, name="SyncInit").start()

    def _handle_sync_manager_ready(self) -> None:
        # يمكنك هنا إضافة تحديثات أخرى للواجهة إذا لزم الأمر
        #print("✅ SyncManager جاهز للاستخدام.")
        # ربط UI Manager بـ Sync Manager بمجرد أن يصبح جاهزاً
        if self.ui_manager and self.sync_manager:
            self.ui_manager.sync_manager = self.sync_manager
            self.sync_manager.ui = self.ui_manager # تحديث الـ ui ref إذا كانت غير موجودة
            self.sync_manager.start_auto_sync() # البدء بالتزامن التلقائي

    def _ensure_history_manager(self) -> None:
        try:
            self.history_manager = HistoryManager(
                creds_path=self.data_manager.SYNC_FILE,
                sheet_name="My Tools Sync"
            )
        except Exception as e:
            self._log_error("HistoryManager", e)
            self.history_manager = None
            
    def _setup_update_checker(self):
        try:
            self.updater = UpdateChecker(
                current_version=AppConfig.VERSION,
                version_url=AppConfig.VERSION_URL,
                download_url=AppConfig.DOWNLOAD_URL,
                check_interval_hours=AppConfig.UPDATE_CHECK_INTERVAL_HOURS
            )
            self.updater.check_for_update(silent=True, auto_download=False)
            self.updater.start_auto_check_loop()
        except Exception as e:
            print(f"[UpdateChecker] Error: {e}")


        

def main() -> int:
    try:
        app = EuroToolsApp()
        app.run()
        return 0
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        try:
            messagebox.showerror("خطأ فادح", str(e))
        except:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())

    
