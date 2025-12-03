import json
from datetime import datetime
from .utils import load_json, save_json

def sync_lists(lists_sheet, lists_file, ui=None):
    lists_data = load_json(lists_file, default={})
    if not lists_data:
        return

    try:
        rows = lists_sheet.get_all_records()
        existing = {str(r.get("list_name", "")).strip(): (i, r) for i, r in enumerate(rows)}

        uploaded = updated = skipped = 0
        for list_name, items in lists_data.items():
            list_name = str(list_name).strip()
            if not isinstance(items, list) or not items:
                continue

            # تقليل التكرار حسب final_code/template
            uniq = {}
            for item in items:
                key = item.get("__final_code__") or item.get("template")
                if key:
                    uniq[key] = item
            items_list = list(uniq.values())
            items_json = json.dumps(items_list, ensure_ascii=False, indent=2)
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            if list_name in existing:
                row_number, old_row = existing[list_name]
                row_number += 2
                old_items_json = old_row.get("items", "")
                try:
                    old_items = json.loads(old_items_json) if old_items_json else []
                except Exception:
                    old_items = []
                if sorted(old_items, key=lambda x: json.dumps(x, sort_keys=True)) == sorted(items_list, key=lambda x: json.dumps(x, sort_keys=True)):
                    skipped += 1
                    continue

                lists_sheet.update(f"A{row_number}:D{row_number}", [[list_name, "", items_json, now]])
                updated += 1
            else:
                lists_sheet.append_row([list_name, "", items_json, now])
                uploaded += 1

        if ui and (uploaded + updated) > 0:
            try:
                pass
                #ui.show_toast(f"✅ قوائم: رفع {uploaded} - تحديث {updated}", "success")
            except:
                pass

    except Exception:
        raise

def download_lists(lists_sheet, lists_file):
    rows = lists_sheet.get_all_records()
    result = {}
    for r in rows:
        list_name = str(r.get("list_name", "")).strip()
        items_json = r.get("items")
        if not list_name or not items_json:
            continue
        try:
            items = json.loads(items_json)
        except Exception:
            continue
        result[list_name] = items
    if result:
        save_json(lists_file, result)
