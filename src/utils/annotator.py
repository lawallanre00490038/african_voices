# import os
# import requests
# import pandas as pd
# import gspread
# import io
# from google.oauth2.service_account import Credentials
# from fastapi import APIRouter, HTTPException

# from dotenv import load_dotenv

# load_dotenv()

# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# REPO_OWNER = "lawallanre00490038"
# REPO_NAME = "dsn-voice"
# BASE_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/annotators"
# RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/annotators"

# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# SHEET_ID = "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"
# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "audios_count.json")

# router = APIRouter()

# def get_github_folders():
#     headers = {"Authorization": f"token {GITHUB_TOKEN}"}
#     res = requests.get(BASE_API, headers=headers)
#     res.raise_for_status()
#     return [f["name"] for f in res.json() if f["type"] == "dir"]


# def read_csv_from_github(annotator, file_name):
#     url = f"{RAW_BASE}/{annotator}/{file_name}"
#     headers = {"Authorization": f"token {GITHUB_TOKEN}"}
#     try:
#         res = requests.get(url, headers=headers)
#         res.raise_for_status()
#         if file_name.endswith(".tsv"):
#             df = pd.read_csv(io.StringIO(res.text), sep="\t")
#         else:
#             df = pd.read_csv(io.StringIO(res.text))
#         df["annotator"] = annotator
#         return df
#     except requests.HTTPError as e:
#         if e.response.status_code == 404:
#             print(f"🔸 Skipping {annotator}: {file_name} not found.")
#         else:
#             print(f"❌ Error reading {file_name} for {annotator}: {e}")
#         return None
#     except Exception as e:
#         print(f"❌ Failed to parse {file_name} for {annotator}: {e}")
#         return None


# def write_to_google_sheet(sheet_name: str, df: pd.DataFrame):
#     creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     client = gspread.authorize(creds)

#     try:
#         worksheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
#     except gspread.exceptions.WorksheetNotFound:
#         worksheet = client.open_by_key(SHEET_ID).add_worksheet(title=sheet_name, rows="1000", cols="20")

#     worksheet.clear()
#     worksheet.append_rows([df.columns.tolist()] + df.values.tolist(), value_input_option="USER_ENTERED")


# def fetch_all_annotator_data():
#     folders = get_github_folders()
#     tsv_combined = []
#     stats_combined = []

#     for annotator in folders:
#         assigned_df = read_csv_from_github(annotator, "assigned_data.tsv")
#         stats_df = read_csv_from_github(annotator, "recording_stats.csv")

#         if assigned_df is not None:
#             tsv_combined.append(assigned_df)
#         if stats_df is not None:
#             stats_combined.append(stats_df)

#     if not tsv_combined and not stats_combined:
#         raise HTTPException(status_code=404, detail="No valid CSV data found.")

#     final_result = {}

#     if tsv_combined:
#         all_tsv_df = pd.concat(tsv_combined, ignore_index=True)
#         print("\n\n", all_tsv_df, "\n\n")
#         write_to_google_sheet("assigned_data", all_tsv_df)
#         final_result["assigned_data"] = all_tsv_df.to_dict(orient="records")

#     if stats_combined:
#         all_stats_df = pd.concat(stats_combined, ignore_index=True)
#         write_to_google_sheet("recording_stats", all_stats_df)
#         final_result["recording_stats"] = all_stats_df.to_dict(orient="records")

#     return final_result



# src/routes/json_output.py


import os
import requests
import pandas as pd
import gspread
import io
from google.oauth2.service_account import Credentials
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
BASE_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/annotators"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/annotators"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "audios_count.json")



def get_github_folders():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(BASE_API, headers=headers)
    res.raise_for_status()
    return [f["name"] for f in res.json() if f["type"] == "dir"]

def read_csv_from_github(annotator, file_name):
    url = f"{RAW_BASE}/{annotator}/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        if file_name.endswith(".tsv"):
            df = pd.read_csv(io.StringIO(res.text), sep="\t")
        else:
            df = pd.read_csv(io.StringIO(res.text))
        df["annotator"] = annotator
        return df
    except Exception as e:
        print(f"⚠️ Skipping {annotator}/{file_name}: {e}")
        return None


def get_annotators_json():
    assigned_data, recording_stats = fetch_annotator_data()
    if not assigned_data and not recording_stats:
        raise HTTPException(status_code=404, detail="No data found.")

    result = []

    if assigned_data:
        all_assigned = pd.concat(assigned_data, ignore_index=True)
        result += all_assigned.to_dict(orient="records")

    if recording_stats:
        all_stats = pd.concat(recording_stats, ignore_index=True)
        result += all_stats.to_dict(orient="records")

    return result


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








def get_github_folders():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(BASE_API, headers=headers)
    res.raise_for_status()
    return [f["name"] for f in res.json() if f["type"] == "dir"]

def read_csv_from_github(annotator, file_name):
    url = f"{RAW_BASE}/{annotator}/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
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
        assigned_df = read_csv_from_github(annotator, "assigned_data.tsv")
        stats_df = read_csv_from_github(annotator, "recording_stats.csv")

        if assigned_df is not None:
            assigned_data.append(assigned_df)
        if stats_df is not None:
            recording_stats.append(stats_df)

    return assigned_data, recording_stats




def write_to_google_sheet(sheet_name: str, df: pd.DataFrame):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    try:
        worksheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = client.open_by_key(SHEET_ID).add_worksheet(title=sheet_name, rows="1000", cols="20")

    worksheet.clear()

    # Convert all to strings, fill NaNs with empty string
    cleaned_df = df.fillna("")
    worksheet.append_rows(
        [cleaned_df.columns.tolist()] + cleaned_df.values.tolist(),
        value_input_option="USER_ENTERED"
    )


def push_annotators_to_sheet():
    folders = get_github_folders()
    assigned_data = []
    recording_stats = []

    for annotator in folders:
        assigned_df = read_csv_from_github(annotator, "assigned_data.tsv")
        stats_df = read_csv_from_github(annotator, "recording_stats.csv")

        if assigned_df is not None:
            assigned_data.append(assigned_df)
        if stats_df is not None:
            recording_stats.append(stats_df)

    if not assigned_data and not recording_stats:
        raise HTTPException(status_code=404, detail="No valid data found.")

    if assigned_data:
        all_assigned = pd.concat(assigned_data, ignore_index=True)
        write_to_google_sheet("assigned_data", all_assigned)

    if recording_stats:
        all_stats = pd.concat(recording_stats, ignore_index=True)
        write_to_google_sheet("recording_stats", all_stats)

    return {"message": "Sheets updated successfully"}
