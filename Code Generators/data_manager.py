import json
import os
import platform
from pathlib import Path
from tkinter import messagebox


class DataManager:
    def __init__(self):
        # =============================
        # 📂 تحديد المجلد الآمن للبيانات
        # =============================
        app_name = "EuroTools"

        if platform.system() == "Windows":
            base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / app_name / "data"
        else:
            base_dir = Path.home() / ".local" / "share" / app_name / "data"

        base_dir.mkdir(parents=True, exist_ok=True)
        self.safe_data_dir = base_dir

        self.DATABASE_FILE = str(base_dir / "tools_data.json")
        self.LISTS_FILE = str(base_dir / "lists_data.json")
        self.SYNC_FILE = str(base_dir / "my-tools-sync.json")
        self.CREDENTIALS_FILE = str(base_dir / "credentials.json")

        # ✅ تأكد من وجود الملفات أو أنشئها
        self.ensure_data_files_exist()

    # =============================
    # 🧩 إنشاء الملفات إن لم تكن موجودة
    # =============================
    def ensure_data_files_exist(self):
        """يتأكد من وجود ملفات JSON المطلوبة ويُنشئها عند الحاجة"""
        if not os.path.exists(self.DATABASE_FILE):
            with open(self.DATABASE_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        if not os.path.exists(self.LISTS_FILE):
            with open(self.LISTS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        # 🔹 ملف المزامنة
        if not os.path.exists(self.SYNC_FILE):
            data = {
        "type": "service_account",
      "project_id": "my-tools-sync",
        "private_key_id": "ab0987d765906863f90cf2acf180e3fad9abd3e4",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDSEM/FHaxAJ+eL\n/pe8OKjqXqrCQPTveBqZKD43wykHlypk8Pg1gxY7bvDuPO4qtIXZbi7m1nR5sqDT\nP42mJaqComIa+jNON1iLJpGoCUbYNFUO6FD3bDQTOZG8kT9ONlMXFZE6/B7HkHsE\nuhyq/8y9QB60kiR7mpn8Ax258s+HIqh9M8ZAE93ZL4fzseI4weUO2u67FLAxhYCT\nYRM3G297FZHDh+YvOyKbc0tb41xqLANdEhlXjYLutiAnxNL3zNwcAXGpy66XvYuV\n8udIxIpEtYIfwLF7pGcPY6arxkefhDheyYzQ35USzT5JmVVOGE6U6GQIe3LWmNGG\nztJeYwrjAgMBAAECggEAZ/I8tZf8y9RTLgGBuPg6kZrdmXkGGtdOJhp1SyeNzn09\nU6yvzd77adZ4bxMEcWpZz2FH4R8ejLfZAB9zKtN5n+HVdO7440vcyyJ/MezBOywO\nKO3JXt2SmS7EEFC5SCz2ibY44ryuSGcUkJ69n9orSDyJ1SV52xYB+2PZWlGt4npc\n1e948yNqbsMYC31TpfajixIwIvsDXDLQs6dutVxrKsaUEJq3u94HP6S/8bD3FvXt\nZMJ3EIL7NumIxyGZD0c35U1PO3DCW5Yz0SBIGEotkDoavaITeq4h4UPEQ7b1i8P2\nQSsX9xFNUDPaqnkseBIsZ94JphYCHtvKkgmPRaQlJQKBgQDu4DY2iUBuvA8QJpiv\nFOvDxSzLYxyZnlojQzFRD7sCSoVMzlm7cCo2Dyo6gqD0khjbwzK4T4BwPmtMcswf\nbgy5BTd+1bKesS09X4N+YNs0iQ79WgTDBPsqmV2EFVkNaziohLrgLYWRJsDqrOVf\nghhIZHhcQIWp9mh2oYVL6til5wKBgQDhH+IYTtSvR3VcsT3JnzXSVXbWr+la7oSW\nd2QrByHmyLwzdIdg/lrEmUt5Cek/gImgMWhmvjOvWMrvHBuytMxsOyzDE1BBQ2m6\nYtiozLztl29pGhVcvcgX8ajMs1U5NDNLo2dyIU2QOxcFJ5CBJgfT30qMoQiHB1IE\nDfneLSFbpQKBgFu9DfT51x3v6VUJjZ/HyBfCVMazhJtWnkVmm70G7oodtn3dzcZX\neE6UmmIoIspqhVN47rSsC6aPwkN03wG/EPHJmBuE1Hlvj/E/Ck/xwJ23eWNBPAzt\nj8w3ZBvC2xV1NSg6+U35DY/GM1atGdYJL2w18ad0PCEe+dV9iKS0R4nHAoGBAIu/\nyg/C596DIoTO9gcyUSvnp+TvwJGVHTN2m/Tl8ZKdK89ZWCzK2LfQXXyevW+RMF4E\nLcYR7m28VgWG0l7mQzwwo8HZPGm3Gmv8rnhi2Ck5Z4y8B2TR3uOWPW4NKStgjzM2\nFaJQsCCHveuSOu8hF5zbsSCJWozP64be0iysoVeNAoGAdfGMnKWq+19BLoKQ+bQ7\nG/Hzc8c+qpH39kdB6Iy8yIVoD+Lu4Qrv3F4OvimxME69w689DYFTkaGts+bsZc8i\nqR7cZ9QBcc/5Hw9lM3gAIQCIYfzIwj8FLI5S/q3hTiQS3BXxH2LpBz+F+g6hsIbn\n3n6NkKew90tSw0SHUcR2+IU=\n-----END PRIVATE KEY-----\n",
            "client_email": "my-tools-sync@my-tools-sync.iam.gserviceaccount.com",
              "client_id": "103712197912087915120",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                  "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-tools-sync%40my-tools-sync.iam.gserviceaccount.com",
                        "universe_domain": "googleapis.com"
}
            with open(self.SYNC_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        # 🔹 ملف بيانات الدخول
        if not os.path.exists(self.CREDENTIALS_FILE):
            data = {
  "type": "service_account",
  "project_id": "euro-tools-473006",
  "private_key_id": "01f67b5146ec9e7287dccf610e5f455350bf733e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDJ5oiJ0VICvUmy\nB6AO3gwls0rLjN6V9bwQUqFBaJ8TMvC5PeeE+LlfpPa/Dl8uAWR2g0HPecN6XoOz\nLalQSxzI3aLEQxTV06qhCuPXlEiykkj26oztg7l+Emktx3d5XpXvmdmYXJ4u+BUj\noYfTMA/9iPc1kw2R5PY7SPWsq+8cpT4anBFYW35MxJK0hc/xQ7DO2IfZ/5ql4OVP\nNoFcEqVn7IzC1ZCt7dxkO/7FBZRgjGNMIL42XVw32D74QGdxFTi4vBURw+jofics\n6b+G6DIzzMnK1fiAHghbry9yj1QrTpuv6rlFjYU3Wir/iT1d2fT24KVQiHWw3Tmq\nlsPdqZSXAgMBAAECggEAD0wZvUNwUMfRvRzpyiaVygd3G8wNE1SejqgMEr4gC17Z\nMVfY4lDMDsyba2dl28D8QSR5yIQDxRJDLUDA6tX+FNQCIJeqjPbwHyqJj8xq46jE\nwXyM9/P6imxPrsnFqhr6BkDkZTBjRdDDHUOAXIZwN7f4bwU4ynyMEXraLl6Ki+Nw\nvOrVNRNTge/pWSrMmAAnhDVk4+3D/4RLriJQ44CbQFIZMVPL+t65srDKxKuKToX1\nd9p7aV9gE1e/Cade57eyCy6HzYPwkLX2PveEJr9AlKx3Uhje5uK1ZHRHviL7ljXr\nloCuzGlN7r+ki4pcrsy1Ip35AQFUi3xu0oTVeUrEiQKBgQDvqvevnjx0UAj0i2ss\nZ8Y0zX2csmkXdh6FXhWOuU4kvvoA9vwDMNHs8fZqXb63rOx5gnNI9IA1XSLOjqXC\nJHwhPQOl/2DpliqNTR+ayufx77d4h7opjnK7vi2fc4lYNkB8JvwWnQhC3mASjK0L\nYEEL1Oi2zIO2H6ccUmB4Dzdf/wKBgQDXqLXuF52n1lqTQKGzjjHZ6885JE5dLOiX\n25QfREQkOWoTzdxsiTbRcf0ex+2LAiFewG0GhecUNKgrb6QNNIrFhBgsdZ52dYmo\n1DpFaDpWYx4OcVGHjUjQQSKWL+mQw02zqJLMkXhGcYoTVdAycj9wZfBskhN3AxLI\ndeZvySzLaQKBgHddLv7IUFOdiNhCl54GETE7JtRkBvMoYQsLULFEmSaz9s+EMv9j\n0SmxWIihJ9tSxHPABKrRGwl42V0GroeCpE/pk2eZSSsNHyRAxPzTEbHtMfNVpeIM\nkBfxH8fKQx0r5/HteJ/KldK37iFO7uA7kCnUYBKqyO5r1U7FuEYTTgEBAoGAJrpE\nWYpiJHbI8zKjFzSM3T6Miw1rCS58YnDrK6Y9umeZFg9c6xzE/F3E/9cVYGY0iehy\na752HdnK7WnyAvERjqDHGozQtSMsYmYiRL6P412PUzakVnxXvBZGWMQn5Hg+Juo5\n2oSxHa1cB1bcuYJsxAl6YHTnC/NAV0Fc7WwqICkCgYBl+g6igTrDdQX1gwLi9Hf4\nK8UHmw0PJOQHbT1ufuJ8/YxI4rToBkHYZL8LeOO2vPCzkf1p/Kc0yrESvSrKJicm\nBJUCJ4FFBAV8EbOfjb2MT6Mz2dDAeIlw4OLyRiBpminzs1h+x2e2W9lpaPkK4HgP\nf09YXDZYS5K5sSmFdvxJfw==\n-----END PRIVATE KEY-----\n",
  "client_email": "euro-tools@euro-tools-473006.iam.gserviceaccount.com",
  "client_id": "100467059774628349932",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/euro-tools%40euro-tools-473006.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

            with open(self.CREDENTIALS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    # =============================
    # 🧠 دوال التعامل مع الملفات
    # =============================

    def load_data(self, file_name):
        """تحميل البيانات من ملف JSON بشكل آمن مع إصلاح الملفات الفارغة أو التالفة"""
        try:
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                    # 🔹 الملف موجود لكن فاضي → نعيد إنشاؤه
                    if not content:
                        default_value = [] if "tools" in file_name else {}
                        self.save_data(file_name, default_value)
                        return default_value

                    # 🔹 نحاول تحميل JSON عادي
                    return json.loads(content)

            # 🔹 الملف مش موجود أساسًا
            default_value = [] if "tools" in file_name else {}
            self.save_data(file_name, default_value)
            return default_value

        except (FileNotFoundError, json.JSONDecodeError) as e:
            default_value = [] if "tools" in file_name else {}
            self.save_data(file_name, default_value)
            return default_value


    def save_data(self, file_name, data):
        """حفظ البيانات إلى ملف JSON داخل المجلد الآمن"""
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            return True
        except Exception as e:
            messagebox.showerror("Error", f"⚠️ Failed to save data to {file_name}:\n{str(e)}")
            return False

    # =============================
    # 📦 دوال خاصة بالأدوات والقوائم
    # =============================

    def load_tools(self):
        return self.load_data(self.DATABASE_FILE)

    def save_tools(self, data):
        return self.save_data(self.DATABASE_FILE, data)

    def load_lists(self):
        return self.load_data(self.LISTS_FILE)

    def save_lists(self, data):
        return self.save_data(self.LISTS_FILE, data)
