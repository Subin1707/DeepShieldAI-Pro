from pathlib import Path

import cv2

from app.core.config import settings
from app.core.constants import DEFAULT_FRAME_SAMPLE_COUNT


def get_video_metadata(file_path: str) -> dict:
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise ValueError("Could not read video file.")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = round(frame_count / fps, 2) if fps else 0
    cap.release()

    return {
        "type": "video",
        "width": width,
        "height": height,
        "fps": round(fps, 2),
        "frameCount": frame_count,
        "durationSeconds": duration,
        "sizeBytes": Path(file_path).stat().st_size,
    }


def sample_video_frames(
    file_path: str,
    analysis_id: str,
    max_frames: int = DEFAULT_FRAME_SAMPLE_COUNT,
) -> list[str]:
    output_dir = Path(settings.FRAME_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise ValueError("Could not read video file.")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return []

    count = min(max_frames, total_frames)
    if count == 1:
        indices = [0]
    else:
        indices = [round(i * (total_frames - 1) / (count - 1)) for i in range(count)]

    saved_paths: list[str] = []
    for order, frame_index in enumerate(indices, start=1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = cap.read()
        if not success:
            continue

        output_path = output_dir / f"{analysis_id}_frame_{order}.jpg"
        cv2.imwrite(str(output_path), frame)
        saved_paths.append(str(output_path))

    cap.release()
    return saved_paths
