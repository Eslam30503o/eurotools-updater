import json
import os

def load_json(file_name, default=None, create_if_missing=False):
    if default is None:
        default = [] if "tools" in os.path.basename(file_name) else {}
    if not os.path.exists(file_name):
        if create_if_missing:
            save_json(file_name, default)
        return default
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(file_name, data):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
