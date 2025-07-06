from fastapi import APIRouter, HTTPException
import os, io, time, requests
import pandas as pd
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.auth.exceptions import TransportError
from requests.exceptions import SSLError

load_dotenv()

hourly = APIRouter()

# CONFIG
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
EXCEL_URL = "https://raw.githubusercontent.com/lawallanre00490038/dsn-voice/main/reports/current_annotators_report.xlsx"
SHEET_ID = "1JW8mRPgOZ8xIgwq4EKvfd-uILPQCZCdfFgsJqDJ5Zmc"
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "audios_count.json")
SHEET_NAME = "hourly_summary"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]





# def fetch_excel_from_github():
#     headers = {"Authorization": f"token {GITHUB_TOKEN}"}
#     response = requests.get(EXCEL_URL, headers=headers)

#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="❌ Failed to fetch Excel from GitHub")

#     try:
#         df = pd.read_excel(io.BytesIO(response.content), sheet_name="read")
#         print("🧪 Columns in fetched Excel:", df.columns.tolist())

#         cols = df.columns.tolist()

#         if len(cols) != 2:
#             raise HTTPException(status_code=500, detail=f"❌ Unexpected column count. Got: {cols}")

#         annotator_col = cols[0]
#         timestamp_header = cols[1]

#         df = df.rename(columns={
#             annotator_col: "annotator",
#             timestamp_header: "count"
#         })
#         df["timestamp"] = timestamp_header

#         return df[["annotator", "timestamp", "count"]]

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"❌ Failed to parse Excel: {str(e)}")

    

def fetch_excel_from_github():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(EXCEL_URL, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="❌ Failed to fetch Excel from GitHub")

    try:
        # Read both sheets
        read_df = pd.read_excel(io.BytesIO(response.content), sheet_name="read")
        unread_df = pd.read_excel(io.BytesIO(response.content), sheet_name="unread")

        # Extract timestamp column name
        timestamp = read_df.columns[1]
        
        # Rename columns
        read_df.columns = ["annotator", "read_count"]
        read_df.insert(1, "timestamp", timestamp)

        unread_df.columns = ["annotator", "unread_count"]
        unread_df.insert(1, "timestamp", timestamp)

        # Merge on annotator
        df = pd.merge(read_df, unread_df, on=["annotator", "timestamp"], how="outer").fillna(0)

        # Cast to int
        df["read_count"] = df["read_count"].astype(int)
        df["unread_count"] = df["unread_count"].astype(int)

        return df

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to parse Excel: {str(e)}")



def get_credentials_with_retry(retries=3):
    for i in range(retries):
        try:
            return Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        except (TransportError, SSLError) as e:
            print(f"Retrying Google auth ({i+1}/{retries}) due to: {e}")
            time.sleep(2 ** i)
    raise HTTPException(status_code=500, detail="❌ Failed to authenticate with Google Sheets.")


def write_sheet(sheet_name: str, df: pd.DataFrame):
    creds = get_credentials_with_retry()
    gc = gspread.authorize(creds)

    try:
        worksheet = gc.open_by_key(SHEET_ID).worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = gc.open_by_key(SHEET_ID).add_worksheet(title=sheet_name, rows="1000", cols="20")

    worksheet.clear()
    worksheet.append_rows([df.columns.tolist()], value_input_option="USER_ENTERED")

    chunk_size = 500
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size].values.tolist()
        worksheet.append_rows(chunk, value_input_option="USER_ENTERED")
        time.sleep(1)  # Avoid rate limit




@hourly.get("/hourly-summary")
def get_hourly_summary():
    df = fetch_excel_from_github()

    # Push to sheet
    write_sheet(SHEET_NAME, df)

    # Return as JSON
    result = df.to_dict(orient="records")
    return result

