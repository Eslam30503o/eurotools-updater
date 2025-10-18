import gspread
from google.oauth2.service_account import Credentials
import os
import platform
from pathlib import Path
from tkinter import Toplevel, Label
import threading
import time
import requests
from typing import Optional, Dict
import logging


class GoogleSheetsUploader:

    
    # ألوان احترافية للتنبيهات
    COLORS = {
        'success': {'bg': '#10b981', 'fg': '#ffffff'},  # أخضر زمردي
        'error': {'bg': '#ef4444', 'fg': '#ffffff'},    # أحمر قوي
        'warning': {'bg': '#f59e0b', 'fg': '#ffffff'},  # برتقالي ذهبي
        'info': {'bg': '#3b82f6', 'fg': '#ffffff'},     # أزرق سماوي
        'dark': {'bg': '#1f2937', 'fg': '#f9fafb'}      # رمادي داكن
    }
    
    def __init__(self, root, sheet_name: str = "Test"):
        
        
        self.root = root
        self.sheet_name = sheet_name
        self.client: Optional[gspread.Client] = None
        self.sheet: Optional[gspread.Worksheet] = None
        self.is_connected = False
        self.retry_interval = 10  # ثوانٍ بين المحاولات
        
        # إعداد المسارات بشكل آمن
        self._setup_directories()
        
        # إعداد نظام السجلات
        self._setup_logging()
        
        # بدء خيط الاتصال التلقائي
        self._start_connection_thread()
    
    def _setup_directories(self):
        """إنشاء المجلدات اللازمة بشكل آمن"""
        app_name = "EuroTools"
        
        if platform.system() == "Windows":
            base_dir = Path(os.getenv("LOCALAPPDATA", 
                           Path.home() / "AppData" / "Local")) / app_name / "data"
        else:
            base_dir = Path.home() / ".local" / "share" / app_name / "data"
        
        base_dir.mkdir(parents=True, exist_ok=True)
        self.safe_data_dir = base_dir
        self.creds_file = str(base_dir / "credentials.json")
    
    def _setup_logging(self):
        """إعداد نظام تسجيل الأحداث"""
        log_file = self.safe_data_dir / "sheets_uploader.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _start_connection_thread(self):
        """بدء خيط المراقبة والاتصال التلقائي"""
        connection_thread = threading.Thread(
            target=self._auto_reconnect_loop,
            daemon=True,
            name="GoogleSheetsConnection"
        )
        connection_thread.start()
        self.logger.info("🚀 بدء نظام الاتصال التلقائي بـ Google Sheets")
    
    # ═══════════════════════════════════════════════════════════
    # 🌐 فحص الاتصال والإعادة التلقائية
    # ═══════════════════════════════════════════════════════════
    
    def check_internet_connection(self) -> bool:

        
        try:
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _auto_reconnect_loop(self):
        """حلقة إعادة المحاولة التلقائية للاتصال"""
        retry_count = 0
        
        while True:
            if not self.is_connected:
                retry_count += 1
                
                if self.check_internet_connection():
                    try:
                        self._initialize_connection()
                        self.is_connected = True
                        retry_count = 0
                        self.logger.info("✅ تم الاتصال بـ Google Sheets بنجاح")
                        self._show_notification(
                            "✅ متصل بـالانترنت ",
                            "تم الاتصال بنجاح وجاهز للعمل",
                            theme='success'
                        )
                    except Exception as e:
                        self.is_connected = False
                        self.logger.error(f"❌ فشل الاتصال (المحاولة {retry_count}): {e!r}")
                        if retry_count % 6 == 1:  # كل دقيقة
                            self._show_notification(
                                "⚠️ محاولة إعادة الاتصال",
                                f"المحاولة #{retry_count}...",
                                theme='warning'
                            )
                else:
                    self.is_connected = False
                    if retry_count == 1:
                        self._show_notification(
                            "📡 لا يوجد اتصال بالإنترنت",
                            "سيُعاد المحاولة تلقائيًا عند توفر الاتصال",
                            theme='warning'
                        )
            
            time.sleep(self.retry_interval)
    
    def _initialize_connection(self):
        """تهيئة الاتصال بـ Google Sheets"""
        if not os.path.exists(self.creds_file):
            raise FileNotFoundError(
                f"⚠️ ملف الاعتماد غير موجود:\n{self.creds_file}"
            )
        
        # تحميل بيانات الاعتماد
        creds = Credentials.from_service_account_file(
            self.creds_file,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        
        # الاتصال بـ Google Sheets
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(self.sheet_name).sheet1
    
    # ═══════════════════════════════════════════════════════════
    # 📤 رفع وتحديث البيانات
    # ═══════════════════════════════════════════════════════════
    
    def save_to_google_sheet(self, tool_data: Dict[str, str], final_code: str) -> bool:


        if not self.is_connected or not self.sheet:
            self._show_notification(
                "⚠️ غير متصل",
                "لا يوجد اتصال حالي بـ Google Sheets",
                theme='warning'
            )
            self.logger.warning("محاولة الحفظ بدون اتصال نشط")
            return False
        
        try:
            tool_name_en = tool_data.get("name_en", "Unknown")
            tool_name_ar = tool_data.get("name_ar", "غير معروف")
            
            # البحث عن الأداة في القائمة
            existing_names = self.sheet.col_values(2)
            row_to_update = None
            
            try:
                row_to_update = existing_names.index(tool_name_en) + 1
            except ValueError:
                pass  # الأداة غير موجودة
            
            # تحديث أو إضافة
            if row_to_update:
                self.sheet.update(f'C{row_to_update}', [[final_code]])
                self.logger.info(f"📝 تم تحديث: {tool_name_en}")
                self._show_notification(
                    "✅ تم التحديث بنجاح",
                    f"تم تحديث '{tool_name_ar}' في السجل",
                    theme='success'
                )
            else:
                new_row = [
                    tool_name_ar,
                    tool_name_en,
                    final_code,
                    tool_data.get("category", "غير محددة"),
                    tool_data.get("project_name", "")
                ]
                self.sheet.append_row(new_row)
                self.logger.info(f"➕ تمت إضافة: {tool_name_en}")
                self._show_notification(
                    "✅ تمت الإضافة بنجاح",
                    f"تمت إضافة '{tool_name_ar}' كسجل جديد",
                    theme='success'
                )
            
            return True
            
        except gspread.exceptions.APIError as e:
            self.logger.error(f"❌ خطأ في API: {e}")
            self._show_notification(
                "❌ خطأ في الاتصال",
                "فشل التواصل مع Google Sheets API",
                theme='error'
            )
            self.is_connected = False
            return False
            
        except Exception as e:
            self.logger.error(f"❌ خطأ غير متوقع: {e}")
            self._show_notification(
                "❌ فشل الحفظ",
                f"حدث خطأ: {str(e)[:50]}...",
                theme='error'
            )
            return False
    
    # ═══════════════════════════════════════════════════════════
    # 🎨 نظام الإشعارات المحسّن
    # ═══════════════════════════════════════════════════════════
    
    def _show_notification(
        self, 
        title: str, 
        message: str, 
        theme: str = 'dark',
        duration: int = 3500
    ):

        try:
            colors = self.COLORS.get(theme, self.COLORS['dark'])
            
            toast = Toplevel(self.root)
            toast.overrideredirect(True)
            toast.attributes("-topmost", True)
            toast.configure(bg=colors['bg'])
            
            # حساب الموقع (أعلى يمين النافذة)
            x = self.root.winfo_x() + self.root.winfo_width() - 350
            y = self.root.winfo_y() + 20
            toast.geometry(f"320x90+{x}+{y}")
            
            # إطار التصميم
            frame = Label(
                toast,
                bg=colors['bg'],
                padx=20,
                pady=15
            )
            frame.pack(fill='both', expand=True)
            
            # العنوان
            Label(
                frame,
                text=title,
                bg=colors['bg'],
                fg=colors['fg'],
                font=("Segoe UI", 11, "bold"),
                anchor='w'
            ).pack(fill='x')
            
            # الرسالة
            Label(
                frame,
                text=message,
                bg=colors['bg'],
                fg=colors['fg'],
                font=("Segoe UI", 9),
                anchor='w',
                wraplength=280,
                justify='left'
            ).pack(fill='x', pady=(5, 0))
            
            # تأثير الظهور
            toast.attributes("-alpha", 0.0)
            self._fade_in(toast, duration)
            
        except Exception as e:
            self.logger.error(f"فشل عرض الإشعار: {e}")
    
    def _fade_in(self, window, duration):
        """تأثير ظهور تدريجي للإشعار"""
        alpha = 0.0
        
        def animate():
            nonlocal alpha
            alpha += 0.1
            if alpha <= 1.0:
                window.attributes("-alpha", alpha)
                window.after(30, animate)
            else:
                window.after(duration, lambda: self._fade_out(window))
        
        animate()
    
    def _fade_out(self, window):
        """تأثير اختفاء تدريجي للإشعار"""
        alpha = 1.0
        
        def animate():
            nonlocal alpha
            alpha -= 0.1
            if alpha >= 0.0:
                window.attributes("-alpha", alpha)
                window.after(30, animate)
            else:
                window.destroy()
        
        animate()
    
    # ═══════════════════════════════════════════════════════════
    # 🔧 دوال مساعدة
    # ═══════════════════════════════════════════════════════════
    
    def get_connection_status(self) -> Dict[str, any]:


        return {
            'connected': self.is_connected,
            'has_client': self.client is not None,
            'has_sheet': self.sheet is not None,
            'sheet_name': self.sheet_name,
            'creds_file_exists': os.path.exists(self.creds_file)
        }
    
    def force_reconnect(self):
        """إجبار إعادة الاتصال يدوياً"""
        self.logger.info("🔄 إعادة اتصال يدوية...")
        self.is_connected = False
        self.client = None
        self.sheet = None