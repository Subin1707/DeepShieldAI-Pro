from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from app.core.config import settings
from app.utils.response_utils import success_response

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("")
def list_reports():
    report_dir = Path(settings.REPORT_DIR)
    if not report_dir.exists():
        return success_response(data=[], message="No reports found.")

    reports = [
        {
            "reportId": path.stem,
            "fileName": path.name,
            "downloadUrl": f"/api/reports/{path.stem}/download",
        }
        for path in sorted(report_dir.glob("*.txt"), reverse=True)
    ]
    return success_response(data=reports, message="Reports loaded.")


@router.get("/{report_id}")
def get_report_text(report_id: str):
    report_path = Path(settings.REPORT_DIR) / f"{report_id}.txt"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found.")

    return PlainTextResponse(report_path.read_text(encoding="utf-8"))


@router.get("/{report_id}/download")
def download_report(report_id: str):
    report_path = Path(settings.REPORT_DIR) / f"{report_id}.txt"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found.")

    return FileResponse(
        path=report_path,
        media_type="text/plain",
        filename=report_path.name,
    )
