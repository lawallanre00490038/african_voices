from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class AnnotatorStat(SQLModel, table=True):
    __tablename__ = "annotator_stats"
    id: Optional[int] = Field(default=None, primary_key=True)
    annotator_id: str = Field(index=True)
    name: str
    language: str = Field(index=True)
    report_date: date = Field(index=True)

    files_read: int = 0
    remaining_texts: int = 0
    minutes_recorded: float = 0.0

    has_started: bool = Field(default=True)

    created_at: Optional[date] = Field(default_factory=date.today)

