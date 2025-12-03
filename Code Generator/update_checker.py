import os
import time
import threading
import requests
import tkinter as tk
from tkinter import messagebox

class UpdateChecker:
    def __init__(self, current_version, version_url, download_url, check_interval_hours=24):
        self.current_version = current_version
        self.version_url = version_url
        self.download_url = download_url
        self.check_interval = check_interval_hours * 3600
        self.last_check_file = os.path.join(os.path.expanduser("~"), ".eurotools_update_check")

    def _is_time_to_check(self):
        if not os.path.exists(self.last_check_file):
            return True
        last_check = os.path.getmtime(self.last_check_file)
        return (time.time() - last_check) > self.check_interval

    def _fetch_latest_version(self):
        try:
            response = requests.get(self.version_url, timeout=5)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            print(f"[UpdateChecker] Failed to fetch version: {e}")
            return None

    def _is_newer(self, latest):
        def normalize(v): return [int(x) for x in v.split(".")]
        try:
            return normalize(latest) > normalize(self.current_version)
        except:
            return False

    def _mark_checked(self):
        try:
            with open(self.last_check_file, "w") as f:
                f.write(time.ctime())
        except:
            pass
        
    def _get_latest_release_info(self):
        """يجلب أحدث إصدار من GitHub Releases تلقائيًا."""
        try:
            api_url = "https://api.github.com/repos/Eslam30503o/eurotools-updater/releases/latest"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data = response.json()

            latest_version = data["tag_name"].replace("v", "")
            assets = data.get("assets", [])
            download_url = None

            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe"):  # نجيب رابط ملف exe فقط
                    download_url = asset.get("browser_download_url")
                    break

            return latest_version, download_url
        except Exception as e:
            print(f"[UpdateChecker] Failed to fetch latest release info: {e}")
            return None, None


    def check_for_update(self, silent=False, auto_download=False):
        if not self._is_time_to_check() and silent:
            return

        latest_version, latest_download = self._get_latest_release_info()
        if not latest_version or not latest_download:
            if not silent:
                messagebox.showwarning("تحقق التحديث", "تعذر الاتصال بخادم التحديث.")
            return

        if self._is_newer(latest_version):
            self.download_url = latest_download  # نحدّث رابط التحميل تلقائي
            self._show_update_prompt(latest_version, auto_download)
        elif not silent:
            messagebox.showinfo("تحديث", "البرنامج محدّث إلى آخر إصدار.")
        self._mark_checked()


    def _show_update_prompt(self, latest_version, auto_download=False):
        root = tk.Tk()
        root.withdraw()
        msg = f"يتوفر تحديث جديد ({latest_version}).\nهل ترغب في تحميله الآن؟"
        if messagebox.askyesno("تحديث متوفر", msg):
            self._download_update()
        root.destroy()

    def _download_update(self):
        import tempfile, shutil, subprocess, sys
        import threading
        import tkinter as tk
        from tkinter import ttk, messagebox

        exe_path = sys.argv[0]
        temp_path = os.path.join(tempfile.gettempdir(), "EuroTools_new.exe")

        def run_download():
            try:
                response = requests.get(self.download_url, stream=True)
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(1024 * 64):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = (downloaded / total) * 100 if total else 0
                            progress_var.set(percent)
                            progress_bar.update()

                progress_label.config(text="✅ تم تحميل التحديث بنجاح!")
                time.sleep(0.8)
                messagebox.showinfo("تحديث", "سيتم تثبيت التحديث الآن...")
                
                # إنشاء سكربت التحديث
                updater_script = os.path.join(tempfile.gettempdir(), "apply_update.bat")
                with open(updater_script, "w", encoding="utf-8") as f:
                    f.write(f"""@echo off
                    chcp 65001 >nul
                    echo 🔄 جاري تطبيق التحديث...
                    REM اغلق البرنامج القديم أولاً
                    taskkill /IM "{os.path.basename(exe_path)}" /F >nul 2>&1
                    timeout /t 4 >nul
                    echo 📦 جاري استبدال الملفات...
                    move /Y "{temp_path}" "{exe_path}" >nul
                    if %errorlevel% neq 0 (
                        echo ❌ فشل استبدال الملف!
                        pause
                        exit /b
                    )
                    echo ✅ تم التحديث بنجاح!
                    start "" "{exe_path}"
                    del "%~f0"
                    """)

                subprocess.Popen(
                    ["cmd", "/c", updater_script],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                try:
                    tk._default_root.destroy()
                except:
                    pass
                sys.exit(0)
                


            except Exception as e:
                messagebox.showerror("فشل التحديث", f"حدث خطأ أثناء تحميل التحديث:\n{e}")
                window.destroy()

        # إنشاء نافذة صغيرة لعرض شريط التقدم
        window = tk.Toplevel()
        window.title("تحميل التحديث")
        window.geometry("400x150")
        window.resizable(False, False)

        progress_label = tk.Label(window, text="⬇️ جاري تحميل التحديث...", font=("Arial", 12))
        progress_label.pack(pady=10)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100, length=300)
        progress_bar.pack(pady=10)

        # تحميل في خيط منفصل حتى لا تتجمد الواجهة
        threading.Thread(target=run_download, daemon=True).start()


    def start_auto_check_loop(self):
        def loop():
            while True:
                try:
                    self.check_for_update(silent=True, auto_download=False)
                except Exception as e:
                    print(f"[UpdateChecker] Loop error: {e}")
                time.sleep(self.check_interval)
        t = threading.Thread(target=loop, daemon=True, name="UpdateChecker")
        t.start()
