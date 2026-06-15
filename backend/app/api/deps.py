from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.utils.file_utils import validate_file


def get_app_settings():
    return settings


def validate_upload_dependency(file: UploadFile):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        validate_file(file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return file


def require_existing_report(report_id: str) -> Path:
    report_path = Path(settings.REPORT_DIR) / f"{report_id}.txt"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found.")
    return report_path
