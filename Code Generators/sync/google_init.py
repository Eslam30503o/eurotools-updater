import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone

def initialize_google(creds_file: str, sheet_name: str, scope: list):
    """
    يرجع: (client, sheet, locks_sheet, products_sheet, lists_sheet)
    يرفع استثناء لو ملف الاعتماد خطأ.
    """
    creds = Credentials.from_service_account_file(creds_file, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name)

    # Locks sheet
    try:
        locks_sheet = sheet.worksheet("Locks")
    except gspread.WorksheetNotFound:
        locks_sheet = sheet.add_worksheet(title="Locks", rows="20", cols="5")
        locks_sheet.update('A1:B1', [["client_id", "timestamp"]])

    # ProductsData
    try:
        products_sheet = sheet.worksheet("ProductsData")
    except gspread.WorksheetNotFound:
        products_sheet = sheet.add_worksheet(title="ProductsData", rows="500", cols="10")
    if not products_sheet.row_values(1):
        headers = ["name_ar", "name_en", "category", "description", "properties", "template", "final_code", "project_name", "updated_at"]
        products_sheet.update('A1:I1', [headers])

    # ListsData
    try:
        lists_sheet = sheet.worksheet("ListsData")
    except gspread.WorksheetNotFound:
        lists_sheet = sheet.add_worksheet(title="ListsData", rows="200", cols="5")
    if not lists_sheet.row_values(1):
        lists_sheet.update('A1:D1', [["list_name", "description", "items", "uploaded_at"]])

    return client, sheet, locks_sheet, products_sheet, lists_sheet
