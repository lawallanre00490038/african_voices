from fastapi import Request, Header, HTTPException, APIRouter, Depends
from dotenv import load_dotenv
import subprocess
import hmac
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pathlib import Path
import hashlib
import os
import pandas as pd
import requests
import io
from datetime import datetime
import pandas as pd
from src.utils.audio_data_summary import  push_all_audio_summary_sheets, push_all_audio_summary_sheets_multiple
from src.db import get_session
from src.models import AnnotatorStat
from src.process_data import update_or_create_language_stat, process_all_languages
from src.utils.trigger_webhook import trigger_github_webhook
from src.utils.count_summary import get_folder_stats, write_summary_to_sheet
from src.utils.annotator import get_annotators_json, push_annotators_to_sheet

load_dotenv()
# Load from .env
GITHUB_SECRET =  os.getenv("GITHUB_TOKEN")
REPO_PATH = Path(os.getenv("REPO_PATH", "./dsn-voice")).resolve()
REPO_URL = "https://github.com/abumafrim/dsn-voice.git"


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"

CSV_PATH = "data/annotator_status.csv"
annotator_status_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{CSV_PATH}"
get_registered_annotators_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/data/registered_annotators.csv"





github_router = APIRouter()

@github_router.post("/github-webhook", include_in_schema=False)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    db: AsyncSession = Depends(get_session)
):
    print("🚀 Webhook endpoint hit")
    print("\n\n\n")
    print("This is the request headers:", request.headers)

    if not x_hub_signature_256:
        raise HTTPException(status_code=400, detail="Missing X-Hub-Signature-256 header")
    
    payload = await request.body()

    # 🔐 Signature Verification
    computed_signature = 'sha256=' + hmac.new(GITHUB_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    print("⚠️  Received signature:", x_hub_signature_256)
    print("✅ Computed signature:", computed_signature)
    print("🧾 Payload received:", payload.decode())

    if not hmac.compare_digest(computed_signature, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 🔄 Clone or Pull Repo
    if not REPO_PATH.exists():
        print(f"📥 Cloning repository into {REPO_PATH}...")
        subprocess.run([
            "git", "clone", "--filter=blob:none", "--no-checkout",
            REPO_URL, str(REPO_PATH)
        ], check=True)
        subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=REPO_PATH, check=True)
        subprocess.run(["git", "sparse-checkout", "set", "reports"], cwd=REPO_PATH, check=True)

        # ✅ This ensures the reports/ folder is actually checked out
        subprocess.run(["git", "checkout", "main"], cwd=REPO_PATH, check=True)

    print(f"🔄 Pulling latest changes into {REPO_PATH}...")

    try:
        print("🔄 Starting pull...")
        subprocess.run(["git", "pull"], cwd=REPO_PATH, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Git pull failed: {e}")

    # 📊 Process data
    report_path = REPO_PATH / "reports"
    annotators = process_all_languages(report_path)

    for a in annotators:
        await update_or_create_language_stat(db, a.language, a.dict(exclude={"id"}))

    await db.commit()

    return {
        "message": "Update successful",
        "total_annotators": len(annotators),
        "languages": list(set([a.language for a in annotators]))
    }



@github_router.get("/trigger-webhook-to-pull")
async def trigger():
    result = trigger_github_webhook()
    print("✅ Webhook response:", result)
    return result



@github_router.get("/google_sheet_count_summary", tags=["Count Google Sheets"])
def update_annotator_summary():
    data = get_folder_stats()
    write_summary_to_sheet(data)
    return {"status": "success", "data": data}


# @github_router.get("/google_sheet_count-audio", tags=["Count Google Sheets"])
# def get_audio_analytics():
#     data = count_audio_files_deep()
#     write_to_sheet(data)
#     return data



AUDIO_SUMMARY_PATH = REPO_PATH / "reports" / "audio_data_summary.xlsx"
@github_router.post("/audio_data_summary_to_sheets", tags=["Completed Task Google Sheets"])
async def push_audio_summary_to_sheets():
    """
        Fetches the latest audio_data_summary.xlsx directly from GitHub,
        parses all language sheets, and writes them to Google Sheets.
    """
    try:
        push_all_audio_summary_sheets()
        return {"message": "✅ Google Sheets updated for all languages via GitHub"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



AUDIO_SUMMARY_PATH = REPO_PATH / "reports" / "audio_data_summary.xlsx"
@github_router.post("/audio_data_summary_to_multiple_sheets", tags=["Completed Task Google Sheets"])
async def push_audio_summary_to_multiple_sheets():
    """Pushes language-specific audio data to individual Google Sheets."""
    try:
        push_all_audio_summary_sheets_multiple()
        return {"message": "✅ Google Sheets updated for all languages via GitHub"}
    except Exception as e:
        import traceback
        traceback.print_exc()  # 👈 shows full error trace in terminal
        raise HTTPException(status_code=500, detail=str(e))



@github_router.get("/assigned_data-recording_stats-to-sheet", tags=["Annotator Data"])
def get_annotator_data():
    return push_annotators_to_sheet()


# @github_router.get("/annotation_update_stats_to_sheet", tags=["Annotator Data"])
# def get_annotation_update_stats_to_sheet():
#     return push_annotation_update_stats_to_sheet()


@github_router.get("/assigned_data-recording_stats-to-json", tags=["Annotator Data"])
def get_annotator_data_in_json():
    return get_annotators_json()


@github_router.get("/annotators", response_model=List[AnnotatorStat], tags=["Annotator Data"])
async def get_annotators(db: AsyncSession = Depends(get_session)):
    stmt = select(AnnotatorStat)
    result = await db.execute(stmt)
    return result.scalars().all()

@github_router.get("/annotators/summary", tags=["Annotator Data"])
async def get_summary(db: AsyncSession = Depends(get_session)):
    stmt = (
        select(
            AnnotatorStat.language,
            func.count(AnnotatorStat.id).label("annotator_count"),
            func.sum(AnnotatorStat.minutes_recorded).label("total_minutes"),
            func.sum(AnnotatorStat.files_read).label("total_files_read")
        )
        .group_by(AnnotatorStat.language)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "language": r.language,
            "annotator_count": r.annotator_count,
            "total_minutes": round(r.total_minutes or 0, 2),
            "total_files_read": r.total_files_read or 0
        }
        for r in rows
    ]



@github_router.get("/annotator-status", tags=["Annotator Data"])
def get_annotator_status_json():
    try:
        res = requests.get(annotator_status_url, headers=headers)
        res.raise_for_status()
        df = pd.read_csv(io.StringIO(res.text))

        # Flatten and clean
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading annotator_status.csv: {e}")




@github_router.get("/registered-annotators", tags=["Annotator Data"])
def get_registered_annotators():
    try:
        response = requests.get(get_registered_annotators_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching CSV: {str(e)}")

    try:
        df = pd.read_csv(io.StringIO(response.text))
        # Clean and JSON-serialize safely
        df = df.fillna("").infer_objects(copy=False)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")







stats_json_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/reports"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/reports"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

@github_router.get("/stats-json", tags=["Completed Task Google Sheets"])
def fetch_all_stats_flat_for_today():
    today = datetime.utcnow().strftime("%Y%m%d")
    try:
        res = requests.get(stats_json_url, headers=headers)
        res.raise_for_status()
        folders = res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list language folders: {str(e)}")

    all_rows = []

    for folder in folders:
        if folder["type"] != "dir":
            continue

        lang = folder["name"]
        txt_url = f"{RAW_BASE}/{lang}/{today}/report.txt"

        try:
            txt_res = requests.get(txt_url, headers=headers)
            if txt_res.status_code != 200:
                continue

            lines = txt_res.text.strip().splitlines()
            summary = {
                "language": lang,
                "annotators": safe_int(lines[1]),
                "files_read": safe_int(lines[2]),
                "remaining_texts": safe_int(lines[3]),
                "minutes_recorded": safe_float(lines[4])
            }
            all_rows.append(summary)
        except Exception:
            continue  # silently skip bad folders

    return all_rows




# ✅ Fetch stats for specific language
@github_router.get("/stats-json/{language}", tags=["Completed Task Google Sheets"])
def fetch_stats_for_language(language: str):
    # Step 1: List folders inside reports/{language}
    sub_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/reports/{language}"
    try:
        res = requests.get(sub_url, headers=headers)
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
        res = requests.get(csv_url, headers=headers)
        res.raise_for_status()
        df = pd.read_csv(io.StringIO(res.text))
        df["language"] = language
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to fetch data for language '{language}' on date '{latest_date}': {str(e)}"
        )

    


@github_router.get("/stats-summary", tags=["Completed Task Google Sheets"])
def fetch_annotation_summary_all_languages():
    try:
        res = requests.get(stats_json_url, headers=headers)
        res.raise_for_status()
        folders = res.json()
        print(f"🔎 Found {len(folders)} language folders")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list language folders: {str(e)}")

    summaries = []

    for folder in folders:
        if folder["type"] != "dir":
            continue

        lang = folder["name"]
        print(f"📁 Checking language folder: {lang}")

        # 🔍 List date folders inside /reports/{lang}
        sub_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/reports/{lang}"
        sub_res = requests.get(sub_url, headers=headers)
        if sub_res.status_code != 200:
            continue

        subfolders = [f["name"] for f in sub_res.json() if f["type"] == "dir"]
        if not subfolders:
            continue

        # 📅 Sort to get the latest folder by date
        latest_date = sorted(subfolders, reverse=True)[0]

        txt_url = f"{RAW_BASE}/{lang}/{latest_date}/report.txt"

        try:
            txt_res = requests.get(txt_url, headers=headers)
            if txt_res.status_code != 200:
                continue

            lines = txt_res.text.strip().splitlines()
            print(f"📄 Found report.txt for {lang}/{latest_date}")

            summary = {}

            for i, line in enumerate(lines):
                if line.strip().lower().startswith("annotation info"):
                    summary = {
                        "language": line.split(":")[1].strip() if ":" in line else lang,
                        "annotators": safe_int(lines[i+1]),
                        "files_read": safe_int(lines[i+2]),
                        "remaining_texts": safe_int(lines[i+3]),
                        "minutes_recorded": safe_float(lines[i+4])
                    }

                    if all(v is not None for v in summary.values()):
                        summaries.append(summary)
                    else:
                        print(f"⚠️ Skipping summary for {lang} due to parsing error: {summary}")
                    break
            print(f"📃 Content of report.txt for {lang}:\n{txt_res.text}")

        except Exception:
            continue

    return summaries







def safe_int(line: str):
    try:
        return int(line.split(":")[1].replace(",", "").strip())
    except Exception as e:
        print(f"❌ Failed to parse int from: '{line}' – {e}")
        return None

def safe_float(line: str):
    try:
        return float(line.split(":")[1].replace(",", "").strip())
    except Exception as e:
        print(f"❌ Failed to parse float from: '{line}' – {e}")
        return None
