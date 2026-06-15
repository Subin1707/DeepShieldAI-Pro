import random
from pathlib import Path

from app.ai.inference import run_image_inference
from app.core.constants import EXPLANATION_SIGNALS, FOCUS_AREAS, PREDICTION_FAKE, PREDICTION_REAL
from app.utils.file_utils import is_image_file
from app.utils.risk_utils import calculate_risk_level, calculate_risk_score


def _build_frame_results(total_frames: int, suspicious_frames: int) -> list[dict]:
    return [
        {
            "frameIndex": index + 1,
            "prediction": PREDICTION_FAKE if index < suspicious_frames else PREDICTION_REAL,
            "confidence": round(random.uniform(75, 96), 2),
        }
        for index in range(total_frames)
    ]


def predict_deepfake(file_path: str, analysis_id: str) -> dict:
    model_result = run_image_inference(file_path) if is_image_file(file_path) else None

    if model_result:
        confidence = model_result["confidence"]
        prediction = model_result["prediction"]
        risk_level = model_result["riskLevel"]
        risk_score = model_result["riskScore"]
    else:
        confidence = round(random.uniform(87.0, 96.5), 2)
        prediction = PREDICTION_FAKE
        risk_level = calculate_risk_level(confidence, prediction)
        risk_score = calculate_risk_score(confidence, prediction)


    if is_image_file(file_path):
        total_frames = 1
        suspicious_frames = 1 if prediction == PREDICTION_FAKE else 0
        frame_results = [{"frameIndex": 1, "prediction": prediction, "confidence": confidence}]
    else:
        total_frames = 20
        suspicious_frames = random.randint(15, 19)
        frame_results = _build_frame_results(total_frames, suspicious_frames)

    return {
        "analysisId": analysis_id,
        "sourceFile": Path(file_path).name,
        "prediction": prediction,
        "confidence": confidence,
        "riskLevel": risk_level,
        "riskScore": risk_score,
        "modelUsed": bool(model_result),
        "totalFrames": total_frames,
        "suspiciousFrames": suspicious_frames,
        "focusAreas": FOCUS_AREAS,
        "explanation": EXPLANATION_SIGNALS,
        "frameResults": frame_results,
    }
