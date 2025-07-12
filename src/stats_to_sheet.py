import requests
import pandas as pd
import io, os
import gspread
from fastapi import APIRouter, HTTPException
from src.utils.credentials import get_credentials_with_retry


stats_router = APIRouter()

# Google Sheets settings
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# GitHub settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/reports"

SPREADSHEET_ID = '1_GoSkWDpW-cfosDDSRTCsJYZyz1rR-wCSl4O3sif69s'

credentials = get_credentials_with_retry()
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID)


@stats_router.get("/stats-to-sheet", tags=["Completed Task Google Sheets"])
def push_language_stats_to_sheet():
    """
    Push latest stats.csv from GitHub to Google Sheet tabs (one per language).
    Overwrites each tab and adds 'date' column.
    """
    result_summary = []

    for language in ["pidgin", "yoruba", "igbo", "hausa"]:
        try:
            # 1. List folders in reports/{language}
            folder_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/reports/{language}"
            folder_res = requests.get(folder_url, headers=HEADERS)
            folder_res.raise_for_status()

            folders = [f["name"] for f in folder_res.json() if f["type"] == "dir"]
            if not folders:
                raise Exception(f"No folders found for {language}")

            latest_date = sorted(folders, reverse=True)[0]

            # 2. Fetch the latest stats.csv
            csv_url = f"{RAW_BASE}/{language}/{latest_date}/stats.csv"
            csv_res = requests.get(csv_url, headers=HEADERS)
            csv_res.raise_for_status()

            df = pd.read_csv(io.StringIO(csv_res.text))
            df["language"] = language
            # df["date"] = pd.to_datetime(latest_date, format="%Y%m%d").dt.strftime("%Y-%m-%d")
            df["date"] = pd.to_datetime(latest_date, format="%Y%m%d").strftime("%Y-%m-%d")

            # 3. Push to Google Sheet
            worksheet_titles = [ws.title for ws in sheet.worksheets()]
            if language not in worksheet_titles:
                sheet.add_worksheet(title=language, rows="1000", cols="20")

            ws = sheet.worksheet(language)
            ws.clear()
            ws.update([df.columns.values.tolist()] + df.values.tolist())

            result_summary.append({
                "language": language,
                "status": "success",
                "message": f"{len(df)} rows pushed to '{language}' tab",
                "date": latest_date
            })

        except Exception as e:
            result_summary.append({
                "language": language,
                "status": "error",
                "message": str(e)
            })

    return result_summary
