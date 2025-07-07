import gspread, os
from google.oauth2.service_account import Credentials
from src.utils.credentials import get_credentials_with_retry

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"
SHEET_NAME = "audios_count"

def write_to_sheet(data: dict):
    credentials = get_credentials_with_retry()
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    # Clear sheet first
    sheet.clear()

    # ✅ Write headers (no subfolder columns)
    rows = [["Annotator", "Total Audio Files"]]

    # ✅ Flatten data without subfolder details
    for annotator, values in data.items():
        total = values.get("total_audio", 0)
        rows.append([annotator, total])

    sheet.append_rows(rows, value_input_option="USER_ENTERED")
