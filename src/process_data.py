import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List
from src.models import AnnotatorStat
from sqlalchemy.orm import Session
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import AnnotatorStat

from src.models import AnnotatorStat 


def parse_report_and_stats(language: str, folder_path: Path) -> List[AnnotatorStat]:
    report_txt = folder_path / "report.txt"
    stats_csv = folder_path / "stats.csv"
    report_date = datetime.strptime(folder_path.name, "%Y%m%d").date()
    annotators = {}

    if report_txt.exists():
        with open(report_txt, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_id = None
        current_name = None
        for line in lines:
            line = line.strip()

            if line.startswith("ID:"):
                current_id = line.replace("ID:", "").strip()

            elif line.startswith("Name:"):
                current_name = line.replace("Name:", "").strip()

            elif line.lower().startswith("has not started"):
                if current_id and current_name:
                    annotators[current_id] = AnnotatorStat(
                        annotator_id=current_id,
                        name=current_name,
                        language=language,
                        report_date=report_date,
                        files_read=0,
                        remaining_texts=0,
                        minutes_recorded=0.0,
                        has_started=False
                    )

    # Merge stats.csv if it exists
    if stats_csv.exists():
        df = pd.read_csv(stats_csv)
        for _, row in df.iterrows():
            id_ = str(row["ID"]).strip()
            if id_ in annotators:
                annotators[id_].files_read = int(row.get("Files Read", 0))
                annotators[id_].minutes_recorded = float(row.get("Minutes Recorded", 0.0))
                annotators[id_].remaining_texts = int(row.get("Remaining Texts", 0))
            else:
                annotators[id_] = AnnotatorStat(
                    annotator_id=id_,
                    name=str(row.get("Name", "Unknown")),
                    language=language,
                    report_date=report_date,
                    files_read=int(row.get("Files Read", 0)),
                    remaining_texts=int(row.get("Remaining Texts", 0)),
                    minutes_recorded=float(row.get("Minutes Recorded", 0.0)),
                    has_started=True
                )

    return list(annotators.values())


def process_all_languages(base_path: Path) -> List[AnnotatorStat]:
    all_stats = []
    for language_folder in base_path.iterdir():
        if not language_folder.is_dir():
            continue

        language = language_folder.name

        for report_folder in language_folder.iterdir():
            if not report_folder.is_dir():
                continue

            annotator_stats = parse_report_and_stats(language, report_folder)
            all_stats.extend(annotator_stats)

    return all_stats




async def update_or_create_language_stat(db: AsyncSession, language: str, data: dict):
    annotator_id = data.get("annotator_id")
    report_date = data.get("report_date")

    if not annotator_id or not report_date:
        return

    stmt = select(AnnotatorStat).where(
        AnnotatorStat.annotator_id == annotator_id,
        AnnotatorStat.language == language,
        AnnotatorStat.report_date == report_date
    )

    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        for key, value in data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
    else:
        new_record = AnnotatorStat(**data)
        db.add(new_record)

