import os
import io
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import base64
import json 

load_dotenv()

# GitHub setup
TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
BASE_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/annotators"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/annotators"
HEADERS = {"Authorization": f"token {TOKEN}"}

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"
SHEET_NAME = "annotated_count_summary"
# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "audios_count.json")

b64_creds = os.getenv("GOOGLE_CREDS_B64")

if not b64_creds:
    raise Exception("Missing GOOGLE_CREDS_B64 in environment.")

creds_dict = json.loads(base64.b64decode(b64_creds).decode("utf-8"))



def parse_tsv(folder_name):
    """Parse assigned_data.tsv for an annotator folder."""
    url = f"{RAW_BASE}/{folder_name}/assigned_data.tsv"
    print(f"📥 Fetching TSV: {url}")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # will raise an error for 404, etc.

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
            "invalid": int(invalid),
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
        


# 📊 Collect stats for each annotator
def get_folder_stats():
    result = []
    res = requests.get(BASE_API, headers=HEADERS)
    if res.status_code != 200:
        print("❌ Failed to fetch annotator folders")
        return []

    folders = res.json()
    for folder in folders:
        if folder["type"] == "dir":
            name = folder["name"]
            print(f"📁 Processing {name}...")
            tsv_stats = parse_tsv(name)

            result.append({
                "annotator": name,
                "total": tsv_stats["total_rows"],
                "presented": tsv_stats["presented"],
                "recorded": tsv_stats["recorded"],
                "invalid": tsv_stats["invalid"]
            })

    return result







def write_summary_to_sheet(data):
    creds = Credentials.from_service_account_file(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    headers = ["Annotator", "Total Sentences", "Presented", "Recorded", "Invalid"]

    rows = []
    for row in data:
        annotator = row.get("annotator", "")
        total = row.get("total", 0) 
        presented = row.get("presented", 0)
        recorded = row.get("recorded", 0)
        invalid = row.get("invalid", 0)

        print("This is great: ", annotator, total, presented, recorded, invalid)
        rows.append([annotator, total, presented, recorded, invalid])

    sheet.batch_clear(["A1:E1000"])
    sheet.update("A1", [headers] + rows, value_input_option="USER_ENTERED")



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
