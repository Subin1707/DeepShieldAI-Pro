import csv
import json
from pathlib import Path

from app.core.config import settings


BACKEND_ROOT = Path(__file__).resolve().parents[2]
TRAINING_LOG_ROOT = BACKEND_ROOT / "training_logs"
DEFAULT_HISTORY_CANDIDATES = [
    TRAINING_LOG_ROOT / "video_temporal" / "history.csv",
    TRAINING_LOG_ROOT / "efficientnet" / "history.csv",
]


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_readable_history(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def _configured_history_candidates() -> list[Path]:
    configured_path = Path(settings.TRAINING_HISTORY_PATH)
    if configured_path.is_absolute():
        return [configured_path]
    return [configured_path, BACKEND_ROOT / configured_path]


def _resolve_history_path() -> Path | None:
    candidates = _configured_history_candidates() + DEFAULT_HISTORY_CANDIDATES
    for path in candidates:
        if _is_readable_history(path):
            return path

    if TRAINING_LOG_ROOT.exists():
        histories = [
            path
            for path in TRAINING_LOG_ROOT.rglob("history.csv")
            if _is_readable_history(path)
        ]
        if histories:
            return max(histories, key=lambda path: path.stat().st_mtime)

    return None


def _load_validation_report(history_path: Path) -> dict | None:
    report_path = history_path.with_name("validation_report.json")
    if not _is_readable_history(report_path):
        return None

    try:
        with report_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def _history_paths(history_path: Path) -> list[Path]:
    runs_dir = history_path.parent / "runs"
    if not runs_dir.exists():
        return [history_path]

    histories = [
        path
        for path in runs_dir.glob("*/history.csv")
        if _is_readable_history(path)
    ]
    if not histories:
        return [history_path]
    return sorted(histories, key=lambda path: (path.stat().st_mtime, str(path)))


def _run_id_from_path(path: Path, fallback: str) -> str:
    return path.parent.name if path.parent.name != "runs" else fallback


def _append_point(runs: list[dict], point: dict, source_path: Path | None = None) -> None:
    last_run = runs[-1] if runs else None
    last_epoch = last_run["points"][-1]["epoch"] if last_run and last_run["points"] else None
    path_changed = bool(last_run and source_path and last_run.get("source") != str(source_path))
    starts_new_run = (
        last_run is None
        or path_changed
        or (point["epoch"] == 0 and last_epoch is not None)
        or (last_epoch is not None and point["epoch"] < last_epoch)
    )

    if starts_new_run:
        fallback = f"run-{len(runs) + 1}"
        run_id = _run_id_from_path(source_path, fallback) if source_path else fallback
        if any(run.get("runId") == run_id for run in runs):
            run_id = f"{run_id}-{len(runs) + 1}"
        runs.append(
            {
                "runId": run_id,
                "startStep": point["step"],
                "source": str(source_path) if source_path else None,
                "points": [],
            }
        )

    point["runId"] = runs[-1]["runId"]
    point["runStep"] = len(runs[-1]["points"]) + 1
    runs[-1]["points"].append(point)


def _summarize_run(run: dict) -> dict:
    points = run["points"]
    best_validation = min(
        (point for point in points if point.get("valLoss") is not None),
        key=lambda point: point["valLoss"],
        default=None,
    )
    return {
        **run,
        "totalPoints": len(points),
        "endStep": points[-1]["step"],
        "lastPoint": points[-1],
        "bestValidation": best_validation,
    }


def load_training_history(limit: int | None = None) -> dict | None:
    history_path = _resolve_history_path()
    if history_path is None:
        return None

    points = []
    runs = []
    history_paths = _history_paths(history_path)
    for source_path in history_paths:
        with source_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                loss = _to_float(row.get("loss"))
                if loss is None:
                    continue

                points.append(
                    {
                        "step": len(points) + 1,
                        "epoch": int(_to_float(row.get("epoch")) or 0),
                        "loss": loss,
                        "valLoss": _to_float(row.get("val_loss")),
                        "accuracy": _to_float(row.get("accuracy")),
                        "valAccuracy": _to_float(row.get("val_accuracy")),
                        "auc": _to_float(row.get("auc")),
                        "valAuc": _to_float(row.get("val_auc")),
                        "learningRate": _to_float(row.get("learning_rate")),
                        "source": str(source_path),
                    }
                )
                _append_point(runs, points[-1], source_path)

    if not points:
        return None

    if limit and limit > 0:
        points = points[-limit:]

    runs = [_summarize_run(run) for run in runs]
    current_run = runs[-1] if runs else None
    best_validation = min(
        (point for point in points if point.get("valLoss") is not None),
        key=lambda point: point["valLoss"],
        default=None,
    )

    return {
        "source": str(history_path),
        "sources": [str(path) for path in history_paths],
        "runCount": len(runs),
        "runs": runs,
        "currentRun": current_run,
        "validationReport": _load_validation_report(history_path),
        "points": points,
        "totalPoints": len(points),
        "bestValidation": best_validation,
        "lastPoint": points[-1],
    }
