from fastapi import APIRouter, HTTPException
import os, io, time, requests
import pandas as pd
import gspread
import re
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from src.utils.credentials import get_credentials_with_retry

import numpy as np

load_dotenv()

hourly = APIRouter()

# CONFIG
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
EXCEL_URL = "https://raw.githubusercontent.com/lawallanre00490038/dsn-voice/main/reports/current_annotators_report.xlsx"
SHEET_IDS = [
    "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc",
    "1_GoSkWDpW-cfosDDSRTCsJYZyz1rR-wCSl4O3sif69s",
]


# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "audios_count.json")


SHEET_NAME = "hourly_summary"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]



def fetch_excel_from_github():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(EXCEL_URL, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="❌ Failed to fetch Excel from GitHub")

    try:
        # Read read and unread sheets
        read_df = pd.read_excel(io.BytesIO(response.content), sheet_name="read")
        unread_df = pd.read_excel(io.BytesIO(response.content), sheet_name="unread")

        # Check column shape
        if read_df.shape[1] < 2 or unread_df.shape[1] < 2:
            raise HTTPException(status_code=500, detail="❌ 'read' or 'unread' sheet has insufficient columns")

        # Extract annotator column
        annotator_col = read_df.columns[0]

        # Melt both sheets to long format (timestamp -> rows)
        read_long = read_df.melt(id_vars=[annotator_col], var_name="timestamp", value_name="read_count")
        unread_long = unread_df.melt(id_vars=[annotator_col], var_name="timestamp", value_name="unread_count")

        # Merge long-form data
        df_long = pd.merge(read_long, unread_long, on=[annotator_col, "timestamp"], how="outer").fillna(0)

        # Rename 'annotator' column explicitly
        df_long = df_long.rename(columns={annotator_col: "annotator"})

        # Ensure numeric columns are of int type
        df_long["read_count"] = df_long["read_count"].astype(int)
        df_long["unread_count"] = df_long["unread_count"].astype(int)

        # Create wide format from read_df (optional, for hourly analysis)
        wide_df = read_df.copy()
        wide_df = wide_df.rename(columns={annotator_col: "annotator"})

        return df_long, read_df, unread_df, wide_df

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to parse Excel: {str(e)}")


def write_sheet(sheet_name: str, df: pd.DataFrame):
    creds = get_credentials_with_retry()
    gc = gspread.authorize(creds)

    for SHEET_ID in SHEET_IDS:
        try:
            worksheet = gc.open_by_key(SHEET_ID).worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = gc.open_by_key(SHEET_ID).add_worksheet(title=sheet_name, rows="1000", cols="20")

        worksheet.clear()
        worksheet.append_rows([df.columns.tolist()], value_input_option="USER_ENTERED")

        # ✅ Clean all data before pushing
        df = df.replace({np.nan: ""}).fillna("")  # Remove NaNs and None safely

        chunk_size = 500
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size].values.tolist()
            worksheet.append_rows(chunk, value_input_option="USER_ENTERED")
            time.sleep(1)  # Avoid rate limit



def get_latest_hour_summary(read_df: pd.DataFrame, unread_df: pd.DataFrame, wide_df: pd.DataFrame) -> dict:
    # Rename first column to 'annotator' if needed
    if read_df.columns[0] != "annotator":
        read_df.rename(columns={read_df.columns[0]: "annotator"}, inplace=True)
    if unread_df.columns[0] != "annotator":
        unread_df.rename(columns={unread_df.columns[0]: "annotator"}, inplace=True)

    # Identify timestamp columns (excluding 'annotator')
    hour_cols = [col for col in read_df.columns if col != "annotator"]
    if not hour_cols:
        raise ValueError("❌ No hourly timestamp columns found.")

    # Sort to find latest timestamp column
    latest_hour_col = sorted(hour_cols)[-1]

    # Get sentence counts for latest hour
    latest_read_sentences = read_df[latest_hour_col].fillna(0).astype(int).sum()
    latest_unread_sentences = unread_df[latest_hour_col].fillna(0).astype(int).sum()

    # Compute total sentences and convert read_sentences to hours
    total_sentences = latest_read_sentences + latest_unread_sentences
    latest_total_hours = round(latest_read_sentences * 8 / 3600, 2)

    # Count active and inactive annotators from the READ sheet only
    active_df = read_df[read_df[latest_hour_col] > 0]
    inactive_df = read_df[read_df[latest_hour_col] == 0]

    active_annotators = active_df["annotator"].nunique()
    inactive_annotators = inactive_df["annotator"].nunique()
    total_annotators = read_df["annotator"].nunique()

    # Get list of inactive annotator names
    inactive_annotator_list = inactive_df["annotator"].tolist()

    return {
        "latest_hour": latest_hour_col,
        "latest_total_sentences": int(total_sentences),
        "latest_read_sentences": int(latest_read_sentences),
        "latest_unread_sentences": int(latest_unread_sentences),
        "latest_total_hours": latest_total_hours,
        "Total_annotators": total_annotators,
        "active_annotators": active_annotators,
        "inactive_annotators": inactive_annotators,
        "list_of_inactive_annotators": inactive_annotator_list,

    }



@hourly.get("/hourly-summary")
def get_hourly_summary():
    df_long, read_df, unread_df, wide_df = fetch_excel_from_github()

    write_sheet("hourly_summary_read", read_df)
    write_sheet("hourly_summary_unread", unread_df)

    latest_summary = get_latest_hour_summary(read_df, unread_df, wide_df)

    return {
        "latest_hour_summary": {
            k: v for k, v in latest_summary.items() if k != "list_of_inactive_annotators"
        },
        "list_of_inactive_annotators": latest_summary["list_of_inactive_annotators"],
        "records": df_long.to_dict(orient="records"),
    }



@hourly.get("/hourly-summary-read")
def get_hourly_summary_read():
    _, read_df, _, _ = fetch_excel_from_github()

    if read_df.columns[0] != "Annotator":
        read_df.rename(columns={read_df.columns[0]: "Annotator"}, inplace=True)

    # Replace NaN with None
    read_df = read_df.replace({np.nan: None})

    # Convert float columns to object (optional but ensures JSON compliance)
    for col in read_df.columns:
        if read_df[col].dtype == float:
            read_df[col] = read_df[col].astype(object)

    return (read_df.to_dict(orient="records"))



@hourly.get("/hourly-summary-unread")
def get_hourly_summary_unread():
    _, _, unread_df, _ = fetch_excel_from_github()

    if unread_df.columns[0] != "Annotator":
        unread_df.rename(columns={unread_df.columns[0]: "Annotator"}, inplace=True)

    unread_df = unread_df.replace({np.nan: None})

    for col in unread_df.columns:
        if unread_df[col].dtype == float:
            unread_df[col] = unread_df[col].astype(object)

    return (unread_df.to_dict(orient="records"))
