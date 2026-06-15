import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.core.config import settings


def get_database_path() -> Path:
    database_url = settings.DATABASE_URL
    if database_url.startswith("sqlite:///"):
        return Path(database_url.replace("sqlite:///", "", 1))
    return Path("data/deepshield.db")


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def db_session():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with db_session() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                analysis_id TEXT PRIMARY KEY,
                report_id TEXT,
                file_name TEXT,
                file_path TEXT,
                prediction TEXT,
                confidence REAL,
                risk_level TEXT,
                risk_score INTEGER,
                model_used INTEGER,
                total_frames INTEGER,
                suspicious_frames INTEGER,
                heatmap_url TEXT,
                report_url TEXT,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_analyses_created_at
            ON analyses(created_at)
            """
        )
