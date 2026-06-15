import os
import re
import shutil
from pathlib import Path

from fastapi import UploadFile

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS
MAX_UPLOAD_SIZE = 200 * 1024 * 1024


def ensure_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_file_extension(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def is_image_file(filename: str | None) -> bool:
    return get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS


def is_video_file(filename: str | None) -> bool:
    return get_file_extension(filename) in ALLOWED_VIDEO_EXTENSIONS


def sanitize_filename(filename: str | None) -> str:
    if not filename:
        return "upload"

    stem = Path(filename).stem.strip()
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem)
    return stem[:80] or "upload"


def validate_file(filename: str | None):
    ext = get_file_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported file type. Allowed extensions: {allowed}")


def validate_file_size(file_path: str | Path, max_size: int = MAX_UPLOAD_SIZE):
    size = Path(file_path).stat().st_size
    if size > max_size:
        raise ValueError(f"File is too large. Max size is {max_size // (1024 * 1024)}MB.")


def build_upload_filename(original_filename: str | None, analysis_id: str) -> str:
    ext = get_file_extension(original_filename)
    safe_name = sanitize_filename(original_filename)
    return f"{analysis_id}_{safe_name}{ext}"


async def save_upload_file(file: UploadFile, upload_dir: str | Path, analysis_id: str) -> str:
    validate_file(file.filename)
    upload_path = ensure_dir(upload_dir)
    file_path = upload_path / build_upload_filename(file.filename, analysis_id)

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    validate_file_size(file_path)
    return str(file_path)


def delete_file(path: str | Path):
    file_path = Path(path)
    if file_path.exists() and file_path.is_file():
        os.remove(file_path)
