from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from PIL import ExifTags, Image

from app.ai.labels import decision_payload
from app.ai.face_detector import detect_largest_face
from app.core.config import settings

AI_SOFTWARE_HINTS = (
    "gemini",
    "midjourney",
    "stable diffusion",
    "stability",
    "dall",
    "openai",
    "firefly",
    "leonardo",
    "comfyui",
    "automatic1111",
    "invokeai",
)

STRICT_SUSPICION_THRESHOLD = settings.FORENSIC_STRICT_THRESHOLD


def run_hybrid_forensics(file_path: str, frame_paths: list[str] | None = None) -> dict:
    frame_paths = frame_paths or []
    image_paths = [file_path] if _is_image(file_path) else frame_paths[:5]
    image_paths = [path for path in image_paths if path]

    timings = {}
    stage_started = perf_counter()
    metadata = analyze_metadata(file_path)
    timings["metadataForensicsMs"] = round((perf_counter() - stage_started) * 1000, 2)

    stage_started = perf_counter()
    frequency_items = [analyze_frequency(path) for path in image_paths]
    timings["frequencyAnalysisMs"] = round((perf_counter() - stage_started) * 1000, 2)

    stage_started = perf_counter()
    artifact_items = [analyze_artifacts(path) for path in image_paths]
    timings["artifactDetectionMs"] = round((perf_counter() - stage_started) * 1000, 2)

    frequency = _aggregate_scores("frequency", frequency_items, "FFT Frequency Analysis")
    artifacts = _aggregate_scores("artifacts", artifact_items, "AI Artifact Detection")
    generated_portrait = analyze_generated_portrait(file_path, metadata, frequency, artifacts)

    component_scores = [metadata["score"], frequency["score"], artifacts["score"], generated_portrait["score"]]
    strong_components = sum(1 for score in component_scores if score >= STRICT_SUSPICION_THRESHOLD)
    ensemble_bonus = 10 if strong_components >= 2 else 0
    generated_media_bonus = (
        15
        if metadata["score"] >= 70 and frequency["score"] >= 40 and generated_portrait["score"] >= 40
        else 0
    )
    risk_score = round(
        min(
            100,
            (0.30 * metadata["score"])
            + (0.23 * frequency["score"])
            + (0.30 * artifacts["score"])
            + (0.17 * generated_portrait["score"])
            + ensemble_bonus
            + generated_media_bonus,
        ),
        2,
    )
    signals = metadata["signals"] + frequency["signals"] + artifacts["signals"] + generated_portrait["signals"]
    if generated_media_bonus:
        signals.append("Multiple moderate generated-media signals reinforce the AI-generated portrait suspicion")

    return {
        "metadata": metadata,
        "frequency": frequency,
        "artifacts": artifacts,
        "generatedPortrait": generated_portrait,
        "riskScore": risk_score,
        "strictMode": True,
        "strongComponentCount": strong_components,
        "generatedMediaBonus": generated_media_bonus,
        "signals": signals[:10],
        "processingTimes": timings,
    }


def fuse_deepfake_and_forensics(result: dict, hybrid: dict) -> dict:
    model_fake = float(result.get("fakeProbability", 0.5))
    model_risk = float(result.get("riskScore", 0))
    forensic_risk = float(hybrid.get("riskScore", 0))

    metadata_score = float((hybrid.get("metadata") or {}).get("score", 0))
    frequency_score = float((hybrid.get("frequency") or {}).get("score", 0))
    artifact_score = float((hybrid.get("artifacts") or {}).get("score", 0))
    portrait_score = float((hybrid.get("generatedPortrait") or {}).get("score", 0))
    strict_bonus = 8 if sum(score >= STRICT_SUSPICION_THRESHOLD for score in (metadata_score, frequency_score, artifact_score, portrait_score)) >= 2 else 0
    forensic_weighted = (model_fake * 100 * 0.35) + (forensic_risk * 0.65) + strict_bonus
    final_risk = round(min(100, max(model_risk, forensic_weighted, forensic_risk)), 2)
    final_fake_probability = round(max(model_fake, final_risk / 100), 4)
    final_prediction = "FAKE" if final_risk >= STRICT_SUSPICION_THRESHOLD else result.get("prediction", "REAL")
    final_confidence = round(final_risk if final_prediction == "FAKE" else max(0, 100 - final_risk), 2)

    fused = dict(result)
    fused["modelPrediction"] = result.get("prediction")
    fused["modelConfidence"] = result.get("confidence")
    fused["modelRiskScore"] = result.get("riskScore")
    fused["hybridForensics"] = hybrid
    fused["fusion"] = {
        "modelFakeProbability": model_fake,
        "forensicRiskScore": forensic_risk,
        "finalRiskScore": final_risk,
        "strictThreshold": STRICT_SUSPICION_THRESHOLD,
        "strictBonus": strict_bonus,
        "method": "strict max(model risk, 35% CNN + 65% metadata/FFT/artifact forensic risk + ensemble bonus)",
    }
    fused["prediction"] = final_prediction
    fused["confidence"] = final_confidence
    fused["riskScore"] = int(round(final_risk))
    fused["riskLevel"] = _risk_level(final_risk, final_prediction)
    fused["fakeProbability"] = final_fake_probability
    fused["realProbability"] = round(1 - final_fake_probability, 4)
    fused.update(decision_payload(final_fake_probability))

    explanation = list(fused.get("explanation") or [])
    for signal in hybrid.get("signals", [])[:5]:
        if signal not in explanation:
            explanation.append(signal)
    fused["explanation"] = explanation[:10]
    return fused


def analyze_metadata(file_path: str) -> dict:
    signals = []
    score = 0.0
    fields = {}

    try:
        with Image.open(file_path) as image:
            raw_exif = image.getexif()
            if raw_exif:
                for key, value in raw_exif.items():
                    label = ExifTags.TAGS.get(key, str(key))
                    fields[label] = str(value)[:160]
            info = {key: str(value)[:160] for key, value in image.info.items() if key.lower() not in {"icc_profile"}}
            fields.update(info)
    except Exception as exc:
        signals.append(f"Metadata could not be parsed: {exc}")
        score += 15

    software = " ".join(str(fields.get(key, "")) for key in ("Software", "Creator", "Description", "parameters", "comment")).lower()
    if any(hint in software for hint in AI_SOFTWARE_HINTS):
        signals.append("Metadata software field contains AI-generation tool hint")
        score += 95

    filename = Path(file_path).name.lower()
    if any(hint in filename for hint in AI_SOFTWARE_HINTS):
        signals.append("Filename contains AI-generation tool hint")
        score += 85

    camera_fields = ["Make", "Model", "LensModel", "DateTimeOriginal", "FocalLength", "ExposureTime"]
    present_camera_fields = [field for field in camera_fields if fields.get(field)]
    if not fields:
        signals.append("No EXIF metadata found; many camera originals include capture metadata")
        score += 55
    elif len(present_camera_fields) <= 1:
        signals.append("Camera capture metadata is sparse or missing")
        score += 35

    if Path(file_path).suffix.lower() in {".png", ".webp"} and not present_camera_fields:
        signals.append("Image format and metadata pattern are consistent with exported/generated media")
        score += 18

    if fields and not fields.get("DateTimeOriginal") and not fields.get("DateTimeDigitized"):
        signals.append("Original capture timestamp is missing")
        score += 12

    if not signals:
        signals.append("Metadata does not contain strong AI-generation indicators")

    return {
        "name": "Metadata Forensics",
        "score": round(min(score, 100), 2),
        "signals": signals,
        "fields": fields,
    }


def analyze_frequency(file_path: str) -> dict:
    image = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return {"score": 0, "signals": ["FFT skipped because image could not be read"]}

    image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)
    spectrum = np.fft.fftshift(np.fft.fft2(image.astype(np.float32)))
    magnitude = np.log1p(np.abs(spectrum))
    magnitude = cv2.normalize(magnitude, None, 0, 1, cv2.NORM_MINMAX)

    height, width = magnitude.shape
    y, x = np.indices((height, width))
    center_y, center_x = height // 2, width // 2
    radius = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    max_radius = np.max(radius)

    high_band = magnitude[radius > max_radius * 0.62]
    mid_band = magnitude[(radius > max_radius * 0.22) & (radius <= max_radius * 0.62)]
    low_band = magnitude[radius <= max_radius * 0.22]

    high_ratio = float(np.mean(high_band) / (np.mean(mid_band) + 1e-6))
    grid_energy = float(np.std(np.mean(magnitude, axis=0)) + np.std(np.mean(magnitude, axis=1)))
    radial_smoothness = float(1.0 / (np.std(mid_band) + 1e-6))

    high_signal = np.clip((high_ratio - 0.72) / 0.36, 0, 1)
    grid_signal = np.clip((grid_energy - 0.055) / 0.14, 0, 1)
    smooth_signal = np.clip((radial_smoothness - 4.8) / 7.2, 0, 1)
    score = float((0.42 * high_signal + 0.30 * grid_signal + 0.28 * smooth_signal) * 100)

    signals = []
    if high_signal > 0.35:
        signals.append("FFT shows elevated high-frequency synthetic residuals")
    if grid_signal > 0.35:
        signals.append("Frequency spectrum contains grid-like periodic energy")
    if smooth_signal > 0.35:
        signals.append("Frequency bands are unusually smooth for natural camera capture")
    if not signals:
        signals.append("FFT spectrum does not show strong synthetic frequency artifacts")

    return {
        "score": round(score, 2),
        "signals": signals,
        "features": {
            "highFrequencyRatio": round(high_ratio, 4),
            "gridEnergy": round(grid_energy, 4),
            "radialSmoothness": round(radial_smoothness, 4),
            "lowBandMean": round(float(np.mean(low_band)), 4),
        },
    }


def _edge_chroma_features(image: np.ndarray) -> dict:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 70, 170) > 0
    if not np.any(edges):
        return {"edgeChroma": 0.0, "backgroundChroma": 0.0, "edgeChromaLift": 0.0}

    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    chroma_delta = (np.abs(red - green) + np.abs(blue - green)) / 510.0
    dilated_edges = cv2.dilate(edges.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    background = ~dilated_edges
    edge_chroma = float(np.mean(chroma_delta[dilated_edges]))
    background_chroma = float(np.mean(chroma_delta[background])) if np.any(background) else 0.0
    return {
        "edgeChroma": edge_chroma,
        "backgroundChroma": background_chroma,
        "edgeChromaLift": max(0.0, edge_chroma - background_chroma),
    }


def analyze_generated_portrait(file_path: str, metadata: dict, frequency: dict, artifacts: dict) -> dict:
    image = cv2.imread(str(file_path))
    if image is None:
        return {"score": 0, "signals": ["Generated portrait analysis skipped because image could not be read"]}

    image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)
    face_box = detect_largest_face(image)
    if face_box is None:
        return {
            "score": 0,
            "signals": ["Generated portrait analysis skipped because no clear face was detected"],
            "features": {"faceDetected": False},
        }

    x, y, width, height = face_box
    face_area_ratio = float((width * height) / (image.shape[0] * image.shape[1]))
    face_crop = image[y : y + height, x : x + width]
    gray_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    high_pass = cv2.absdiff(gray_face, cv2.GaussianBlur(gray_face, (0, 0), 2.0))
    face_residual_std = float(np.std(high_pass))
    face_lap_var = float(cv2.Laplacian(gray_face, cv2.CV_64F).var())
    edge_chroma = _edge_chroma_features(image)

    metadata_signal = np.clip(float(metadata.get("score", 0)) / 75.0, 0, 1)
    artifact_signal = np.clip(float(artifacts.get("score", 0)) / 70.0, 0, 1)
    frequency_signal = np.clip(float(frequency.get("score", 0)) / 70.0, 0, 1)
    portrait_signal = np.clip((face_area_ratio - 0.12) / 0.18, 0, 1)
    smooth_face_signal = np.clip((11.0 - face_residual_std) / 11.0, 0, 1)
    edge_chroma_signal = np.clip((edge_chroma["edgeChromaLift"] - 0.018) / 0.055, 0, 1)
    sharp_face_signal = np.clip((face_lap_var - 130) / 520, 0, 1)

    score = float(
        (
            0.18 * metadata_signal
            + 0.18 * artifact_signal
            + 0.14 * frequency_signal
            + 0.14 * portrait_signal
            + 0.18 * smooth_face_signal
            + 0.12 * edge_chroma_signal
            + 0.06 * sharp_face_signal
        )
        * 100
    )

    signals = []
    if metadata_signal > 0.45:
        signals.append("Portrait image lacks strong camera provenance metadata")
    if smooth_face_signal > 0.35:
        signals.append("Face texture is unusually smooth for a natural camera portrait")
    if edge_chroma_signal > 0.35:
        signals.append("Color fringing around high-contrast edges is elevated")
    if artifact_signal > 0.45 or frequency_signal > 0.45:
        signals.append("Portrait-level forensic signals align with generated image patterns")
    if not signals:
        signals.append("Generated portrait consistency did not find strong synthetic portrait signals")

    return {
        "name": "Generated Portrait Consistency",
        "score": round(min(score, 100), 2),
        "signals": signals,
        "features": {
            "faceDetected": True,
            "faceAreaRatio": round(face_area_ratio, 4),
            "faceResidualStd": round(face_residual_std, 4),
            "faceLaplacianVariance": round(face_lap_var, 4),
            "edgeChroma": round(edge_chroma["edgeChroma"], 4),
            "backgroundChroma": round(edge_chroma["backgroundChroma"], 4),
            "edgeChromaLift": round(edge_chroma["edgeChromaLift"], 4),
        },
    }


def analyze_artifacts(file_path: str) -> dict:
    image = cv2.imread(str(file_path))
    if image is None:
        return {"score": 0, "signals": ["Artifact analysis skipped because image could not be read"]}

    image = cv2.resize(image, (384, 384), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    high_pass = cv2.absdiff(gray, cv2.GaussianBlur(gray, (0, 0), 2.0))
    residual_std = float(np.std(high_pass))
    saturation_std = float(np.std(hsv[:, :, 1]))
    local_std = cv2.blur((gray.astype(np.float32) - cv2.blur(gray.astype(np.float32), (17, 17))) ** 2, (17, 17))
    smooth_area_ratio = float(np.mean(local_std < 28))
    edge_density = float(np.mean(cv2.Canny(gray, 80, 180) > 0))
    edge_chroma = _edge_chroma_features(image)

    smooth_signal = np.clip((smooth_area_ratio - 0.28) / 0.34, 0, 1)
    low_noise_signal = np.clip((10.5 - residual_std) / 10.5, 0, 1)
    sharpness_signal = np.clip((lap_var - 120) / 430, 0, 1)
    color_signal = np.clip((saturation_std - 38) / 46, 0, 1)
    edge_signal = np.clip((edge_density - 0.085) / 0.15, 0, 1)
    edge_chroma_signal = np.clip((edge_chroma["edgeChromaLift"] - 0.018) / 0.055, 0, 1)

    score = float(
        (
            0.25 * smooth_signal
            + 0.19 * low_noise_signal
            + 0.16 * sharpness_signal
            + 0.14 * color_signal
            + 0.13 * edge_signal
            + 0.13 * edge_chroma_signal
        )
        * 100
    )

    signals = []
    if smooth_signal > 0.35:
        signals.append("Large regions are unusually smooth compared with natural camera texture")
    if low_noise_signal > 0.35:
        signals.append("High-pass residual noise is lower than expected for camera capture")
    if sharpness_signal > 0.35:
        signals.append("Local sharpness/edge pattern may indicate synthetic rendering")
    if color_signal > 0.35:
        signals.append("Color saturation variance is elevated")
    if edge_signal > 0.35:
        signals.append("Dense edge transitions may indicate generated background/object detail")
    if edge_chroma_signal > 0.35:
        signals.append("Color fringing around high-contrast edges is elevated")
    if not signals:
        signals.append("AI artifact detector did not find strong synthetic rendering clues")

    return {
        "score": round(score, 2),
        "signals": signals,
        "features": {
            "smoothAreaRatio": round(smooth_area_ratio, 4),
            "residualStd": round(residual_std, 4),
            "laplacianVariance": round(lap_var, 4),
            "saturationStd": round(saturation_std, 4),
            "edgeDensity": round(edge_density, 4),
            "edgeChromaLift": round(edge_chroma["edgeChromaLift"], 4),
        },
    }


def _aggregate_scores(key: str, items: list[dict], name: str) -> dict:
    valid = [item for item in items if item]
    if not valid:
        return {"name": name, "score": 0, "signals": [f"{name} did not run"], "items": []}

    score = round(float(np.mean([float(item.get("score", 0)) for item in valid])), 2)
    signals = []
    for item in valid:
        for signal in item.get("signals", []):
            if signal not in signals:
                signals.append(signal)

    return {
        "name": name,
        "score": score,
        "signals": signals[:6],
        "items": valid,
        "key": key,
    }


def _risk_level(score: float, prediction: str) -> str:
    if prediction != "FAKE":
        return "LOW"
    if score >= 90:
        return "CRITICAL"
    if score >= 75:
        return "HIGH"
    if score >= STRICT_SUSPICION_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def _is_image(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
