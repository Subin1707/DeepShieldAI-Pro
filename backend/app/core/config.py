import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "DeepShield AI Pro")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION: str = os.getenv(
        "APP_DESCRIPTION",
        "Deepfake Detection Platform using EfficientNet-B0, Grad-CAM and Groq AI",
    )
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    MODEL_PATH: str = os.getenv(
        "MODEL_PATH",
        "models/efficientnet_deepfake_thisperson.keras"
    )
    IMAGE_MODEL_SIZE: int = int(os.getenv("IMAGE_MODEL_SIZE", "160"))
    FAKE_THRESHOLD: float = float(os.getenv("FAKE_THRESHOLD", "0.58"))
    REVIEW_MARGIN: float = float(os.getenv("REVIEW_MARGIN", "0.08"))
    SUSPICIOUS_FRAME_THRESHOLD: float = float(os.getenv("SUSPICIOUS_FRAME_THRESHOLD", "0.55"))
    FORENSIC_STRICT_THRESHOLD: float = float(os.getenv("FORENSIC_STRICT_THRESHOLD", "58"))
    REQUIRE_MODEL_IN_PRODUCTION: bool = os.getenv("REQUIRE_MODEL_IN_PRODUCTION", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    VIDEO_MODEL_PATH: str = os.getenv(
        "VIDEO_MODEL_PATH",
        "models/video_deepfake.keras"
    )
    TRAINING_HISTORY_PATH: str = os.getenv(
        "TRAINING_HISTORY_PATH",
        "training_logs/video_temporal/history.csv"
    )
    VIDEO_SEQUENCE_LENGTH: int = int(os.getenv("VIDEO_SEQUENCE_LENGTH", "4"))
    VIDEO_IMAGE_SIZE: int = int(os.getenv("VIDEO_IMAGE_SIZE", "128"))

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "storage/uploads")
    FRAME_DIR: str = os.getenv("FRAME_DIR", "storage/frames")
    FACE_DIR: str = os.getenv("FACE_DIR", "storage/faces")
    HEATMAP_DIR: str = os.getenv("HEATMAP_DIR", "storage/heatmaps")
    REPORT_DIR: str = os.getenv("REPORT_DIR", "storage/reports")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/deepshield.db")

    CHATBOT_PROVIDER: str = os.getenv("CHATBOT_PROVIDER", "groq")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:5174,http://localhost:5175,"
            "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175",
        ).split(",")
        if origin.strip()
    ]

    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(200 * 1024 * 1024)))

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    def ensure_storage_dirs(self):
        for directory in [
            self.UPLOAD_DIR,
            self.FRAME_DIR,
            self.FACE_DIR,
            self.HEATMAP_DIR,
            self.REPORT_DIR,
            "data",
        ]:
            Path(directory).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
