import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from passlib.hash import bcrypt
from data_manager import DataManager


# ================================
# ⚙️ تهيئة DataManager
# ================================
dm = DataManager()
LOCAL_USERS_FILE = os.path.join(dm.safe_data_dir, "users.json")
SERVICE_ACCOUNT_FILE = dm.SYNC_FILE
SPREADSHEET_NAME = "My Tools Sync"
USERS_SHEET = "users"

# ================================
# 🧩 تأكد من وجود ملف users.json
# ================================
if not os.path.exists(LOCAL_USERS_FILE):
    with open(LOCAL_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
else:
    with open(LOCAL_USERS_FILE, "r+", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            f.seek(0)
            json.dump([], f, ensure_ascii=False, indent=2)
            f.truncate()

# ================================
# 📡 الاتصال بـ Google Sheets
# ================================
def connect_to_sheet(readonly=False):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly" if readonly
        else "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    client = gspread.authorize(creds)

    try:
        sheet = client.open(SPREADSHEET_NAME).worksheet(USERS_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        # إنشاء الورقة لو مش موجودة
        file = client.open(SPREADSHEET_NAME)
        sheet = file.add_worksheet(title=USERS_SHEET, rows="100", cols="4")
        sheet.update("A1:D1", [["username", "password_hash", "role", "created_at"]])

    return sheet


# ================================
# ➕ إضافة مستخدم جديد
# ================================
def add_user(username: str, password: str, role: str = "user"):
    sheet = connect_to_sheet()
    usernames = [u.strip() for u in sheet.col_values(1)[1:] if u.strip()]

    if username.strip() in usernames:
        print(f"⚠️ المستخدم '{username}' موجود بالفعل.")
        return False

    password_hash = bcrypt.hash(password)
    created_at = datetime.utcnow().isoformat()

    # ✳️ الحفظ في Google Sheets
    sheet.append_row(
        [username, password_hash, role, created_at],
        value_input_option="RAW"
    )

    # ✳️ الحفظ في ملف محلي
    try:
        with open(LOCAL_USERS_FILE, "r", encoding="utf-8") as f:
            local_users = json.load(f)
    except json.JSONDecodeError:
        local_users = []

    local_users.append({
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "created_at": created_at
    })

    with open(LOCAL_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(local_users, f, ensure_ascii=False, indent=2)

    print(f"✅ تمت إضافة المستخدم '{username}' بنجاح.")
    return True


# ================================
# 🔐 التحقق من بيانات المستخدم
# ================================
def verify_user(username: str, password: str) -> bool:
    """يتحقق من بيانات المستخدم (من Google أولاً، ثم من النسخة المحلية)."""
    try:
        sheet = connect_to_sheet(readonly=True)
        rows = sheet.get_all_records()
    except Exception as e:
        print(f"⚠️ تعذر الاتصال بـ Google Sheets: {e}\nسيتم التحقق محليًا فقط.")
        rows = []

    # 🔹 ابحث عن المستخدم في Google أولاً
    for row in rows:
        if row.get("username") == username:
            stored_hash = row.get("password_hash", "")
            try:
                if bcrypt.verify(password, stored_hash):
                    return True, row.get("role")   # ← نرجع الـ role
                else:
                    return False, None
            except Exception:
                print("⚠️ كلمة المرور تالفة أو غير صالحة.")
                return False, None

    # 🔹 fallback محلي (Offline)
    if os.path.exists(LOCAL_USERS_FILE):
        try:
            with open(LOCAL_USERS_FILE, "r", encoding="utf-8") as f:
                local_users = json.load(f)
        except json.JSONDecodeError:
            local_users = []

        for u in local_users:
            if u["username"] == username:
                try:
                    if bcrypt.verify(password, u["password_hash"]):
                        return True, u.get("role")   # ← نرجع الـ role من الملف المحلي أيضًا
                    else:
                        return False, None
                except Exception:
                    return False, None

    return False, None


# ================================
# 📋 عرض جميع المستخدمين
# ================================
def list_users():
    try:
        sheet = connect_to_sheet(readonly=True)
        users = sheet.get_all_records()
        if not users:
            print("🚫 لا يوجد مستخدمون بعد.")
            return
        print("\n📋 قائمة المستخدمين:")
        for u in users:
            print(f"- {u['username']} ({u['role']}) - أنشئ في {u['created_at']}")
    except Exception as e:
        print(f"⚠️ خطأ أثناء قراءة المستخدمين: {e}")


# ================================
# 🚀 تنفيذ مباشر (اختياري للتجريب)
# ================================
if __name__ == "__main__":
    print("🔐 نظام إدارة مستخدمي Google Sheets 🔐")
    print("1️⃣ إضافة مستخدم")
    print("2️⃣ تحقق من مستخدم")
    print("3️⃣ عرض المستخدمين")
    choice = input("اختيارك: ").strip()

    if choice == "1":
        user = input("اسم المستخدم: ").strip()
        pwd = input("كلمة المرور: ").strip()
        role = input("الدور (افتراضي=user): ").strip() or "user"
        add_user(user, pwd, role)

    elif choice == "2":
        user = input("اسم المستخدم: ").strip()
        pwd = input("كلمة المرور: ").strip()
        if verify_user(user, pwd):
            print("✅ تسجيل الدخول ناجح!")
        else:
            print("❌ بيانات الدخول غير صحيحة.")

    elif choice == "3":
        list_users()
    else:
        print("❌ اختيار غير صحيح.")
