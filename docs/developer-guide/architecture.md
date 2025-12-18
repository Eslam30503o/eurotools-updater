# 🏗️ بنية المشروع - دليل شامل

دليل مفصل لبنية Euro Tools Code Manager وتصميمه المعماري.

## 🎯 نظرة عامة على البنية

Euro Tools Code Manager مبني على بنية معيارية قابلة للتوسع تتبع مبادئ التصميم الحديثة.

## 📐 البنية العامة

### نمط MVC (Model-View-Controller)

```
┌─────────────────────────────────────────────────────────────┐
│                    Euro Tools Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    View     │◄──►│ Controller  │◄──►│    Model    │     │
│  │             │    │             │    │             │     │
│  │ UI Manager  │    │ App Logic   │    │ Data Manager│     │
│  │ Components  │    │ Handlers    │    │ Database    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Widgets   │    │  Services   │    │   Storage   │     │
│  │  Dialogs    │    │ Validators  │    │    Sync     │     │
│  │  Screens    │    │ Utilities   │    │   Backup    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### الطبقات الأساسية

#### 1. طبقة العرض (Presentation Layer)
```python
# ui/ - واجهة المستخدم
├── ui_manager.py          # مدير الواجهة الرئيسي
├── login_screen.py        # شاشة تسجيل الدخول
├── products_ui.py         # واجهة إدارة المنتجات
├── lists_ui.py            # واجهة إدارة القوائم
├── new_tool.py            # نموذج إضافة أداة
├── edit_tool.py           # نموذج تحرير الأدوات
├── export_excel.py        # واجهة التصدير
├── printer.py             # نظام الطباعة
├── settings_ui.py         # واجهة الإعدادات
└── history_screen.py      # شاشة السجل
```

#### 2. طبقة المنطق (Business Logic Layer)
```python
# Core Business Logic
├── app.py                 # التطبيق الرئيسي
├── data_manager.py        # منطق إدارة البيانات
├── categories.py          # منطق التصنيفات
├── google_users.py        # إدارة المستخدمين
├── performance_optimizer.py # تحسين الأداء
└── update_checker.py      # فحص التحديثات
```

#### 3. طبقة البيانات (Data Layer)
```python
# sync/ - طبقة المزامنة والبيانات
├── manager.py             # مدير المزامنة الرئيسي
├── google_init.py         # تهيئة Google Sheets
├── history_manager.py     # إدارة السجل
├── lock_manager.py        # إدارة الأقفال
├── sync_products.py       # مزامنة المنتجات
├── sync_lists.py          # مزامنة القوائم
└── utils.py               # أدوات مساعدة
```

## 🔧 المكونات الأساسية

### 1. مدير البيانات (Data Manager)

#### الهيكل والمسؤوليات
```python
class DataManager:
    """
    مدير البيانات الرئيسي - يتولى جميع عمليات البيانات
    
    المسؤوليات:
    - تحميل وحفظ البيانات
    - التحقق من صحة البيانات
    - إدارة النسخ الاحتياطية
    - تحسين الأداء
    """
    
    def __init__(self):
        self.tools_file = "data/tools.json"
        self.lists_file = "data/lists.json"
        self.users_file = "data/users.json"
        self.cache = {}
        
    # العمليات الأساسية
    def load_tools(self) -> List[Dict]
    def save_tools(self, tools: List[Dict]) -> bool
    def add_tool(self, tool: Dict) -> str
    def update_tool(self, tool_id: str, updates: Dict) -> bool
    def delete_tool(self, tool_id: str) -> bool
    
    # عمليات البحث والفلترة
    def search_tools(self, query: str, filters: Dict) -> List[Dict]
    def filter_by_category(self, category: str) -> List[Dict]
    def get_tools_by_status(self, status: str) -> List[Dict]
    
    # إدارة الأداء
    def optimize_data(self) -> None
    def clear_cache(self) -> None
    def get_statistics(self) -> Dict
```

#### تدفق البيانات
```
📊 تدفق البيانات في DataManager:

1. التحميل (Loading):
   File System → JSON Parser → Validation → Cache → Application

2. الحفظ (Saving):
   Application → Validation → JSON Serializer → Backup → File System

3. المزامنة (Sync):
   Local Data ↔ Sync Manager ↔ Google Sheets ↔ Cloud Storage
```

### 2. مدير الواجهة (UI Manager)

#### البنية الهرمية
```python
class UIManager:
    """
    مدير الواجهة الرئيسي - ينسق جميع عناصر الواجهة
    
    المسؤوليات:
    - إدارة النوافذ والحوارات
    - تنسيق الأحداث
    - إدارة المظاهر والثيمات
    - التحكم في التنقل
    """
    
    def __init__(self, root):
        self.root = root
        self.current_screen = None
        self.theme_manager = ThemeManager()
        self.event_dispatcher = EventDispatcher()
        
    # إدارة الشاشات
    def show_screen(self, screen_name: str, **kwargs) -> None
    def hide_screen(self, screen_name: str) -> None
    def switch_screen(self, from_screen: str, to_screen: str) -> None
    
    # إدارة الأحداث
    def bind_event(self, event: str, handler: Callable) -> None
    def trigger_event(self, event: str, data: Dict) -> None
    
    # إدارة المظهر
    def set_theme(self, theme_name: str) -> None
    def update_colors(self, color_scheme: Dict) -> None
```

#### نمط الأحداث (Event Pattern)
```python
# نظام الأحداث المركزي
class EventDispatcher:
    """
    موزع الأحداث - يدير التواصل بين المكونات
    """
    
    events = {
        'tool_added': [],
        'tool_updated': [],
        'tool_deleted': [],
        'list_created': [],
        'sync_started': [],
        'sync_completed': [],
        'user_login': [],
        'user_logout': []
    }
    
    @staticmethod
    def subscribe(event: str, callback: Callable):
        """اشتراك في حدث معين"""
        if event in EventDispatcher.events:
            EventDispatcher.events[event].append(callback)
    
    @staticmethod
    def publish(event: str, data: Dict = None):
        """نشر حدث لجميع المشتركين"""
        if event in EventDispatcher.events:
            for callback in EventDispatcher.events[event]:
                callback(data)
```

### 3. مدير المزامنة (Sync Manager)

#### البنية المعيارية
```python
class SyncManager:
    """
    مدير المزامنة - يتولى جميع عمليات المزامنة السحابية
    
    المسؤوليات:
    - المزامنة مع Google Sheets
    - إدارة التعارضات
    - المزامنة التلقائية
    - إدارة الأقفال
    """
    
    def __init__(self):
        self.google_client = GoogleSheetsClient()
        self.lock_manager = LockManager()
        self.history_manager = HistoryManager()
        self.conflict_resolver = ConflictResolver()
        
    # عمليات المزامنة الأساسية
    async def sync_tools(self) -> SyncResult
    async def sync_lists(self) -> SyncResult
    async def sync_users(self) -> SyncResult
    
    # إدارة التعارضات
    def detect_conflicts(self, local_data, remote_data) -> List[Conflict]
    def resolve_conflict(self, conflict: Conflict, resolution: str) -> bool
    
    # المزامنة التلقائية
    def start_auto_sync(self, interval: int) -> None
    def stop_auto_sync(self) -> None
```

#### استراتيجيات المزامنة
```python
# استراتيجيات مختلفة للمزامنة
class SyncStrategy:
    """استراتيجية المزامنة الأساسية"""
    
    def sync(self, local_data, remote_data):
        raise NotImplementedError

class LastWriteWinsStrategy(SyncStrategy):
    """آخر كتابة تفوز"""
    
    def sync(self, local_data, remote_data):
        if local_data.timestamp > remote_data.timestamp:
            return local_data
        return remote_data

class MergeStrategy(SyncStrategy):
    """دمج التغييرات"""
    
    def sync(self, local_data, remote_data):
        merged = {}
        # منطق الدمج المعقد
        return merged

class ManualResolveStrategy(SyncStrategy):
    """حل يدوي للتعارضات"""
    
    def sync(self, local_data, remote_data):
        # عرض واجهة للمستخدم لحل التعارض
        return self.show_conflict_dialog(local_data, remote_data)
```

## 🔄 أنماط التصميم المستخدمة

### 1. نمط Singleton

#### تطبيق في مدير الإعدادات
```python
class ConfigManager:
    """
    مدير الإعدادات - نمط Singleton
    يضمن وجود نسخة واحدة فقط من الإعدادات
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self.load_config()
    
    def get(self, key: str, default=None):
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        self._config[key] = value
        self.save_config()
    
    def load_config(self) -> Dict:
        """تحميل الإعدادات من الملف"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def save_config(self) -> None:
        """حفظ الإعدادات في الملف"""
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)
```

### 2. نمط Observer

#### تطبيق في نظام الإشعارات
```python
class NotificationCenter:
    """
    مركز الإشعارات - نمط Observer
    يدير الإشعارات والتنبيهات في التطبيق
    """
    
    def __init__(self):
        self.observers = {}
    
    def subscribe(self, event_type: str, observer: Callable):
        """اشتراك في نوع إشعار معين"""
        if event_type not in self.observers:
            self.observers[event_type] = []
        self.observers[event_type].append(observer)
    
    def unsubscribe(self, event_type: str, observer: Callable):
        """إلغاء الاشتراك"""
        if event_type in self.observers:
            self.observers[event_type].remove(observer)
    
    def notify(self, event_type: str, data: Dict):
        """إرسال إشعار لجميع المشتركين"""
        if event_type in self.observers:
            for observer in self.observers[event_type]:
                observer(data)

# مثال على الاستخدام
notification_center = NotificationCenter()

def on_tool_added(data):
    print(f"تم إضافة أداة جديدة: {data['tool_name']}")

def on_sync_completed(data):
    print(f"تمت المزامنة بنجاح: {data['items_synced']} عنصر")

# الاشتراك في الأحداث
notification_center.subscribe('tool_added', on_tool_added)
notification_center.subscribe('sync_completed', on_sync_completed)
```

### 3. نمط Factory

#### تطبيق في إنشاء الواجهات
```python
class UIComponentFactory:
    """
    مصنع مكونات الواجهة - نمط Factory
    ينشئ مكونات الواجهة حسب النوع المطلوب
    """
    
    @staticmethod
    def create_dialog(dialog_type: str, parent, **kwargs):
        """إنشاء حوار حسب النوع"""
        
        if dialog_type == 'add_tool':
            return AddToolDialog(parent, **kwargs)
        elif dialog_type == 'edit_tool':
            return EditToolDialog(parent, **kwargs)
        elif dialog_type == 'confirm':
            return ConfirmDialog(parent, **kwargs)
        elif dialog_type == 'error':
            return ErrorDialog(parent, **kwargs)
        elif dialog_type == 'progress':
            return ProgressDialog(parent, **kwargs)
        else:
            raise ValueError(f"نوع الحوار غير مدعوم: {dialog_type}")
    
    @staticmethod
    def create_screen(screen_type: str, parent, **kwargs):
        """إنشاء شاشة حسب النوع"""
        
        screens = {
            'login': LoginScreen,
            'main': MainScreen,
            'tools': ToolsScreen,
            'lists': ListsScreen,
            'settings': SettingsScreen,
            'reports': ReportsScreen
        }
        
        if screen_type in screens:
            return screens[screen_type](parent, **kwargs)
        else:
            raise ValueError(f"نوع الشاشة غير مدعوم: {screen_type}")
```

### 4. نمط Command

#### تطبيق في نظام التراجع والإعادة
```python
class Command:
    """الأمر الأساسي"""
    
    def execute(self):
        raise NotImplementedError
    
    def undo(self):
        raise NotImplementedError

class AddToolCommand(Command):
    """أمر إضافة أداة"""
    
    def __init__(self, data_manager, tool_data):
        self.data_manager = data_manager
        self.tool_data = tool_data
        self.tool_id = None
    
    def execute(self):
        self.tool_id = self.data_manager.add_tool(self.tool_data)
        return self.tool_id
    
    def undo(self):
        if self.tool_id:
            self.data_manager.delete_tool(self.tool_id)

class UpdateToolCommand(Command):
    """أمر تحديث أداة"""
    
    def __init__(self, data_manager, tool_id, new_data):
        self.data_manager = data_manager
        self.tool_id = tool_id
        self.new_data = new_data
        self.old_data = None
    
    def execute(self):
        self.old_data = self.data_manager.get_tool(self.tool_id)
        self.data_manager.update_tool(self.tool_id, self.new_data)
    
    def undo(self):
        if self.old_data:
            self.data_manager.update_tool(self.tool_id, self.old_data)

class CommandManager:
    """مدير الأوامر - يدير التراجع والإعادة"""
    
    def __init__(self):
        self.history = []
        self.current_index = -1
    
    def execute_command(self, command: Command):
        """تنفيذ أمر وإضافته للسجل"""
        result = command.execute()
        
        # إزالة الأوامر بعد النقطة الحالية
        self.history = self.history[:self.current_index + 1]
        
        # إضافة الأمر الجديد
        self.history.append(command)
        self.current_index += 1
        
        return result
    
    def undo(self):
        """التراجع عن آخر أمر"""
        if self.can_undo():
            command = self.history[self.current_index]
            command.undo()
            self.current_index -= 1
    
    def redo(self):
        """إعادة تنفيذ الأمر"""
        if self.can_redo():
            self.current_index += 1
            command = self.history[self.current_index]
            command.execute()
    
    def can_undo(self) -> bool:
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        return self.current_index < len(self.history) - 1
```

## 📊 إدارة البيانات والتخزين

### هيكل البيانات

#### ملفات البيانات الأساسية
```json
// tools.json - بيانات الأدوات
{
  "tools": [
    {
      "id": "CT-0001",
      "name": "مثقاب كهربائي 18V",
      "description": "مثقاب كهربائي قوي مع بطارية ليثيوم",
      "category": "أدوات القطع",
      "subcategory": "مثاقب",
      "quantity": 5,
      "unit": "قطعة",
      "price": 450.00,
      "location": "المخزن الرئيسي - رف A3",
      "status": "متاح",
      "purchase_date": "2024-01-15",
      "warranty_period": "سنتان",
      "supplier": "شركة الأدوات المتقدمة",
      "model_number": "DRL-18V-PRO",
      "serial_number": "SN123456789",
      "notes": "يحتاج صيانة دورية كل 6 أشهر",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-12-18T14:25:00Z",
      "created_by": "admin",
      "updated_by": "ahmed"
    }
  ],
  "metadata": {
    "version": "4.5.0",
    "last_backup": "2024-12-18T12:00:00Z",
    "total_tools": 1247,
    "last_sync": "2024-12-18T14:27:00Z"
  }
}
```

```json
// lists.json - قوائم المشاريع
{
  "lists": [
    {
      "id": "LIST-001",
      "name": "صيانة خط الإنتاج A",
      "description": "صيانة شاملة لخط الإنتاج الرئيسي",
      "type": "صيانة",
      "status": "نشط",
      "priority": "عالية",
      "start_date": "2024-12-20",
      "end_date": "2024-12-25",
      "manager": "أحمد محمد",
      "team": ["سارة أحمد", "محمد علي"],
      "supervisor": "مهندس خالد",
      "budget": 15000.00,
      "location": "المصنع الرئيسي - خط A",
      "tools": [
        {
          "tool_id": "CT-0001",
          "quantity_needed": 2,
          "assigned_to": "أحمد محمد",
          "start_date": "2024-12-20",
          "duration_days": 3,
          "status": "محجوز",
          "notes": "للاستخدام في صيانة المحركات"
        }
      ],
      "progress": 80,
      "created_at": "2024-12-15T09:00:00Z",
      "updated_at": "2024-12-18T14:30:00Z"
    }
  ]
}
```

### نظام النسخ الاحتياطية

#### استراتيجية النسخ الاحتياطية
```python
class BackupManager:
    """
    مدير النسخ الاحتياطية - يدير جميع عمليات النسخ الاحتياطي
    """
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # أنواع النسخ الاحتياطية
        self.backup_types = {
            'daily': {'retention': 7, 'schedule': '23:59'},
            'weekly': {'retention': 4, 'schedule': 'sunday 23:59'},
            'monthly': {'retention': 12, 'schedule': 'last_day 23:59'}
        }
    
    def create_backup(self, backup_type: str = 'manual') -> str:
        """إنشاء نسخة احتياطية"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{backup_type}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # إنشاء مجلد النسخة الاحتياطية
        backup_path.mkdir(exist_ok=True)
        
        # نسخ ملفات البيانات
        data_files = [
            'tools.json',
            'lists.json', 
            'users.json',
            'settings.json'
        ]
        
        for file_name in data_files:
            source = Path(file_name)
            if source.exists():
                destination = backup_path / file_name
                shutil.copy2(source, destination)
        
        # ضغط النسخة الاحتياطية
        archive_path = f"{backup_path}.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(backup_path))
        
        # حذف المجلد المؤقت
        shutil.rmtree(backup_path)
        
        # تنظيف النسخ القديمة
        self.cleanup_old_backups(backup_type)
        
        return archive_path
    
    def restore_backup(self, backup_path: str) -> bool:
        """استعادة نسخة احتياطية"""
        
        try:
            # إنشاء نسخة احتياطية من البيانات الحالية
            current_backup = self.create_backup('pre_restore')
            
            # استخراج النسخة الاحتياطية
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall('temp_restore')
            
            # نسخ الملفات المستعادة
            restore_dir = Path('temp_restore')
            for file_path in restore_dir.rglob('*.json'):
                destination = Path(file_path.name)
                shutil.copy2(file_path, destination)
            
            # تنظيف الملفات المؤقتة
            shutil.rmtree(restore_dir)
            
            return True
            
        except Exception as e:
            print(f"خطأ في استعادة النسخة الاحتياطية: {e}")
            return False
    
    def cleanup_old_backups(self, backup_type: str) -> None:
        """تنظيف النسخ الاحتياطية القديمة"""
        
        if backup_type not in self.backup_types:
            return
        
        retention = self.backup_types[backup_type]['retention']
        pattern = f"{backup_type}_*.zip"
        
        # العثور على جميع النسخ من هذا النوع
        backups = list(self.backup_dir.glob(pattern))
        
        # ترتيب حسب تاريخ الإنشاء
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # حذف النسخ الزائدة
        for backup in backups[retention:]:
            backup.unlink()
```

## 🔐 الأمان والحماية

### تشفير البيانات

#### نظام التشفير
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class SecurityManager:
    """
    مدير الأمان - يتولى تشفير وحماية البيانات الحساسة
    """
    
    def __init__(self):
        self.key_file = "security.key"
        self.salt_file = "security.salt"
        self._key = None
        self._fernet = None
    
    def generate_key(self, password: str) -> None:
        """توليد مفتاح التشفير من كلمة المرور"""
        
        # توليد أو تحميل الملح
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        
        # توليد المفتاح
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self._key = key
        self._fernet = Fernet(key)
        
        # حفظ المفتاح (مشفر)
        with open(self.key_file, 'wb') as f:
            f.write(key)
    
    def encrypt_data(self, data: str) -> str:
        """تشفير البيانات"""
        if not self._fernet:
            raise ValueError("لم يتم تهيئة نظام التشفير")
        
        encrypted = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """فك تشفير البيانات"""
        if not self._fernet:
            raise ValueError("لم يتم تهيئة نظام التشفير")
        
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self._fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def encrypt_file(self, file_path: str) -> None:
        """تشفير ملف كامل"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self._fernet.encrypt(data)
        
        with open(f"{file_path}.encrypted", 'wb') as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str) -> None:
        """فك تشفير ملف"""
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self._fernet.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
```

### إدارة المستخدمين والصلاحيات

#### نظام الأدوار
```python
from enum import Enum
from passlib.hash import bcrypt

class UserRole(Enum):
    """أدوار المستخدمين"""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"

class Permission(Enum):
    """الصلاحيات المتاحة"""
    READ_TOOLS = "read_tools"
    WRITE_TOOLS = "write_tools"
    DELETE_TOOLS = "delete_tools"
    READ_LISTS = "read_lists"
    WRITE_LISTS = "write_lists"
    DELETE_LISTS = "delete_lists"
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    EXPORT_DATA = "export_data"
    SYNC_DATA = "sync_data"

class UserManager:
    """
    مدير المستخدمين - يدير المصادقة والتخويل
    """
    
    # تعريف صلاحيات كل دور
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [p for p in Permission],  # جميع الصلاحيات
        UserRole.EDITOR: [
            Permission.READ_TOOLS, Permission.WRITE_TOOLS,
            Permission.READ_LISTS, Permission.WRITE_LISTS,
            Permission.EXPORT_DATA, Permission.SYNC_DATA
        ],
        UserRole.VIEWER: [
            Permission.READ_TOOLS, Permission.READ_LISTS,
            Permission.EXPORT_DATA
        ],
        UserRole.GUEST: [
            Permission.READ_TOOLS, Permission.READ_LISTS
        ]
    }
    
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.security_manager = SecurityManager()
    
    def create_user(self, username: str, password: str, email: str, 
                   role: UserRole) -> bool:
        """إنشاء مستخدم جديد"""
        
        users = self.load_users()
        
        # التحقق من عدم وجود المستخدم
        if any(user['username'] == username for user in users):
            return False
        
        # تشفير كلمة المرور
        hashed_password = bcrypt.hash(password)
        
        # إنشاء المستخدم
        new_user = {
            'id': self.generate_user_id(),
            'username': username,
            'password': hashed_password,
            'email': email,
            'role': role.value,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True,
            'failed_login_attempts': 0,
            'locked_until': None
        }
        
        users.append(new_user)
        self.save_users(users)
        
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        """مصادقة المستخدم"""
        
        users = self.load_users()
        user = next((u for u in users if u['username'] == username), None)
        
        if not user:
            return False
        
        # التحقق من حالة القفل
        if user.get('locked_until'):
            lock_time = datetime.fromisoformat(user['locked_until'])
            if datetime.now() < lock_time:
                return False
        
        # التحقق من كلمة المرور
        if bcrypt.verify(password, user['password']):
            # إعادة تعيين محاولات الدخول الفاشلة
            user['failed_login_attempts'] = 0
            user['last_login'] = datetime.now().isoformat()
            user['locked_until'] = None
            
            self.current_user = user
            self.save_users(users)
            
            return True
        else:
            # زيادة محاولات الدخول الفاشلة
            user['failed_login_attempts'] += 1
            
            # قفل الحساب بعد 5 محاولات فاشلة
            if user['failed_login_attempts'] >= 5:
                lock_duration = timedelta(minutes=30)
                user['locked_until'] = (datetime.now() + lock_duration).isoformat()
            
            self.save_users(users)
            return False
    
    def has_permission(self, permission: Permission) -> bool:
        """التحقق من صلاحية المستخدم الحالي"""
        
        if not self.current_user:
            return False
        
        user_role = UserRole(self.current_user['role'])
        return permission in self.ROLE_PERMISSIONS.get(user_role, [])
    
    def require_permission(self, permission: Permission):
        """ديكوريتر للتحقق من الصلاحيات"""
        
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.has_permission(permission):
                    raise PermissionError(f"ليس لديك صلاحية: {permission.value}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
```

---

**التالي**: [أنماط التصميم](design-patterns.md)