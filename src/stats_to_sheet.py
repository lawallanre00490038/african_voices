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
    Fetch latest stats.csv from GitHub and write to Google Sheet tab named after the language.
    """

    for language in ["pidgin", "yoruba", "igbo", "hausa"]:

        # Step 1: List folders inside reports/{language}
        sub_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/reports/{language}"
        try:
            res = requests.get(sub_url, headers=HEADERS)
            res.raise_for_status()
            folders = [f["name"] for f in res.json() if f["type"] == "dir"]
            if not folders:
                raise HTTPException(status_code=404, detail=f"No date folders found for language '{language}'")
            latest_date = sorted(folders, reverse=True)[0]
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Could not fetch folders for language '{language}': {str(e)}")

        # Step 2: Use latest folder to fetch stats.csv
        csv_url = f"{RAW_BASE}/{language}/{latest_date}/stats.csv"
        try:
            res = requests.get(csv_url, headers=HEADERS)
            res.raise_for_status()
            df = pd.read_csv(io.StringIO(res.text))
            df["language"] = language
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to fetch data for language '{language}' on date '{latest_date}': {str(e)}"
            )

        # Step 3: Push to Google Sheet (create worksheet if missing)
        try:
            worksheet_titles = [ws.title for ws in sheet.worksheets()]
            if language not in worksheet_titles:
                sheet.add_worksheet(title=language, rows="1000", cols="20")

            ws = sheet.worksheet(language)
            ws.clear()

            # Set header and values
            ws.update([df.columns.values.tolist()] + df.values.tolist())
            return {"status": "success", "message": f"Data pushed to Google Sheet tab '{language}'"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write to Google Sheet: {str(e)}")
