# 🔧 استكشاف الأخطاء وإصلاحها

دليل شامل لحل المشاكل الشائعة في Euro Tools Code Manager.

## 🎯 نظرة عامة

هذا الدليل يساعدك في تشخيص وحل المشاكل التي قد تواجهها أثناء استخدام التطبيق.

## 🚨 المشاكل الشائعة وحلولها

### 1. مشاكل بدء التشغيل

#### المشكلة: التطبيق لا يبدأ
```
🔍 الأعراض:
• لا يظهر شيء عند النقر على التطبيق
• رسالة خطأ عند محاولة التشغيل
• التطبيق يتوقف فوراً بعد البدء
```

**الحلول المقترحة:**

##### الحل 1: التحقق من متطلبات النظام
```bash
# التحقق من إصدار Python
python --version
# يجب أن يكون 3.8 أو أحدث

# التحقق من المكتبات المطلوبة
pip list | grep customtkinter
pip list | grep pandas
pip list | grep gspread
```

##### الحل 2: إعادة تثبيت المتطلبات
```bash
# إعادة تثبيت جميع المتطلبات
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# أو تثبيت كل مكتبة منفردة
pip install customtkinter pandas gspread google-auth
```

##### الحل 3: فحص ملفات البيانات
```bash
# التحقق من وجود ملفات البيانات الأساسية
ls -la *.json

# إنشاء ملفات البيانات إذا كانت مفقودة
echo '{"tools": [], "metadata": {"version": "4.5.0"}}' > tools.json
echo '{"lists": []}' > lists.json
echo '{"users": []}' > users.json
```

#### المشكلة: رسالة "Module not found"
```
🔍 الخطأ:
ModuleNotFoundError: No module named 'customtkinter'
```

**الحل:**
```bash
# تثبيت المكتبة المفقودة
pip install customtkinter

# أو تثبيت جميع المتطلبات
pip install -r requirements.txt

# في حالة استخدام بيئة افتراضية
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. مشاكل واجهة المستخدم

#### المشكلة: الواجهة تظهر بشكل غريب أو مشوه
```
🔍 الأعراض:
• النصوص متداخلة أو غير واضحة
• الأزرار في أماكن خاطئة
• الألوان غير صحيحة
• حجم النوافذ غير مناسب
```

**الحلول:**

##### الحل 1: إعادة تعيين إعدادات الواجهة
```python
# حذف ملف الإعدادات لإعادة تعيين الواجهة
import os
if os.path.exists('ui_settings.json'):
    os.remove('ui_settings.json')

# إعادة تشغيل التطبيق
```

##### الحل 2: تحديث إعدادات العرض
```
⚙️ في إعدادات التطبيق:
1. اذهب إلى الإعدادات > المظهر
2. اختر "إعادة تعيين للافتراضي"
3. أعد تشغيل التطبيق
4. اختر دقة الشاشة المناسبة
```

##### الحل 3: التحقق من إعدادات النظام
```
🖥️ إعدادات Windows:
1. كليك يمين على سطح المكتب
2. اختر "Display settings"
3. تأكد من أن Scale هو 100% أو 125%
4. أعد تشغيل التطبيق

🖥️ إعدادات macOS:
1. System Preferences > Displays
2. اختر "Default for display"
3. أعد تشغيل التطبيق
```

#### المشكلة: التطبيق بطيء أو يتجمد
```
🔍 الأعراض:
• استجابة بطيئة للنقرات
• تجمد عند فتح النوافذ
• بطء في تحميل البيانات
• استهلاك عالي للذاكرة
```

**الحلول:**

##### الحل 1: تحسين الأداء
```python
# في إعدادات التطبيق
performance_settings = {
    "enable_cache": True,
    "max_cache_size": 1000,
    "lazy_loading": True,
    "reduce_animations": True
}
```

##### الحل 2: تنظيف البيانات
```
🧹 خطوات التنظيف:
1. اذهب إلى الإعدادات > الصيانة
2. انقر على "تنظيف الملفات المؤقتة"
3. انقر على "ضغط قاعدة البيانات"
4. انقر على "إعادة بناء الفهارس"
5. أعد تشغيل التطبيق
```

### 3. مشاكل البيانات

#### المشكلة: فقدان البيانات أو تلفها
```
🔍 الأعراض:
• الأدوات المحفوظة لا تظهر
• رسالة "ملف البيانات تالف"
• البيانات تختفي بعد إعادة التشغيل
• أخطاء في تحميل القوائم
```

**الحلول:**

##### الحل 1: استعادة من النسخة الاحتياطية
```
💾 استعادة النسخة الاحتياطية:
1. اذهب إلى مجلد "backups"
2. ابحث عن أحدث نسخة احتياطية
3. انسخ الملفات إلى المجلد الرئيسي
4. أعد تشغيل التطبيق

# أو استخدم الأداة المدمجة
python backup_restore.py --restore backups/latest_backup.zip
```

##### الحل 2: إصلاح ملفات البيانات
```python
# أداة إصلاح البيانات
import json
import shutil
from datetime import datetime

def repair_data_file(file_path):
    """إصلاح ملف البيانات التالف"""
    
    # إنشاء نسخة احتياطية
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    
    try:
        # محاولة تحميل الملف
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ الملف {file_path} سليم")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في الملف {file_path}: {e}")
        
        # محاولة الإصلاح
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إصلاحات شائعة
            content = content.replace('}\n{', '},\n{')  # إضافة فواصل مفقودة
            content = content.strip()
            
            if not content.startswith('{'):
                content = '{' + content
            if not content.endswith('}'):
                content = content + '}'
            
            # محاولة تحميل المحتوى المُصلح
            repaired_data = json.loads(content)
            
            # حفظ الملف المُصلح
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(repaired_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ تم إصلاح الملف {file_path}")
            return True
            
        except Exception as repair_error:
            print(f"❌ فشل في إصلاح الملف: {repair_error}")
            
            # إنشاء ملف جديد فارغ
            default_data = {
                "tools": [] if "tools" in file_path else [],
                "lists": [] if "lists" in file_path else [],
                "users": [] if "users" in file_path else [],
                "metadata": {"version": "4.5.0", "created": datetime.now().isoformat()}
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            
            print(f"⚠️ تم إنشاء ملف جديد: {file_path}")
            return False

# تشغيل الإصلاح
repair_data_file('tools.json')
repair_data_file('lists.json')
repair_data_file('users.json')
```

#### المشكلة: أكواد الأدوات مكررة
```
🔍 المشكلة:
• ظهور أدوات بنفس الكود
• رسائل تحذير من التكرار
• مشاكل في البحث والفلترة
```

**الحل:**
```python
# أداة إصلاح الأكواد المكررة
def fix_duplicate_codes():
    """إصلاح الأكواد المكررة"""
    
    with open('tools.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tools = data.get('tools', [])
    seen_codes = set()
    fixed_tools = []
    duplicates_found = 0
    
    for tool in tools:
        original_code = tool.get('id', '')
        
        if original_code in seen_codes:
            # توليد كود جديد
            base_code = original_code.split('-')[0] if '-' in original_code else 'TOOL'
            counter = 1
            
            while f"{base_code}-{counter:04d}" in seen_codes:
                counter += 1
            
            new_code = f"{base_code}-{counter:04d}"
            tool['id'] = new_code
            duplicates_found += 1
            
            print(f"🔄 تم تغيير الكود من {original_code} إلى {new_code}")
        
        seen_codes.add(tool['id'])
        fixed_tools.append(tool)
    
    # حفظ البيانات المُصلحة
    data['tools'] = fixed_tools
    
    with open('tools.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم إصلاح {duplicates_found} كود مكرر")

# تشغيل الإصلاح
fix_duplicate_codes()
```

### 4. مشاكل المزامنة السحابية

#### المشكلة: فشل المزامنة مع Google Sheets
```
🔍 الأعراض:
• رسالة "فشل في الاتصال"
• "انتهت صلاحية المفاتيح"
• "ليس لديك صلاحية للوصول"
• المزامنة تتوقف في المنتصف
```

**الحلول:**

##### الحل 1: التحقق من الاتصال
```bash
# اختبار الاتصال بالإنترنت
ping google.com

# اختبار الوصول لـ Google Sheets API
curl -I https://sheets.googleapis.com/v4/spreadsheets
```

##### الحل 2: تجديد مفاتيح الوصول
```
🔑 تجديد المفاتيح:
1. اذهب إلى Google Cloud Console
2. اختر مشروعك
3. اذهب إلى "APIs & Services" > "Credentials"
4. احذف Service Account القديم
5. أنشئ Service Account جديد
6. حمل ملف JSON الجديد
7. استبدل الملف القديم في التطبيق
8. أعد تشغيل التطبيق
```

##### الحل 3: فحص الصلاحيات
```python
# اختبار صلاحيات Google Sheets
import gspread
from google.oauth2.service_account import Credentials

def test_google_sheets_access():
    """اختبار الوصول لـ Google Sheets"""
    
    try:
        # تحميل المفاتيح
        creds = Credentials.from_service_account_file('service_account.json')
        client = gspread.authorize(creds)
        
        # اختبار الوصول
        sheets = client.openall()
        print(f"✅ تم العثور على {len(sheets)} جدول بيانات")
        
        # اختبار القراءة والكتابة
        if sheets:
            sheet = sheets[0]
            worksheet = sheet.sheet1
            
            # اختبار القراءة
            data = worksheet.get_all_records()
            print(f"✅ تم قراءة {len(data)} صف")
            
            # اختبار الكتابة
            test_cell = worksheet.cell(1, 1)
            print(f"✅ تم قراءة الخلية: {test_cell.value}")
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الوصول: {e}")
        return False

# تشغيل الاختبار
test_google_sheets_access()
```

#### المشكلة: تعارضات في البيانات
```
🔍 المشكلة:
• رسائل تحذير من التعارضات
• بيانات مختلفة في التطبيق والسحابة
• فقدان بعض التحديثات
```

**الحل:**
```python
# حل التعارضات يدوياً
def resolve_sync_conflicts():
    """حل تعارضات المزامنة"""
    
    print("🔍 فحص التعارضات...")
    
    # تحميل البيانات المحلية
    with open('tools.json', 'r', encoding='utf-8') as f:
        local_data = json.load(f)
    
    # تحميل البيانات السحابية
    # (هذا مثال مبسط)
    cloud_data = fetch_cloud_data()
    
    conflicts = []
    
    # مقارنة البيانات
    for local_tool in local_data.get('tools', []):
        tool_id = local_tool['id']
        cloud_tool = find_tool_in_cloud(cloud_data, tool_id)
        
        if cloud_tool:
            if local_tool['updated_at'] != cloud_tool['updated_at']:
                conflicts.append({
                    'tool_id': tool_id,
                    'local': local_tool,
                    'cloud': cloud_tool
                })
    
    # عرض التعارضات للمستخدم
    if conflicts:
        print(f"⚠️ تم العثور على {len(conflicts)} تعارض")
        for conflict in conflicts:
            print(f"تعارض في الأداة: {conflict['tool_id']}")
            # هنا يمكن عرض واجهة للمستخدم لاختيار الحل
    else:
        print("✅ لا توجد تعارضات")

# تشغيل حل التعارضات
resolve_sync_conflicts()
```

### 5. مشاكل الأداء

#### المشكلة: التطبيق يستهلك ذاكرة كثيرة
```
🔍 الأعراض:
• بطء في النظام عموماً
• رسائل تحذير من نقص الذاكرة
• التطبيق يتوقف فجأة
• استجابة بطيئة جداً
```

**الحلول:**

##### الحل 1: تحسين استخدام الذاكرة
```python
# مراقبة استخدام الذاكرة
import psutil
import gc

def monitor_memory_usage():
    """مراقبة استخدام الذاكرة"""
    
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"استخدام الذاكرة: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"الذاكرة الافتراضية: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # تنظيف الذاكرة
    gc.collect()
    
    memory_info_after = process.memory_info()
    print(f"بعد التنظيف: {memory_info_after.rss / 1024 / 1024:.2f} MB")

# تشغيل المراقبة
monitor_memory_usage()
```

##### الحل 2: تحسين تحميل البيانات
```python
# تحميل البيانات بشكل تدريجي
class OptimizedDataLoader:
    """محمل البيانات المحسن"""
    
    def __init__(self):
        self.cache = {}
        self.max_cache_size = 1000
    
    def load_tools_paginated(self, page=1, page_size=50):
        """تحميل الأدوات بشكل مقسم"""
        
        cache_key = f"tools_page_{page}_{page_size}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # تحميل البيانات
        with open('tools.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tools = data.get('tools', [])
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_tools = tools[start_idx:end_idx]
        
        # إضافة للذاكرة المؤقتة
        if len(self.cache) < self.max_cache_size:
            self.cache[cache_key] = page_tools
        
        return page_tools
    
    def clear_cache(self):
        """مسح الذاكرة المؤقتة"""
        self.cache.clear()
        gc.collect()

# استخدام المحمل المحسن
loader = OptimizedDataLoader()
tools_page_1 = loader.load_tools_paginated(1, 50)
```

## 🛠️ أدوات التشخيص المتقدمة

### أداة فحص النظام الشاملة

```python
#!/usr/bin/env python3
"""
أداة التشخيص الشاملة لـ Euro Tools Code Manager
"""

import os
import sys
import json
import psutil
import platform
from pathlib import Path
from datetime import datetime

class SystemDiagnostics:
    """أداة التشخيص الشاملة"""
    
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'python_info': {},
            'dependencies': {},
            'files_status': {},
            'performance': {},
            'errors': []
        }
    
    def run_full_diagnostics(self):
        """تشغيل التشخيص الشامل"""
        
        print("🔍 بدء التشخيص الشامل...")
        
        self.check_system_info()
        self.check_python_environment()
        self.check_dependencies()
        self.check_data_files()
        self.check_performance()
        self.check_permissions()
        
        self.generate_report()
        
        print("✅ انتهى التشخيص")
    
    def check_system_info(self):
        """فحص معلومات النظام"""
        
        print("📊 فحص معلومات النظام...")
        
        self.report['system_info'] = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('.').percent
        }
    
    def check_python_environment(self):
        """فحص بيئة Python"""
        
        print("🐍 فحص بيئة Python...")
        
        self.report['python_info'] = {
            'version': sys.version,
            'executable': sys.executable,
            'path': sys.path[:5],  # أول 5 مسارات فقط
            'encoding': sys.getdefaultencoding()
        }
    
    def check_dependencies(self):
        """فحص المكتبات المطلوبة"""
        
        print("📦 فحص المكتبات...")
        
        required_packages = [
            'customtkinter', 'pandas', 'gspread', 
            'google-auth', 'Pillow', 'requests'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.report['dependencies'][package] = 'مثبت'
            except ImportError:
                self.report['dependencies'][package] = 'مفقود'
                self.report['errors'].append(f"المكتبة مفقودة: {package}")
    
    def check_data_files(self):
        """فحص ملفات البيانات"""
        
        print("📁 فحص ملفات البيانات...")
        
        data_files = ['tools.json', 'lists.json', 'users.json', 'config.json']
        
        for file_name in data_files:
            file_path = Path(file_name)
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.report['files_status'][file_name] = {
                        'exists': True,
                        'valid_json': True,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat()
                    }
                    
                except json.JSONDecodeError as e:
                    self.report['files_status'][file_name] = {
                        'exists': True,
                        'valid_json': False,
                        'error': str(e)
                    }
                    self.report['errors'].append(f"ملف JSON تالف: {file_name}")
                    
            else:
                self.report['files_status'][file_name] = {
                    'exists': False
                }
                self.report['errors'].append(f"ملف مفقود: {file_name}")
    
    def check_performance(self):
        """فحص الأداء"""
        
        print("⚡ فحص الأداء...")
        
        # قياس استخدام الذاكرة
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # قياس استخدام المعالج
        cpu_percent = psutil.cpu_percent(interval=1)
        
        self.report['performance'] = {
            'memory_usage_mb': memory_info.rss / 1024 / 1024,
            'cpu_usage_percent': cpu_percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
        }
    
    def check_permissions(self):
        """فحص الصلاحيات"""
        
        print("🔐 فحص الصلاحيات...")
        
        # فحص صلاحيات الكتابة
        test_file = Path('test_write_permission.tmp')
        
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()
            
            self.report['permissions'] = {
                'write_access': True
            }
            
        except PermissionError:
            self.report['permissions'] = {
                'write_access': False
            }
            self.report['errors'].append("ليس لديك صلاحية الكتابة في المجلد الحالي")
    
    def generate_report(self):
        """إنشاء التقرير النهائي"""
        
        report_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 تم حفظ التقرير في: {report_file}")
        
        # عرض ملخص
        self.print_summary()
    
    def print_summary(self):
        """عرض ملخص التشخيص"""
        
        print("\n" + "="*50)
        print("📋 ملخص التشخيص")
        print("="*50)
        
        # معلومات النظام
        system = self.report['system_info']
        print(f"🖥️ النظام: {system['system']} {system['release']}")
        print(f"💾 الذاكرة: {system['memory_available'] / 1024**3:.1f} GB متاحة")
        print(f"💿 القرص: {system['disk_usage']:.1f}% مستخدم")
        
        # Python
        python_version = self.report['python_info']['version'].split()[0]
        print(f"🐍 Python: {python_version}")
        
        # المكتبات
        deps = self.report['dependencies']
        missing_deps = [k for k, v in deps.items() if v == 'مفقود']
        if missing_deps:
            print(f"❌ مكتبات مفقودة: {', '.join(missing_deps)}")
        else:
            print("✅ جميع المكتبات مثبتة")
        
        # ملفات البيانات
        files = self.report['files_status']
        corrupted_files = [k for k, v in files.items() if not v.get('valid_json', True)]
        if corrupted_files:
            print(f"❌ ملفات تالفة: {', '.join(corrupted_files)}")
        else:
            print("✅ جميع ملفات البيانات سليمة")
        
        # الأداء
        perf = self.report['performance']
        print(f"⚡ استخدام الذاكرة: {perf['memory_usage_mb']:.1f} MB")
        print(f"⚡ استخدام المعالج: {perf['cpu_usage_percent']:.1f}%")
        
        # الأخطاء
        if self.report['errors']:
            print(f"\n❌ الأخطاء المكتشفة ({len(self.report['errors'])}):")
            for error in self.report['errors']:
                print(f"  • {error}")
        else:
            print("\n✅ لم يتم اكتشاف أخطاء")

if __name__ == "__main__":
    diagnostics = SystemDiagnostics()
    diagnostics.run_full_diagnostics()
```

## 📞 الحصول على المساعدة

### متى تطلب المساعدة

```
🆘 اطلب المساعدة إذا:
• جربت جميع الحلول المقترحة
• المشكلة تتكرر باستمرار
• تؤثر على عملك بشكل كبير
• تحتاج مساعدة في إعداد معقد
```

### قنوات الدعم

#### 1. الدعم الذاتي
- **الوثائق**: ابدأ بقراءة هذا الدليل
- **الأسئلة الشائعة**: [FAQ](faq.md)
- **أدوات التشخيص**: استخدم الأدوات المدمجة

#### 2. الدعم المجتمعي
- **GitHub Issues**: للأخطاء والاقتراحات
- **GitHub Discussions**: للأسئلة العامة
- **منتدى المستخدمين**: للنقاشات

#### 3. الدعم المباشر
- **البريد الإلكتروني**: support@eurotools.com
- **نموذج الدعم**: عبر الموقع الرسمي

### معلومات مطلوبة عند طلب المساعدة

```
📋 أرفق هذه المعلومات:
• وصف مفصل للمشكلة
• خطوات إعادة إنتاج المشكلة
• رسائل الخطأ (إن وجدت)
• تقرير التشخيص
• إصدار التطبيق ونظام التشغيل
• لقطات شاشة (إن أمكن)
```

---

**التالي**: [الحصول على المساعدة](getting-help.md)