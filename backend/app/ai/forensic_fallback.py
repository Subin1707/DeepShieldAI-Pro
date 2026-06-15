import cv2
import numpy as np

from app.ai.labels import probability_payload
from app.core.constants import PREDICTION_FAKE, PREDICTION_REAL
from app.utils.risk_utils import calculate_risk_level, calculate_risk_score


def _safe_gray(image: np.ndarray) -> np.ndarray:
    if image is None or image.size == 0:
        raise ValueError("Cannot analyze an empty image.")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _artifact_score(image: np.ndarray) -> tuple[float, list[str]]:
    gray = _safe_gray(image)
    resized = cv2.resize(image, (224, 224))
    gray_resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    blur_var = float(cv2.Laplacian(gray_resized, cv2.CV_64F).var())
    edges = cv2.Canny(gray_resized, 90, 180)
    edge_density = float(np.mean(edges > 0))

    high_pass = cv2.absdiff(gray_resized, cv2.GaussianBlur(gray_resized, (0, 0), 2.0))
    noise_level = float(np.std(high_pass))

    ycrcb = cv2.cvtColor(resized, cv2.COLOR_BGR2YCrCb)
    chroma_noise = float(np.mean(np.std(ycrcb[:, :, 1:], axis=(0, 1))))

    block = 8
    height, width = gray_resized.shape
    vertical_blocks = np.abs(np.diff(gray_resized[:, block:width:block], axis=1)).mean() if width > block else 0
    horizontal_blocks = np.abs(np.diff(gray_resized[block:height:block, :], axis=0)).mean() if height > block else 0
    blocking = float((vertical_blocks + horizontal_blocks) / 2)

    blur_signal = np.clip((120 - blur_var) / 120, 0, 1)
    edge_signal = np.clip((edge_density - 0.08) / 0.18, 0, 1)
    noise_signal = np.clip((noise_level - 7) / 24, 0, 1)
    chroma_signal = np.clip((chroma_noise - 5) / 28, 0, 1)
    blocking_signal = np.clip((blocking - 2) / 18, 0, 1)

    fake_probability = float(
        0.18
        + 0.24 * blur_signal
        + 0.20 * edge_signal
        + 0.22 * noise_signal
        + 0.10 * chroma_signal
        + 0.06 * blocking_signal
    )
    fake_probability = float(np.clip(fake_probability, 0.03, 0.97))

    signals = []
    if blur_signal > 0.45:
        signals.append("Low local sharpness around sampled face regions")
    if edge_signal > 0.45:
        signals.append("Dense edge transitions that may indicate compositing boundaries")
    if noise_signal > 0.45:
        signals.append("High-frequency residual noise inconsistent with natural capture")
    if chroma_signal > 0.45:
        signals.append("Color channel variance suggests possible synthetic texture")
    if blocking_signal > 0.45:
        signals.append("Compression block artifacts are elevated")

    if not signals:
        signals.append("No strong forensic artifact signal crossed the fallback threshold")

    return fake_probability, signals


def run_forensic_fallback(image_path: str) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image for fallback analysis: {image_path}")

    fake_probability, signals = _artifact_score(image)
    prediction = PREDICTION_FAKE if fake_probability >= 0.5 else PREDICTION_REAL
    confidence = round((fake_probability if prediction == PREDICTION_FAKE else 1 - fake_probability) * 100, 2)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "riskLevel": calculate_risk_level(confidence, prediction),
        "riskScore": calculate_risk_score(confidence, prediction),
        "modelUsed": False,
        "inferenceMode": "forensic_fallback",
        "signals": signals,
        **probability_payload(fake_probability),
    }
