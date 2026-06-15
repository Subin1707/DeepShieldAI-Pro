from dataclasses import dataclass
from typing import Any


@dataclass
class AnalysisRecord:
    analysis_id: str
    report_id: str | None
    file_name: str | None
    file_path: str | None
    prediction: str
    confidence: float
    risk_level: str
    risk_score: int
    model_used: bool
    total_frames: int
    suspicious_frames: int
    heatmap_url: str | None
    report_url: str | None
    payload: dict[str, Any]
    created_at: str


def row_to_analysis_record(row) -> AnalysisRecord:
    import json

    return AnalysisRecord(
        analysis_id=row["analysis_id"],
        report_id=row["report_id"],
        file_name=row["file_name"],
        file_path=row["file_path"],
        prediction=row["prediction"],
        confidence=row["confidence"],
        risk_level=row["risk_level"],
        risk_score=row["risk_score"],
        model_used=bool(row["model_used"]),
        total_frames=row["total_frames"],
        suspicious_frames=row["suspicious_frames"],
        heatmap_url=row["heatmap_url"],
        report_url=row["report_url"],
        payload=json.loads(row["payload_json"]),
        created_at=row["created_at"],
    )
