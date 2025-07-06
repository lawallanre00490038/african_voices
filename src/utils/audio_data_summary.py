import os
import io
import pandas as pd
import requests
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import time
from requests.exceptions import SSLError



import os, io, requests, json
import pandas as pd
from typing import List
import gspread, time
from requests.exceptions import SSLError
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import google.auth.exceptions
import base64

# Load environment variables
load_dotenv()

# Google Sheets settings
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "audios_count.json")

b64_creds = os.getenv("GOOGLE_CREDS_B64")

if not b64_creds:
    raise Exception("Missing GOOGLE_CREDS_B64 in environment.")

creds_dict = json.loads(base64.b64decode(b64_creds).decode("utf-8"))

# GitHub settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
RAW_FILE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/reports/audio_data_summary.xlsx"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Language → Workbook ID mapping
# SHEET_IDS_BY_LANG = {
#     "pidgin": "1-AgbYEevXN3zt27QdYSpcBP-xr1CvZgzBQrOj4AIug8",
#     "yoruba": "13Yl8oO8h8Bp-qd4BGpfaeY5sXLwcjEEFrZUUQ3Ngc2o",
#     "hausa": "13QBRTAJyVGyjdoTjAPa8QoKYdTnGRKeIndVZLoO34xM",
#     "igbo": "1v65uZIAVVSWDdhR4RFyeFVAiWASFVgehG8bJ5bPXLm0"
# }


SHEET_IDS_BY_LANG = {
    "pidgin": "1CIgBxcKNpwphlxhmP7oAmYR2aMyEeRbntZoH_bJJnuw",
    "yoruba": "1ijQahVMs-k0y6Ao3ah6zxYLfZ5x1W4wqcRq_Hg4YwHI",
    "hausa": "1X0Kx-5VIE1fzOAI6UCUu6gZkuAUUM5Kbz52zcDzeaMY",
    "igbo": "1kQOBCH4lSeLtIsAgkZPX6dzc5h-m9ZOgzuA01turGSI"
}

def get_credentials_with_retry(retries=3):
    for i in range(retries):
        try:
            return Credentials.from_service_account_file(creds_dict, scopes=SCOPES)
        except (google.auth.exceptions.TransportError, SSLError) as e:
            print(f"Retrying auth ({i+1}/{retries}): {e}")
            time.sleep(2 ** i)
    raise Exception("Failed to authenticate after retries.")


def fetch_excel_from_github() -> pd.ExcelFile:
    """Download and load the Excel file directly from GitHub."""
    response = requests.get(RAW_FILE_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch file: {response.status_code}")
    return pd.ExcelFile(io.BytesIO(response.content))




def write_sheet_to_workbook(sheet_id: str, df: pd.DataFrame, tab_name: str = "Sheet1"):
    """Write DataFrame to a specific tab in a workbook."""
    credentials = get_credentials_with_retry()
    gc = gspread.authorize(credentials)
    credentials = Credentials.from_service_account_file(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(credentials)

    try:
        worksheet = gc.open_by_key(sheet_id).worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = gc.open_by_key(sheet_id).add_worksheet(title=tab_name, rows="1000", cols="20")

    worksheet.clear()

    if not df.empty:
        worksheet.append_rows(
            [df.columns.tolist()] + df.values.tolist(),
            value_input_option="USER_ENTERED"
        )
    else:
        print(f"⚠️ DataFrame for {sheet_id} is empty, skipping...")


def push_all_audio_summary_sheets_multiple():
    """Push each Excel sheet to its corresponding Google Sheet workbook."""
    excel_data = fetch_excel_from_github()
    all_sheets = pd.read_excel(excel_data, sheet_name=None)

    for lang, df in all_sheets.items():
        sheet_id = SHEET_IDS_BY_LANG.get(lang.lower())
        if not sheet_id:
            print(f"⚠️ No Sheet ID found for language: {lang}, skipping...")
            continue

        print(f"📝 Writing to workbook: {lang} ({len(df)} rows)")
        write_sheet_to_workbook(sheet_id, df, "main")

    print("✅ All sheets written successfully.")





SHEET_ID="1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"

def write_sheet(sheet_name: str, df: pd.DataFrame):
    """Write a DataFrame to Google Sheets in chunks."""
    credentials = Credentials.from_service_account_file(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(get_credentials_with_retry())

    try:
        worksheet = gc.open_by_key(SHEET_ID).worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = gc.open_by_key(SHEET_ID).add_worksheet(title=sheet_name, rows="1000", cols="20")

    worksheet.clear()

    # Add headers
    worksheet.append_rows([df.columns.tolist()], value_input_option="USER_ENTERED")

    # Chunked writing of data rows
    data = df.values.tolist()
    chunk_size = 500
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        worksheet.append_rows(chunk, value_input_option="USER_ENTERED")
        time.sleep(1)  # Prevent rate limit issues


def push_all_audio_summary_sheets():
    excel_data = fetch_excel_from_github()
    all_sheets = pd.read_excel(excel_data, sheet_name=None)  # Dict: {sheet_name: df}

    for lang, df in all_sheets.items():
        sheet_id = SHEET_IDS_BY_LANG.get(lang.lower())
        if not sheet_id:
            print(f"⚠️ No Sheet ID found for language: {lang}, skipping...")
            continue

        print(f"📝 Writing to workbook: {lang} ({len(df)} rows)")
        write_sheet(sheet_id, lang, df)

    print("✅ All sheets written successfully.")

