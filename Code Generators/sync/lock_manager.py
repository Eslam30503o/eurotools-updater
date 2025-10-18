import time
from datetime import datetime, timezone

class LockManager:
    def __init__(self, locks_sheet, client_id: str):
        self.locks_sheet = locks_sheet
        self.client_id = client_id

    def _now_iso(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def acquire_lock(self, timeout=30, retry_delay=1, lock_ttl=90):
        """حاول أخذ القفل في الخلية A2/B2 داخل ورقة Locks."""
        if not self.locks_sheet:
            return False

        start = time.time()
        owner = self.client_id

        while time.time() - start < timeout:
            try:
                current_owner = (self.locks_sheet.acell('A2').value or "").strip()
                current_ts = (self.locks_sheet.acell('B2').value or "").strip()

                if not current_owner:
                    now = self._now_iso()
                    try:
                        self.locks_sheet.update('A2:B2', [[owner, now]])
                    except Exception:
                        pass
                    owner_after = (self.locks_sheet.acell('A2').value or "").strip()
                    if owner_after == owner:
                        return True
                else:
                    # تحقق من العمر
                    if current_ts:
                        try:
                            ts_dt = datetime.fromisoformat(current_ts.replace("Z", "+00:00"))
                            age = (datetime.now(timezone.utc) - ts_dt).total_seconds()
                        except Exception:
                            age = lock_ttl + 1
                    else:
                        age = lock_ttl + 1

                    if age > lock_ttl:
                        now = self._now_iso()
                        try:
                            self.locks_sheet.update('A2:B2', [[owner, now]])
                        except Exception:
                            pass
                        owner_after = (self.locks_sheet.acell('A2').value or "").strip()
                        if owner_after == owner:
                            return True

                time.sleep(retry_delay)
            except Exception:
                time.sleep(retry_delay)

        return False

    def refresh_remote_lock(self):
        """حدّث الطابع الزمني إذا كان هذا الكلاينت هو المالك."""
        if not self.locks_sheet:
            return
        try:
            current_owner = (self.locks_sheet.acell('A2').value or "").strip()
            if current_owner == self.client_id:
                self.locks_sheet.update('B2', [[self._now_iso()]])
        except Exception:
            pass

    def release_lock(self):
        """حَرّر القفل إذا كنا نحن المالك."""
        if not self.locks_sheet:
            return False
        try:
            current_owner = (self.locks_sheet.acell('A2').value or "").strip()
            if current_owner == self.client_id:
                self.locks_sheet.update('A2:B2', [["", ""]])
                return True
        except Exception:
            pass
        return False
