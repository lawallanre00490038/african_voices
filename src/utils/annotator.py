import os
import io
import requests
import pandas as pd
import gspread
from fastapi import HTTPException
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv
from src.utils.credentials import get_credentials_with_retry

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
BASE_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/annotators"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/annotators"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1.5), retry=retry_if_exception_type(Exception))
def safe_get(url, headers=None):
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res


def get_github_folders():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = safe_get(BASE_API, headers=headers)
    return [f["name"] for f in res.json() if f["type"] == "dir"]


def read_csv_from_github(annotator, file_name):
    url = f"{RAW_BASE}/{annotator}/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = safe_get(url, headers=headers)
        if file_name.endswith(".tsv"):
            df = pd.read_csv(io.StringIO(res.text), sep="\t")
        else:
            df = pd.read_csv(io.StringIO(res.text))
        df["annotator"] = annotator
        return df
    except Exception as e:
        print(f"⚠️ Skipping {annotator}/{file_name}: {e}")
        return None


def fetch_annotator_data():
    folders = get_github_folders()
    assigned_data = []
    recording_stats = []

    for annotator in folders:
        print("Fetching data for", annotator)
        assigned_df = read_csv_from_github(annotator, "assigned_data.tsv")
        stats_df = read_csv_from_github(annotator, "recording_stats.csv")

        if assigned_df is not None and not assigned_df.empty:
            assigned_data.append(assigned_df)
        if stats_df is not None and not stats_df.empty:
            recording_stats.append(stats_df)

    return assigned_data, recording_stats


def write_to_google_sheet(sheet_name: str, df: pd.DataFrame):
    if df.empty:
        print(f"⚠️ Skipping sheet '{sheet_name}' because DataFrame is empty.")
        return

    creds = get_credentials_with_retry()
    client = gspread.authorize(creds)

    try:
        worksheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = client.open_by_key(SHEET_ID).add_worksheet(title=sheet_name, rows="1000", cols="20")

    worksheet.clear()

    # Sanitize and write data
    cleaned_df = df.fillna("").infer_objects(copy=False)
    try:
        worksheet.append_rows(
            [cleaned_df.columns.tolist()] + cleaned_df.astype(str).values.tolist(),
            value_input_option="USER_ENTERED"
        )
        print(f"✅ Updated sheet: {sheet_name}")
    except Exception as e:
        print(f"❌ Failed to update sheet {sheet_name}: {e}")


def push_annotators_to_sheet():
    assigned_data, recording_stats = fetch_annotator_data()

    if not assigned_data and not recording_stats:
        raise HTTPException(status_code=404, detail="No valid data found.")

    if assigned_data:
        all_assigned = pd.concat(assigned_data, ignore_index=True)
        write_to_google_sheet("assigned_data", all_assigned)

    if recording_stats:
        all_stats = pd.concat(recording_stats, ignore_index=True)
        write_to_google_sheet("recording_stats", all_stats)

    return {"message": "Sheets updated successfully"}
