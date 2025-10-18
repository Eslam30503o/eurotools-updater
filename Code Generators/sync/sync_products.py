import json
from datetime import datetime
from .utils import load_json, save_json

def sync_products(products_sheet, database_file, ui=None):
    """ارفع البيانات المحلية إلى Google (ProductsData)."""
    local_data = load_json(database_file, default=[])
    if isinstance(local_data, dict):
        # تحويل dict -> list
        local_data = list(local_data.values())

    try:
        rows = products_sheet.get_all_records()  # يعتمد على رأس الصف 1
        remote_by_code = {str(r.get("final_code") or "").strip(): r for r in rows}

        updated_count = 0
        uploaded_count = 0

        for product in local_data:
            props = product.get("properties", {})
            template = product.get("template", "") or ""
            final_code = product.get("__final_code__") or product.get("final_code", "")

            if not final_code:
                final_code = template
                for k, v in (props or {}).items():
                    final_code = final_code.replace(f"{{{k}}}", str(v))
                final_code = final_code.lower().replace(" ", "")
                product["__final_code__"] = final_code

            if final_code in remote_by_code and remote_by_code[final_code]:
                row_index = rows.index(remote_by_code[final_code]) + 2
                products_sheet.update(f"A{row_index}:I{row_index}", [[
                    product.get("name_ar", ""),
                    product.get("name_en", ""),
                    product.get("category", ""),
                    product.get("description", ""),
                    json.dumps(product.get("properties", {}), ensure_ascii=False),
                    product.get("template", ""),
                    final_code,
                    product.get("project_name", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ]])
                updated_count += 1
            else:
                products_sheet.append_row([
                    product.get("name_ar", ""),
                    product.get("name_en", ""),
                    product.get("category", ""),
                    product.get("description", ""),
                    json.dumps(product.get("properties", {}), ensure_ascii=False),
                    product.get("template", ""),
                    final_code,
                    product.get("project_name", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ])
                uploaded_count += 1

        if ui and (uploaded_count + updated_count) > 0:
            try:
                ui.show_toast(f"✅ تم رفع {uploaded_count} وتحديث {updated_count} منتج.", "success")
            except:
                pass

    except Exception as e:
        # Caller يجب أن يتعامل مع تعيين is_connected=False عند الفشل
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
                "project_name": row.get("project_name", "")
            }
            updated_data.append(product)
        except Exception:
            continue

    if updated_data:
        save_json(database_file, updated_data)
