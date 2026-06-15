from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings


def _load_face_detector():
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    return detector if not detector.empty() else None


FACE_DETECTOR = _load_face_detector()


def detect_largest_face(frame: np.ndarray) -> tuple[int, int, int, int] | None:
    if frame is None or frame.size == 0 or FACE_DETECTOR is None:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_DETECTOR.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(48, 48),
    )
    if len(faces) == 0:
        return None

    x, y, width, height = max(faces, key=lambda box: box[2] * box[3])
    return int(x), int(y), int(width), int(height)


def crop_face_or_frame(frame: np.ndarray, padding_ratio: float = 0.22) -> tuple[np.ndarray, dict]:
    box = detect_largest_face(frame)
    if box is None:
        return frame, {"faceDetected": False, "bbox": None}

    x, y, width, height = box
    pad_x = int(width * padding_ratio)
    pad_y = int(height * padding_ratio)
    max_y, max_x = frame.shape[:2]

    left = max(0, x - pad_x)
    top = max(0, y - pad_y)
    right = min(max_x, x + width + pad_x)
    bottom = min(max_y, y + height + pad_y)

    crop = frame[top:bottom, left:right]
    if crop.size == 0:
        return frame, {"faceDetected": False, "bbox": None}

    return crop, {
        "faceDetected": True,
        "bbox": {
            "x": left,
            "y": top,
            "width": right - left,
            "height": bottom - top,
        },
    }


def save_face_crop(frame_path: str, analysis_id: str, order: int) -> tuple[str, dict]:
    frame = cv2.imread(frame_path)
    if frame is None:
        raise ValueError(f"Could not read sampled frame: {frame_path}")

    crop, metadata = crop_face_or_frame(frame)
    face_dir = Path(settings.FACE_DIR)
    face_dir.mkdir(parents=True, exist_ok=True)

    output_path = face_dir / f"{analysis_id}_face_{order}.jpg"
    cv2.imwrite(str(output_path), crop)
    return str(output_path), metadata
