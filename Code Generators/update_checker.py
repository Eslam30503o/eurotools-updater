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

    def check_for_update(self, silent=False, auto_download=False):
        if not self._is_time_to_check() and silent:
            return
        latest_version = self._fetch_latest_version()
        if latest_version and self._is_newer(latest_version):
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
        import requests, tempfile, shutil, subprocess, sys

        exe_path = sys.argv[0]
        temp_path = os.path.join(tempfile.gettempdir(), "EuroTools_new.exe")

        try:
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            with open(temp_path, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(1024 * 64):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total) * 100 if total else 0
                        print(f"\rتحميل التحديث... {percent:.1f}%", end="")

            print("\n✅ تم تحميل التحديث.")
            messagebox.showinfo("تحديث", "تم تحميل النسخة الجديدة، سيتم تثبيتها الآن...")

            updater_script = os.path.join(tempfile.gettempdir(), "apply_update.bat")
            with open(updater_script, "w") as f:
                f.write(f"""@echo off
timeout /t 2 >nul
move /Y "{temp_path}" "{exe_path}"
start "" "{exe_path}"
del "%~f0"
""")
            subprocess.Popen(["cmd", "/c", updater_script], shell=True)
            sys.exit(0)

        except Exception as e:
            messagebox.showerror("فشل التحديث", f"حدث خطأ أثناء تحميل التحديث: {e}")


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
