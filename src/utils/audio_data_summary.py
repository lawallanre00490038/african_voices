import os
import io
import pandas as pd
import requests
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import time
from requests.exceptions import SSLError
import numpy as np
import os, io, requests, json
import pandas as pd
from typing import List
import gspread, time
from requests.exceptions import SSLError
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from src.utils.credentials import get_credentials_with_retry
import time
import numpy as np
import gspread
from google.auth.exceptions import TransportError
from gspread.exceptions import APIError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type


# Load environment variables
load_dotenv()

# Google Sheets settings
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "audios_count.json")


# GitHub settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
RAW_FILE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/reports/audio_data_summary.xlsx"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


SHEET_ID="1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"

SHEET_IDS_BY_LANG = {
    "pidgin": "1CIgBxcKNpwphlxhmP7oAmYR2aMyEeRbntZoH_bJJnuw",
    "yoruba": "1ijQahVMs-k0y6Ao3ah6zxYLfZ5x1W4wqcRq_Hg4YwHI",
    "hausa": "1X0Kx-5VIE1fzOAI6UCUu6gZkuAUUM5Kbz52zcDzeaMY",
    "igbo": "1kQOBCH4lSeLtIsAgkZPX6dzc5h-m9ZOgzuA01turGSI"
}



def fetch_excel_from_github() -> pd.ExcelFile:
    """Download and load the Excel file directly from GitHub."""
    response = requests.get(RAW_FILE_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch file: {response.status_code}")
    return pd.ExcelFile(io.BytesIO(response.content))



@retry(
    retry=retry_if_exception_type(APIError),
    wait=wait_exponential(multiplier=2, min=4, max=20),
    stop=stop_after_attempt(5),
)
def append_chunk(worksheet, chunk):
    worksheet.append_rows(chunk, value_input_option="USER_ENTERED")

def write_sheet_to_workbook(sheet_id: str, df: pd.DataFrame, tab_name: str = "Sheet1"):
    """Write DataFrame to a specific tab in a workbook with retry + chunking."""
    credentials = get_credentials_with_retry()
    gc = gspread.authorize(credentials)

    try:
        worksheet = gc.open_by_key(sheet_id).worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = gc.open_by_key(sheet_id).add_worksheet(title=tab_name, rows="1000", cols="20")

    worksheet.clear()

    if df.empty:
        print(f"⚠️ DataFrame for {sheet_id} is empty, skipping...")
        return

    df = df.replace({np.nan: ""})  # Avoid NaNs that break JSON
    header = [df.columns.tolist()]
    data_rows = df.values.tolist()

    print("📤 Appending header...")
    append_chunk(worksheet, header)

    chunk_size = 5000
    for i in range(0, len(data_rows), chunk_size):
        chunk = data_rows[i:i + chunk_size]
        try:
            print(f"📤 Appending rows {i} to {i + len(chunk)}...")
            append_chunk(worksheet, chunk)
            time.sleep(1.5)  # Optional: pause to avoid quota hit
        except APIError as e:
            print(f"❌ Failed to append rows {i}-{i+len(chunk)}: {e}")
            raise

    print("✅ Finished writing to sheet.")




def push_all_audio_summary_sheets_multiple():
    """Push each Excel sheet to its corresponding Google Sheet workbook."""
    excel_data = fetch_excel_from_github()
    all_sheets = pd.read_excel(excel_data, sheet_name=None)

    for lang, df in all_sheets.items():
        sheet_id = SHEET_IDS_BY_LANG.get(lang.lower())
        print("The sheet id is:", sheet_id, lang, df.columns)
        if not sheet_id:
            print(f"⚠️ No Sheet ID found for language: {lang}, skipping...")
            continue

        print(f"📝 Writing to workbook: {lang} ({len(df)} rows)")
        write_sheet_to_workbook(sheet_id, df, "main")

        push_all_audio_summary_sheets()

    print("✅ All sheets written successfully.")





def push_all_audio_summary_sheets():
    excel_data = fetch_excel_from_github()
    all_sheets = pd.read_excel(excel_data, sheet_name=None)

    for lang, df in all_sheets.items():
        if not SHEET_ID:
            print(f"⚠️ No Sheet ID found for language: {lang}, skipping...")
            continue

         # Mine
        print(f"📝 Writing {len(df)} rows to tab: {lang}")
        write_sheet_to_workbook(SHEET_ID, df, lang.lower())


        
    print("✅ All sheets written successfully.")
    return("✅ All sheets written successfully.")

