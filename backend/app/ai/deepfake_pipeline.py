from statistics import mean, median
from time import perf_counter

from app.ai.embedding_similarity import build_embedding_similarity
from app.ai.face_detector import save_face_crop
from app.ai.forensic_fallback import run_forensic_fallback
from app.ai.inference import run_batch_inference
from app.ai.labels import decision_payload
from app.ai.model_loader import is_model_ready
from app.ai.temporal_inference import run_video_sequence_inference
from app.core.config import settings
from app.core.constants import FOCUS_AREAS, PREDICTION_FAKE, PREDICTION_REAL
from app.utils.risk_utils import calculate_risk_level, calculate_risk_score


def _aggregate_fake_probability(frame_results: list[dict]) -> float:
    probabilities = [float(item.get("fakeProbability", 0.5)) for item in frame_results]
    if not probabilities:
        return 0.5

    top_score = max(probabilities)
    central_score = median(probabilities)
    average_score = mean(probabilities)
    return round((0.45 * central_score) + (0.35 * average_score) + (0.20 * top_score), 4)


def _build_temporal_stats(frame_results: list[dict]) -> dict:
    probabilities = [float(item.get("fakeProbability", 0.5)) for item in frame_results]
    if not probabilities:
        return {
            "meanFakeProbability": 0,
            "medianFakeProbability": 0,
            "maxFakeProbability": 0,
            "minFakeProbability": 0,
            "temporalVariance": 0,
            "suspiciousFrameRatio": 0,
        }

    suspicious = [value for value in probabilities if value >= settings.SUSPICIOUS_FRAME_THRESHOLD]
    avg = mean(probabilities)
    variance = mean([(value - avg) ** 2 for value in probabilities])

    return {
        "meanFakeProbability": round(avg, 4),
        "medianFakeProbability": round(median(probabilities), 4),
        "maxFakeProbability": round(max(probabilities), 4),
        "minFakeProbability": round(min(probabilities), 4),
        "temporalVariance": round(variance, 4),
        "suspiciousFrameRatio": round((len(suspicious) / len(probabilities)) * 100, 2),
    }


def _build_suspicious_segments(
    frame_results: list[dict],
    threshold: float | None = None,
) -> list[dict]:
    threshold = settings.SUSPICIOUS_FRAME_THRESHOLD if threshold is None else threshold
    segments = []
    current = []

    for item in frame_results:
        if float(item.get("fakeProbability", 0.0)) >= threshold:
            current.append(item)
            continue

        if current:
            segments.append(current)
            current = []

    if current:
        segments.append(current)

    payload = []
    for segment in segments:
        probabilities = [float(item.get("fakeProbability", 0.0)) for item in segment]
        payload.append(
            {
                "startFrame": segment[0].get("frameIndex"),
                "endFrame": segment[-1].get("frameIndex"),
                "length": len(segment),
                "meanFakeProbability": round(mean(probabilities), 4),
                "maxFakeProbability": round(max(probabilities), 4),
            }
        )

    payload.sort(key=lambda item: (item["maxFakeProbability"], item["length"]), reverse=True)
    return payload[:5]


def _build_summary(
    frame_results: list[dict],
    model_used: bool,
    inference_mode: str,
    sequence_result: dict | None = None,
    embedding_similarity: dict | None = None,
    processing_times: dict | None = None,
) -> dict:
    if sequence_result:
        fake_probability = float(sequence_result.get("fakeProbability", 0.5))
        prediction = sequence_result["prediction"]
        confidence = sequence_result["confidence"]
    else:
        fake_probability = _aggregate_fake_probability(frame_results)
        prediction = PREDICTION_FAKE if fake_probability >= settings.FAKE_THRESHOLD else PREDICTION_REAL
        confidence = round((fake_probability if prediction == PREDICTION_FAKE else 1 - fake_probability) * 100, 2)

    suspicious_frames = sum(1 for item in frame_results if item["prediction"] == PREDICTION_FAKE)
    explanation = []
    for item in frame_results:
        for signal in item.get("signals", []):
            if signal not in explanation:
                explanation.append(signal)

    if inference_mode == "video_temporal_model":
        explanation.insert(0, "Temporal video model analyzed motion and frame consistency across the sampled sequence")
    elif model_used:
        explanation.insert(0, "Deep learning model inference was used for sampled face crops")
    else:
        explanation.insert(0, "No usable model artifact was available; deterministic forensic fallback was used")

    summary = {
        "prediction": prediction,
        "confidence": confidence,
        "riskLevel": calculate_risk_level(confidence, prediction),
        "riskScore": calculate_risk_score(confidence, prediction),
        "modelUsed": model_used,
        "inferenceMode": inference_mode,
        "totalFrames": len(frame_results),
        "suspiciousFrames": suspicious_frames,
        "focusAreas": FOCUS_AREAS,
        "explanation": explanation[:8],
        "frameResults": frame_results,
        "temporalStats": _build_temporal_stats(frame_results),
        "suspiciousSegments": _build_suspicious_segments(frame_results),
        "embeddingSimilarity": embedding_similarity,
        "processingTimes": processing_times or {},
        "fakeProbability": fake_probability,
        "realProbability": round(1 - fake_probability, 4),
        **decision_payload(fake_probability),
        "decisionThresholds": {
            "fakeProbability": settings.FAKE_THRESHOLD,
            "suspiciousFrame": settings.SUSPICIOUS_FRAME_THRESHOLD,
        },
    }
    if sequence_result:
        summary["sequenceLength"] = sequence_result.get("sequenceLength")
        summary["sequenceResult"] = sequence_result
    return summary


def run_deepfake_pipeline(frame_paths: list[str], analysis_id: str, is_video: bool = False) -> dict:
    if not frame_paths:
        raise ValueError("No frames were available for analysis.")
    if settings.REQUIRE_MODEL_IN_PRODUCTION and not settings.is_development and not is_model_ready():
        raise RuntimeError("Production analysis requires a usable deepfake model artifact.")

    timings = {}
    face_paths = []
    face_metadata = []
    stage_started = perf_counter()
    for order, frame_path in enumerate(frame_paths, start=1):
        face_path, metadata = save_face_crop(frame_path, analysis_id, order)
        face_paths.append(face_path)
        face_metadata.append(metadata)
    timings["faceDetectionMs"] = round((perf_counter() - stage_started) * 1000, 2)

    stage_started = perf_counter()
    sequence_result = run_video_sequence_inference(face_paths) if is_video else None
    timings["temporalInferenceMs"] = round((perf_counter() - stage_started) * 1000, 2) if is_video else 0

    stage_started = perf_counter()
    frame_results = run_batch_inference(face_paths)
    timings["frameInferenceMs"] = round((perf_counter() - stage_started) * 1000, 2)
    model_used = bool(sequence_result) or frame_results is not None
    inference_mode = (
        "video_temporal_model"
        if sequence_result
        else "deep_learning_model" if frame_results is not None else "forensic_fallback"
    )

    if frame_results is None:
        stage_started = perf_counter()
        frame_results = []
        for index, face_path in enumerate(face_paths, start=1):
            result = run_forensic_fallback(face_path)
            result["frameIndex"] = index
            result["filePath"] = face_path
            frame_results.append(result)
        timings["fallbackInferenceMs"] = round((perf_counter() - stage_started) * 1000, 2)
    else:
        timings["fallbackInferenceMs"] = 0

    for index, item in enumerate(frame_results):
        item["facePath"] = face_paths[index]
        item["face"] = face_metadata[index]
        item["framePath"] = frame_paths[index]

    stage_started = perf_counter()
    embedding_similarity = build_embedding_similarity(face_paths) if is_video else None
    timings["embeddingSimilarityMs"] = round((perf_counter() - stage_started) * 1000, 2) if is_video else 0

    stage_started = perf_counter()
    summary = _build_summary(
        frame_results,
        model_used=model_used,
        inference_mode=inference_mode,
        sequence_result=sequence_result,
        embedding_similarity=embedding_similarity,
        processing_times=timings,
    )
    summary["processingTimes"]["riskScoringMs"] = round((perf_counter() - stage_started) * 1000, 2)
    summary["sampledFaces"] = face_paths
    summary["faceDetections"] = face_metadata
    return summary
