from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from app.ai.inference import _extract_fake_probability, build_inference_result
from app.core.config import settings


def _video_model_path() -> Path:
    return Path(settings.VIDEO_MODEL_PATH)


def video_model_file_exists() -> bool:
    path = _video_model_path()
    return path.exists() and path.stat().st_size > 0


@lru_cache
def load_video_model():
    if not video_model_file_exists():
        return None

    try:
        from tensorflow.keras.models import load_model
    except ImportError:
        return None

    try:
        return load_model(_video_model_path())
    except Exception as exc:
        print("Video model load error:", exc)
        return None


def get_video_model_status() -> dict:
    path = _video_model_path()
    model = load_video_model()
    sequence_length, image_size = _get_model_input_config(model)
    return {
        "modelPath": str(path),
        "exists": path.exists(),
        "sizeBytes": path.stat().st_size if path.exists() else 0,
        "ready": model is not None,
        "sequenceLength": sequence_length,
        "imageSize": image_size,
        "inputShape": list(model.input_shape) if model is not None else None,
    }


def _get_model_input_config(model) -> tuple[int, int]:
    if model is None:
        return settings.VIDEO_SEQUENCE_LENGTH, settings.VIDEO_IMAGE_SIZE

    input_shape = model.input_shape
    if isinstance(input_shape, list):
        input_shape = input_shape[0]

    if len(input_shape) != 5:
        return settings.VIDEO_SEQUENCE_LENGTH, settings.VIDEO_IMAGE_SIZE

    _, sequence_length, height, width, _ = input_shape
    return (
        int(sequence_length or settings.VIDEO_SEQUENCE_LENGTH),
        int(height or width or settings.VIDEO_IMAGE_SIZE),
    )


def _fit_sequence(face_paths: list[str], sequence_length: int) -> list[str]:
    if not face_paths:
        raise ValueError("No face frames are available for temporal inference.")

    if len(face_paths) == sequence_length:
        return face_paths

    if len(face_paths) > sequence_length:
        return [
            face_paths[round(i * (len(face_paths) - 1) / (sequence_length - 1))]
            for i in range(sequence_length)
        ]

    return face_paths + [face_paths[-1]] * (sequence_length - len(face_paths))


def _preprocess_video_sequence(face_paths: list[str], image_size: int) -> np.ndarray:
    frames = []
    for face_path in face_paths:
        image = cv2.imread(face_path)
        if image is None:
            image = np.zeros((image_size, image_size, 3), dtype=np.uint8)
        image = cv2.resize(image, (image_size, image_size))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frames.append(image.astype("uint8"))
    return np.expand_dims(np.stack(frames, axis=0), axis=0)


def run_video_sequence_inference(face_paths: list[str]) -> dict | None:
    model = load_video_model()
    if model is None:
        return None

    sequence_length, image_size = _get_model_input_config(model)
    sequence_paths = _fit_sequence(face_paths, sequence_length)
    sequence = _preprocess_video_sequence(sequence_paths, image_size)
    raw_prediction = model.predict(sequence, verbose=0)
    fake_probability = _extract_fake_probability(raw_prediction)
    result = build_inference_result(fake_probability)
    result["inferenceMode"] = "video_temporal_model"
    result["modelUsed"] = True
    result["sequenceLength"] = len(sequence_paths)
    result["imageSize"] = image_size
    return result
