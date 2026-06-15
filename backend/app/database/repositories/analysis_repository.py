import json

from app.database.database import db_session, init_db
from app.database.models import row_to_analysis_record


def create_analysis(result: dict) -> dict:
    init_db()

    with db_session() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO analyses (
                analysis_id,
                report_id,
                file_name,
                file_path,
                prediction,
                confidence,
                risk_level,
                risk_score,
                model_used,
                total_frames,
                suspicious_frames,
                heatmap_url,
                report_url,
                payload_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.get("analysisId"),
                result.get("reportId"),
                result.get("fileName"),
                result.get("filePath"),
                result.get("prediction"),
                result.get("confidence"),
                result.get("riskLevel"),
                result.get("riskScore"),
                int(bool(result.get("modelUsed"))),
                result.get("totalFrames"),
                result.get("suspiciousFrames"),
                result.get("heatmapUrl"),
                result.get("reportUrl"),
                json.dumps(result, ensure_ascii=False),
                result.get("createdAt"),
            ),
        )

    return result


def list_analyses(limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
    init_db()

    with db_session() as connection:
        total = connection.execute("SELECT COUNT(*) AS count FROM analyses").fetchone()["count"]
        rows = connection.execute(
            """
            SELECT * FROM analyses
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    records = [row_to_analysis_record(row).payload for row in rows]
    return records, total


def get_analysis_by_id(analysis_id: str) -> dict | None:
    init_db()

    with db_session() as connection:
        row = connection.execute(
            "SELECT * FROM analyses WHERE analysis_id = ?",
            (analysis_id,),
        ).fetchone()

    if row is None:
        return None

    return row_to_analysis_record(row).payload


def delete_analysis(analysis_id: str) -> bool:
    init_db()

    with db_session() as connection:
        cursor = connection.execute(
            "DELETE FROM analyses WHERE analysis_id = ?",
            (analysis_id,),
        )
        return cursor.rowcount > 0
