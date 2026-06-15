import numpy as np

from app.ai.labels import (
    confidence_from_probability,
    decision_payload,
    label_from_probability,
    probability_payload,
)
from app.ai.model_loader import get_model_status, load_deepfake_model
from app.ai.preprocess import preprocess_image_file, preprocess_image_files
from app.utils.risk_utils import calculate_risk_level, calculate_risk_score


def _extract_fake_probability(raw_prediction) -> float:
    values = np.asarray(raw_prediction).squeeze()

    if values.ndim == 0:
        return float(values)

    if values.ndim == 1 and values.shape[0] == 1:
        return float(values[0])

    if values.ndim == 1 and values.shape[0] >= 2:
        return float(values[-1])

    flattened = values.reshape(-1)
    return float(flattened[-1])


def build_inference_result(fake_probability: float) -> dict:
    prediction = label_from_probability(fake_probability)
    confidence = confidence_from_probability(fake_probability, prediction)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "riskLevel": calculate_risk_level(confidence, prediction),
        "riskScore": calculate_risk_score(confidence, prediction),
        "modelUsed": True,
        **decision_payload(fake_probability),
        **probability_payload(fake_probability),
    }


def run_image_inference(file_path: str) -> dict | None:
    model = load_deepfake_model()
    if model is None:
        return None

    input_tensor = preprocess_image_file(file_path)
    raw_prediction = model.predict(input_tensor)
    fake_probability = _extract_fake_probability(raw_prediction)
    result = build_inference_result(fake_probability)
    result["inferenceMode"] = f"{model.backend}_model"
    return result


def run_batch_inference(file_paths: list[str]) -> list[dict] | None:
    model = load_deepfake_model()
    if model is None:
        return None

    input_tensor = preprocess_image_files(file_paths)
    raw_predictions = model.predict(input_tensor)
    predictions = np.asarray(raw_predictions).reshape((len(file_paths), -1))

    results = []
    for index, prediction_values in enumerate(predictions):
        fake_probability = _extract_fake_probability(prediction_values)
        result = build_inference_result(fake_probability)
        result["frameIndex"] = index + 1
        result["filePath"] = file_paths[index]
        result["inferenceMode"] = f"{model.backend}_model"
        results.append(result)

    return results


def get_ai_status() -> dict:
    return get_model_status()
