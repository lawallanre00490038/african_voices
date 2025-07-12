import base64
import json 
import os, json, io, base64, time
import requests
import pandas as pd
from dotenv import load_dotenv
import gspread
from src.utils.credentials import get_credentials_with_retry
from gspread.exceptions import APIError, WorksheetNotFound
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables
load_dotenv()

# GitHub settings
TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
BASE_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/annotators"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/annotators"
HEADERS = {"Authorization": f"token {TOKEN}"}

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_IDS = [
    "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc",
    "1_GoSkWDpW-cfosDDSRTCsJYZyz1rR-wCSl4O3sif69s",
]

SHEET_NAME = "annotated_count_summary"



# Retry wrappers
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1.5), retry=retry_if_exception_type(Exception))
def safe_get(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2), retry=retry_if_exception_type(APIError))
def safe_update(worksheet, headers, rows):
    worksheet.batch_clear(["A1:E1000"])
    worksheet.update("A1", [headers] + rows, value_input_option="USER_ENTERED")



@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2), retry=retry_if_exception_type(Exception))
def safe_authorize():
    creds = get_credentials_with_retry()
    return gspread.authorize(creds)

# 📥 Parse individual annotator TSV
def parse_tsv(folder_name):
    url = f"{RAW_BASE}/{folder_name}/assigned_data.tsv"
    print(f"📥 Fetching TSV: {url}")
    try:
        response = safe_get(url)
        df = pd.read_csv(io.StringIO(response.text), sep="\t")

        total = len(df)
        presented = df['presented'].sum() if 'presented' in df else 0
        recorded = df['recorded'].sum() if 'recorded' in df else 0
        invalid = df['invalid'].sum() if 'invalid' in df else 0

        print(f"✅ Parsed {folder_name} with {total} rows")
        return {
            "total_rows": int(total),
            "presented": int(presented),
            "recorded": int(recorded),
            "invalid": int(invalid)
        }

    except Exception as e:
        print(f"❌ Failed to parse {folder_name}: {e}")
        return {
            "total_rows": 0,
            "presented": 0,
            "recorded": 0,
            "invalid": 0,
            "error": str(e)
        }


# 📊 Collect stats from all annotator folders
def get_folder_stats():
    try:
        res = safe_get(BASE_API)
        folders = res.json()
    except Exception as e:
        print("❌ Failed to fetch annotator folders:", e)
        return []

    result = []
    for folder in folders:
        if folder.get("type") == "dir":
            name = folder["name"]
            print(f"📁 Processing {name}...")
            stats = parse_tsv(name)

            result.append({
                "annotator": name,
                "total": stats["total_rows"],
                "presented": stats["presented"],
                "recorded": stats["recorded"],
                "invalid": stats["invalid"]
            })

    return result


# ✅ Write stats to Google Sheets
def write_summary_to_sheet(data):
    for SHEET_ID in SHEET_IDS:
        try:
            client = safe_authorize()
            sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        except WorksheetNotFound:
            sheet = client.open_by_key(SHEET_ID).add_worksheet(title=SHEET_NAME, rows="1000", cols="5")
        except Exception as e:
            print(f"❌ Could not access sheet: {e}")
            return

        headers = ["Annotator", "Total Sentences", "Presented", "Recorded", "Invalid"]
        rows = []

        for row in data:
            annotator = row.get("annotator", "")
            total = row.get("total", 0)
            presented = row.get("presented", 0)
            recorded = row.get("recorded", 0)
            invalid = row.get("invalid", 0)

            print("✅ Row:", annotator, total, presented, recorded, invalid)
            rows.append([annotator, total, presented, recorded, invalid])

        try:
            safe_update(sheet, headers, rows)
            print("✅ Sheet updated successfully.")
        except Exception as e:
            print(f"❌ Failed to update sheet: {e}")
















def calculate_average_time_for_completed():
    url = "https://african-voices-dashboard.onrender.com/stats-json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    completed = []
    total_time = 0
    count = 0

    for record in data:
        if record.get("Files Read") == 600 and record.get("Remaining Texts") == 0:
            minutes = record.get("Minutes Recorded", 0)
            avg_min = round(minutes / 600, 4)
            avg_sec = round(avg_min * 60, 2)

            completed.append({
                "ID": record.get("ID"),
                "Name": record.get("Name"),
                "Minutes Recorded": minutes,
                "avg_time_per_sentence_min": avg_min,
                "avg_time_per_sentence_sec": avg_sec,
                "language": record.get("language")
            })

            total_time += avg_sec
            count += 1

    overall_avg = round(total_time / count, 2) if count > 0 else None

    return {
        "completed_annotators": completed,
        "overall_avg_time_per_sentence_sec": overall_avg
    }
