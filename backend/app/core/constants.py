IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS.union(VIDEO_EXTENSIONS)
MAX_UPLOAD_SIZE_MB = 200
IMAGE_SIZE = 224
DEFAULT_FRAME_SAMPLE_COUNT = 20

PREDICTION_REAL = "REAL"
PREDICTION_FAKE = "FAKE"
PREDICTION_UNKNOWN = "UNKNOWN"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

RISK_COLORS = {
    RISK_LOW: "green",
    RISK_MEDIUM: "yellow",
    RISK_HIGH: "orange",
    RISK_CRITICAL: "red",
}

DEFAULT_TOTAL_VIDEO_FRAMES = 20

FOCUS_AREAS = [
    "Eye region",
    "Mouth boundary",
    "Skin texture",
    "Face edge"
]

EXPLANATION_SIGNALS = [
    "Unnatural facial texture detected",
    "Abnormal eye region artifacts",
    "Inconsistent lighting around face boundary",
    "Possible synthetic facial boundary artifacts"
]

ANALYSIS_STATUS_PENDING = "PENDING"
ANALYSIS_STATUS_PROCESSING = "PROCESSING"
ANALYSIS_STATUS_COMPLETED = "COMPLETED"
ANALYSIS_STATUS_FAILED = "FAILED"

SUPPORTED_UPLOAD_MESSAGE = "Please upload an image or video file."
