from pathlib import Path

import cv2
from PIL import Image

from app.core.constants import IMAGE_SIZE
from app.core.config import settings


def get_image_metadata(file_path: str) -> dict:
    path = Path(file_path)
    with Image.open(path) as image:
        return {
            "type": "image",
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "sizeBytes": path.stat().st_size,
        }


def load_image_for_model(file_path: str):
    image = cv2.imread(file_path)
    if image is None:
        raise ValueError("Could not read image file.")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))


def save_image_frame(file_path: str, analysis_id: str) -> str:
    frame_dir = Path(settings.FRAME_DIR)
    frame_dir.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(file_path)
    if image is None:
        raise ValueError("Could not read image file.")

    output_path = frame_dir / f"{analysis_id}_frame_1.jpg"
    cv2.imwrite(str(output_path), image)
    return str(output_path)
