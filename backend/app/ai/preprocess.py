import cv2
import numpy as np

from app.core.config import settings


def _normalize_image(image: np.ndarray) -> np.ndarray:
    image = image.astype("float32") / 255.0
    return image


def read_image(file_path: str) -> np.ndarray:
    image = cv2.imread(str(file_path))
    if image is None:
        raise ValueError("Could not read image for model preprocessing.")
    return image


def resize_rgb_image(image: np.ndarray, image_size: int | None = None) -> np.ndarray:
    if image is None:
        raise ValueError("Image frame is empty.")

    image_size = image_size or settings.IMAGE_MODEL_SIZE
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (image_size, image_size))
    return image


def preprocess_image_array(image: np.ndarray, image_size: int | None = None) -> np.ndarray:
    image = resize_rgb_image(image, image_size=image_size)
    return _normalize_image(image)


def preprocess_image_file(file_path: str, image_size: int | None = None) -> np.ndarray:
    image = read_image(file_path)
    image = preprocess_image_array(image, image_size=image_size)
    return np.expand_dims(image, axis=0)


def preprocess_frame(frame: np.ndarray, image_size: int | None = None) -> np.ndarray:
    frame = preprocess_image_array(frame, image_size=image_size)
    return np.expand_dims(frame, axis=0)


def preprocess_image_files(file_paths: list[str], image_size: int | None = None) -> np.ndarray:
    if not file_paths:
        raise ValueError("No image files provided for preprocessing.")

    tensors = [preprocess_image_file(path, image_size=image_size)[0] for path in file_paths]
    return np.stack(tensors, axis=0)
