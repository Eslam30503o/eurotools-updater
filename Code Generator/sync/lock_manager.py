import time
from datetime import datetime, timezone

class LockManager:
    def __init__(self, locks_sheet, client_id: str):
        self.locks_sheet = locks_sheet
        self.client_id = client_id

    def _now_iso(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def acquire_lock(self, timeout=30, retry_delay=1, lock_ttl=90):
        if not self.locks_sheet:
            return False

        start = time.time()
        owner = self.client_id

        while time.time() - start < timeout:
            try:
                values = self.locks_sheet.get('A2:B2')
                current_owner = (values[0][0] if values and values[0] else "").strip()
                current_ts = (values[0][1] if values and len(values[0]) > 1 else "").strip()

                if not current_owner:
                    now = self._now_iso()
                    self.locks_sheet.update('A2:B2', [[owner, now]])
                    owner_after = (self.locks_sheet.acell('A2').value or "").strip()
                    if owner_after == owner:
                        return True
                else:
                    # تحقق من عمر القفل
                    if current_ts:
                        try:
                            ts_dt = datetime.fromisoformat(current_ts.strip().replace("Z", "+00:00"))
                            age = (datetime.now(timezone.utc) - ts_dt).total_seconds()
                        except Exception:
                            age = lock_ttl + 1
                    else:
                        age = lock_ttl + 1

                    if age > lock_ttl:
                        now = self._now_iso()
                        self.locks_sheet.update('A2:B2', [[owner, now]])
                        owner_after = (self.locks_sheet.acell('A2').value or "").strip()
                        if owner_after == owner:
                            return True

                time.sleep(retry_delay)
            except Exception as e:
                print(f"⚠️ Lock acquire error: {e}")
                time.sleep(retry_delay)

        return False

    def refresh_remote_lock(self):
        """تحديث الطابع الزمني للقفل الحالي."""
        if not self.locks_sheet:
            return
        try:
            current_owner = (self.locks_sheet.acell('A2').value or "").strip()
            if current_owner == self.client_id:
                self.locks_sheet.update('B2', [[self._now_iso()]])
        except Exception as e:
            print(f"⚠️ Lock refresh error: {e}")

    def release_lock(self):
        """تحرير القفل إذا كنا المالك."""
        if not self.locks_sheet:
            return False
        try:
            current_owner = (self.locks_sheet.acell('A2').value or "").strip()
            if current_owner == self.client_id:
                self.locks_sheet.update('A2:B2', [["", ""]])
                return True
        except Exception as e:
            print(f"⚠️ Lock release error: {e}")
        return False
