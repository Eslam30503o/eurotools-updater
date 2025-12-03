import json
from datetime import datetime
from .utils import load_json, save_json
import time

def sync_products(products_sheet, database_file, ui=None):
    """مزامنة البيانات المحلية مع Google Sheets بطريقة فعالة (batch update)."""
    local_data = load_json(database_file, default=[])
    if isinstance(local_data, dict):
        local_data = list(local_data.values())

    try:
        rows = products_sheet.get_all_records()
        remote_by_code = {str(r.get("final_code") or "").strip(): r for r in rows}

        updated_rows = []
        appended_rows = []
        batch_updates = []

        for idx, product in enumerate(local_data, start=2):
            props = product.get("properties", {})
            template = product.get("template", "") or ""
            final_code = product.get("__final_code__") or product.get("final_code", "")

            # توليد الكود النهائي لو غير موجود
            if not final_code:
                final_code = template
                for k, v in (props or {}).items():
                    final_code = final_code.replace(f"{{{k}}}", str(v))
                final_code = final_code.lower().replace(" ", "")
                product["__final_code__"] = final_code

            # بيانات الصف بالترتيب الصحيح
            row_data = [
                product.get("name_ar", ""),
                product.get("name_en", ""),
                product.get("category", ""),
                product.get("description", ""),
                json.dumps(product.get("properties", {}), ensure_ascii=False),
                product.get("template", ""),
                final_code,
                product.get("project_name", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                product.get("created_at", "")               # created_at ✅

            ]

            # تحديث أو إضافة
            if final_code in remote_by_code:
                row_index = rows.index(remote_by_code[final_code]) + 2
                batch_updates.append({"range": f"A{row_index}:J{row_index}", "values": [row_data]})
                updated_rows.append(final_code)
            else:
                appended_rows.append(row_data)

        # 🟢 إرسال التحديثات دفعة واحدة
        if batch_updates:
            products_sheet.batch_update(batch_updates)

        # 🟢 إرسال الصفوف الجديدة دفعة واحدة
        if appended_rows:
            products_sheet.append_rows(appended_rows)

        # ✅ عرض إشعار
        updated_count = len(updated_rows)
        uploaded_count = len(appended_rows)
        if ui and (uploaded_count + updated_count) > 0:
            try:
                pass
                # ui.show_toast(
                #     f"✅ تم رفع {uploaded_count} وتحديث {updated_count} منتج (Batch).",
                #     "success"
                # )
            except:
                pass

    except Exception as e:
        if ui:
            ui.show_toast(f"❌ فشل المزامنة: {e}", "error")
        raise


def download_products(products_sheet, database_file):
    """حمّل المنتجات من Google وحفظها محليًا."""
    rows = products_sheet.get_all_records()
    updated_data = []
    for row in rows:
        try:
            product = {
                "name_ar": row.get("name_ar", ""),
                "name_en": row.get("name_en", ""),
                "category": row.get("category", ""),
                "description": row.get("description", ""),
                "properties": json.loads(row.get("properties") or "{}"),
                "template": row.get("template", ""),
                "project_name": row.get("project_name", ""),
                "created_at": row.get("created_at", "")  # ✅ أضف هذا السطر

            }
            updated_data.append(product)
        except Exception:
            continue

    if updated_data:
        save_json(database_file, updated_data)
