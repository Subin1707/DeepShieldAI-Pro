from pathlib import Path

import cv2
import numpy as np

from app.ai.face_detector import detect_largest_face
from app.ai.model_loader import load_deepfake_model
from app.ai.preprocess import preprocess_image_file
from app.core.config import settings


DEFAULT_GRADCAM_LAYER = "top_conv"

VI_REGION_LABELS = {
    "Eye region": "Vùng mắt",
    "Nose region": "Vùng mũi",
    "Mouth region": "Vùng miệng",
    "Face boundary": "Viền khuôn mặt",
    "High-saliency artifact": "Điểm bất thường nổi bật",
}

REGION_EXPLANATIONS = {
    "Eye region": {
        "reason": "Vùng mắt thường để lộ dấu hiệu ghép mặt như mí mắt méo, phản chiếu ánh sáng không đều hoặc chuyển động chớp mắt thiếu tự nhiên.",
        "manualCheck": "Phóng to vùng mắt, so sánh hai mắt, mí mắt và phản chiếu ánh sáng qua vài frame liên tiếp.",
    },
    "Nose region": {
        "reason": "Vùng mũi dễ xuất hiện nhiễu texture, sai lệch bóng đổ hoặc biến dạng nhẹ khi khuôn mặt tổng hợp không ổn định.",
        "manualCheck": "Kiểm tra sống mũi, bóng mũi và vùng chuyển tiếp giữa mũi với má trong các frame gần nhau.",
    },
    "Mouth region": {
        "reason": "Vùng miệng hay lỗi khi đồng bộ khẩu hình, răng, môi hoặc đường viền miệng trong video deepfake.",
        "manualCheck": "Xem chậm đoạn có nói chuyện, chú ý viền môi, răng và độ khớp giữa âm thanh với khẩu hình.",
    },
    "Face boundary": {
        "reason": "Viền khuôn mặt là nơi ghép mặt với nền gốc, nên dễ có viền sáng, méo cạnh, sai màu da hoặc ranh giới không tự nhiên.",
        "manualCheck": "Kiểm tra vùng cằm, má, tóc và cổ; nếu viền mặt rung hoặc lệch màu giữa các frame thì cần cảnh giác.",
    },
    "High-saliency artifact": {
        "reason": "Đây là vùng có tín hiệu saliency cao: cạnh ảnh, nhiễu tần số cao hoặc texture khác thường so với vùng xung quanh.",
        "manualCheck": "Phóng to vùng được khoanh, so sánh với frame trước/sau để xem bất thường có lặp lại hay chỉ là nhiễu nén video.",
    },
}


def _normalize_heatmap(heatmap):
    max_value = np.max(heatmap)
    if max_value <= 0:
        return np.zeros_like(heatmap, dtype="float32")
    return (heatmap / max_value).astype("float32")


def _find_last_conv_layer_name(model):
    for layer in reversed(model.layers):
        output = getattr(layer, "output", None)
        shape = getattr(output, "shape", None)
        if shape is not None and len(shape) == 4:
            return layer.name
    return None


def _resolve_last_conv_layer_name(model, last_conv_layer_name: str | None = DEFAULT_GRADCAM_LAYER):
    if last_conv_layer_name:
        try:
            layer = model.get_layer(last_conv_layer_name)
            output = getattr(layer, "output", None)
            shape = getattr(output, "shape", None)
            if shape is not None and len(shape) == 4:
                return last_conv_layer_name
        except Exception:
            pass

    return _find_last_conv_layer_name(model)


def make_gradcam_heatmap(img_array, model, last_conv_layer_name: str | None = DEFAULT_GRADCAM_LAYER):
    import tensorflow as tf

    resolved_layer_name = _resolve_last_conv_layer_name(model, last_conv_layer_name)
    if not resolved_layer_name:
        available_layers = [layer.name for layer in model.layers]
        raise ValueError(f"No 4D convolution layer found for Grad-CAM. Available layers: {available_layers}")

    grad_model = tf.keras.models.Model(
        model.inputs,
        [model.get_layer(resolved_layer_name).output, model.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array, training=False)
        values = tf.reshape(predictions, (tf.shape(predictions)[0], -1))
        loss = values[:, -1]

    grads = tape.gradient(loss, conv_outputs)
    if grads is None:
        raise ValueError("Grad-CAM gradients are empty for this model output.")

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0)
    max_value = tf.reduce_max(heatmap)
    if float(max_value.numpy()) <= 0:
        return np.zeros(tuple(heatmap.shape), dtype="float32")

    heatmap = heatmap / max_value
    return heatmap.numpy()


def save_gradcam(
    image_path: str,
    model,
    output_path: str,
    last_conv_layer_name: str | None = DEFAULT_GRADCAM_LAYER,
) -> str:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image for Grad-CAM: {image_path}")

    original = img.copy()
    img = cv2.resize(img, (settings.IMAGE_MODEL_SIZE, settings.IMAGE_MODEL_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_array = np.expand_dims(img / 255.0, axis=0).astype("float32")

    heatmap = make_gradcam_heatmap(img_array, model, last_conv_layer_name)
    heatmap = cv2.resize(heatmap, (original.shape[1], original.shape[0]))
    heatmap = np.uint8(255 * _normalize_heatmap(heatmap))
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(original, 0.6, heatmap, 0.4, 0)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), overlay)
    return str(output)


def _build_saliency_map(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 2.5)
    residual = cv2.absdiff(gray, blur)
    edges = cv2.Canny(gray, 80, 180)
    saliency = cv2.addWeighted(residual, 0.7, edges, 0.3, 0)
    saliency = cv2.GaussianBlur(saliency, (9, 9), 0)
    return cv2.normalize(saliency, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def _build_gradcam_map(source_path: str) -> np.ndarray | None:
    loaded = load_deepfake_model()
    if loaded is None or loaded.backend != "keras":
        return None

    try:
        import tensorflow as tf
    except ImportError:
        return None

    model = loaded.model

    try:
        input_tensor = preprocess_image_file(source_path)
        heatmap = make_gradcam_heatmap(input_tensor, model, DEFAULT_GRADCAM_LAYER)
        return (heatmap * 255).astype(np.uint8)
    except Exception as exc:
        print("Grad-CAM generation error:", exc)
        return None


def _resize_for_viewer(image: np.ndarray, max_side: int = 960) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_side:
        return image

    scale = max_side / longest
    target = (max(1, int(width * scale)), max(1, int(height * scale)))
    return cv2.resize(image, target, interpolation=cv2.INTER_AREA)


def _fallback_face_box(image: np.ndarray) -> tuple[int, int, int, int]:
    height, width = image.shape[:2]
    pad_x = max(1, int(width * 0.04))
    pad_y = max(1, int(height * 0.04))
    return (
        pad_x,
        pad_y,
        max(1, width - (pad_x * 2)),
        max(1, height - (pad_y * 2)),
    )


def _face_parts(face_box: tuple[int, int, int, int]) -> list[dict]:
    x, y, width, height = face_box
    return [
        {
            "label": "Eye region",
            "bbox_px": (int(x + width * 0.16), int(y + height * 0.20), int(width * 0.68), int(height * 0.22)),
        },
        {
            "label": "Nose region",
            "bbox_px": (int(x + width * 0.34), int(y + height * 0.38), int(width * 0.32), int(height * 0.24)),
        },
        {
            "label": "Mouth region",
            "bbox_px": (int(x + width * 0.26), int(y + height * 0.62), int(width * 0.48), int(height * 0.20)),
        },
        {
            "label": "Face boundary",
            "bbox_px": (int(x + width * 0.04), int(y + height * 0.08), int(width * 0.92), int(height * 0.86)),
        },
    ]


def _severity(score: float) -> str:
    if score >= 60:
        return "Cao"
    if score >= 35:
        return "Trung bình"
    return "Thấp"


def _region_payload(label: str, score: float, bbox: dict) -> dict:
    explanation = REGION_EXPLANATIONS.get(label, REGION_EXPLANATIONS["High-saliency artifact"])
    return {
        "label": VI_REGION_LABELS.get(label, label),
        "rawLabel": label,
        "score": round(score, 2),
        "severity": _severity(score),
        "reason": explanation["reason"],
        "manualCheck": explanation["manualCheck"],
        "bbox": bbox,
    }


def _bbox_area(region: dict) -> float:
    box = region.get("bbox") or {}
    return float(box.get("width", 0)) * float(box.get("height", 0))


def _bbox_overlap_ratio(candidate: dict, selected: list[dict]) -> float:
    box = candidate.get("bbox") or {}
    ax1 = float(box.get("x", 0))
    ay1 = float(box.get("y", 0))
    ax2 = ax1 + float(box.get("width", 0))
    ay2 = ay1 + float(box.get("height", 0))
    area = max(1e-6, (ax2 - ax1) * (ay2 - ay1))

    max_overlap = 0.0
    for item in selected:
        other = item.get("bbox") or {}
        bx1 = float(other.get("x", 0))
        by1 = float(other.get("y", 0))
        bx2 = bx1 + float(other.get("width", 0))
        by2 = by1 + float(other.get("height", 0))
        overlap_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
        overlap_h = max(0.0, min(ay2, by2) - max(ay1, by1))
        max_overlap = max(max_overlap, (overlap_w * overlap_h) / area)
    return max_overlap


def _select_overlay_regions(regions: list[dict], limit: int = 4, minimum_score: float = 8.0) -> list[dict]:
    candidates = []
    fallback_candidates = []
    for region in regions:
        if region.get("rawLabel") == "Face boundary" or _bbox_area(region) > 0.42:
            continue
        fallback_candidates.append(region)
        if float(region.get("score", 0)) >= minimum_score or region.get("rawLabel") == "High-saliency artifact":
            candidates.append(region)

    if not candidates:
        candidates = fallback_candidates[:]

    candidates.sort(key=lambda item: (float(item.get("score", 0)), -_bbox_area(item)), reverse=True)

    selected = []
    for region in candidates:
        if _bbox_overlap_ratio(region, selected) > 0.48:
            continue
        selected.append(region)
        if len(selected) >= limit:
            break
    return selected


def _extract_suspicious_regions(
    saliency: np.ndarray,
    face_box: tuple[int, int, int, int] | None,
    limit: int = 6,
    include_face_parts: bool = True,
) -> list[dict]:
    height, width = saliency.shape[:2]
    if face_box is None:
        return []

    face_mask = np.zeros_like(saliency, dtype=np.uint8)
    fx, fy, fw, fh = face_box
    cv2.rectangle(face_mask, (fx, fy), (min(width - 1, fx + fw), min(height - 1, fy + fh)), 255, -1)
    saliency = cv2.bitwise_and(saliency, saliency, mask=face_mask)

    part_regions = []
    if include_face_parts:
        for part in _face_parts(face_box):
            x, y, box_width, box_height = part["bbox_px"]
            x = max(0, min(width - 1, x))
            y = max(0, min(height - 1, y))
            box_width = max(1, min(width - x, box_width))
            box_height = max(1, min(height - y, box_height))
            crop = saliency[y : y + box_height, x : x + box_width]
            score = float(np.mean(crop) / 255.0) * 100
            bbox = {
                "x": round(x / width, 4),
                "y": round(y / height, 4),
                "width": round(box_width / width, 4),
                "height": round(box_height / height, 4),
            }
            part_regions.append(_region_payload(part["label"], score, bbox))

    threshold_value = max(90, int(np.percentile(saliency, 92)))
    _, mask = cv2.threshold(saliency, threshold_value, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_regions = []
    min_area = max(40, int(width * height * 0.002))

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        x, y, box_width, box_height = cv2.boundingRect(contour)
        crop = saliency[y : y + box_height, x : x + box_width]
        score = float(np.mean(crop) / 255.0) * 100
        bbox = {
            "x": round(x / width, 4),
            "y": round(y / height, 4),
            "width": round(box_width / width, 4),
            "height": round(box_height / height, 4),
        }
        contour_regions.append(_region_payload("High-saliency artifact", score, bbox))

    part_regions.sort(key=lambda item: item["score"], reverse=True)
    contour_regions.sort(key=lambda item: item["score"], reverse=True)
    return (part_regions[:4] + contour_regions[:limit])[:6]


def _region_color(score: float) -> tuple[int, int, int]:
    if score >= 60:
        return (56, 87, 248)
    if score >= 35:
        return (0, 204, 255)
    return (34, 211, 238)


def _draw_number_badge(
    image: np.ndarray,
    number: int,
    center: tuple[int, int],
    color: tuple[int, int, int],
    radius: int,
) -> None:
    x, y = center
    font_scale = max(0.34, radius / 28)
    thickness = 1 if radius <= 13 else 2
    cv2.circle(image, (x, y), radius, (2, 6, 23), -1, lineType=cv2.LINE_AA)
    cv2.circle(image, (x, y), radius, color, thickness, lineType=cv2.LINE_AA)
    text = str(number)
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    cv2.putText(
        image,
        text,
        (x - text_size[0] // 2, y + text_size[1] // 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        lineType=cv2.LINE_AA,
    )


def _draw_region_annotations(overlay: np.ndarray, regions: list[dict]) -> np.ndarray:
    annotated = overlay.copy()
    height, width = annotated.shape[:2]
    line_thickness = 1 if min(width, height) < 360 else 2
    badge_radius = max(9, min(15, int(min(width, height) * 0.045)))

    for index, region in enumerate(regions, start=1):
        region["overlayIndex"] = index
        box = region["bbox"]
        x = int(box["x"] * width)
        y = int(box["y"] * height)
        box_width = int(box["width"] * width)
        box_height = int(box["height"] * height)
        x2 = min(width - 1, x + box_width)
        y2 = min(height - 1, y + box_height)
        color = _region_color(region["score"])

        cv2.rectangle(annotated, (x, y), (x2, y2), color, line_thickness, lineType=cv2.LINE_AA)
        badge_x = min(width - badge_radius - 2, max(badge_radius + 2, x + badge_radius + 3))
        badge_y = min(height - badge_radius - 2, max(badge_radius + 2, y + badge_radius + 3))
        _draw_number_badge(annotated, index, (badge_x, badge_y), color, badge_radius)

    return annotated


def _draw_face_box(image: np.ndarray, face_box: tuple[int, int, int, int] | None) -> np.ndarray:
    annotated = image.copy()
    if face_box is None:
        return annotated

    x, y, width, height = face_box
    cv2.rectangle(annotated, (x, y), (x + width, y + height), (34, 211, 238), 1, lineType=cv2.LINE_AA)
    return annotated


def generate_saliency_heatmap(source_path: str, analysis_id: str) -> dict:
    heatmap_dir = Path(settings.HEATMAP_DIR)
    heatmap_dir.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(source_path)
    if image is None:
        image = np.zeros((224, 224, 3), dtype=np.uint8)

    image = _resize_for_viewer(image)
    detected_face_box = detect_largest_face(image)
    face_box = detected_face_box or _fallback_face_box(image)
    gradcam = _build_gradcam_map(source_path)
    if gradcam is not None:
        saliency = cv2.resize(gradcam, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_CUBIC)
        method = "Grad-CAM"
    else:
        saliency = _build_saliency_map(image)
        method = "saliency_fallback"

    heatmap = cv2.applyColorMap(saliency, cv2.COLORMAP_TURBO)
    overlay = cv2.addWeighted(image, 0.78, heatmap, 0.22, 0)
    if detected_face_box is not None:
        overlay = _draw_face_box(overlay, detected_face_box)
    candidate_regions = _extract_suspicious_regions(
        saliency,
        face_box,
        include_face_parts=detected_face_box is not None,
    )
    annotated_regions = _select_overlay_regions(candidate_regions)
    overlay = _draw_region_annotations(overlay, annotated_regions)

    output_path = heatmap_dir / f"{analysis_id}.jpg"
    cv2.imwrite(str(output_path), overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    return {
        "path": str(output_path),
        "regions": annotated_regions,
        "candidateRegionCount": len(candidate_regions),
        "faceDetected": detected_face_box is not None,
        "faceBoxSource": "detector" if detected_face_box is not None else "image_fallback",
        "method": method,
    }


def generate_demo_heatmap(source_path: str, analysis_id: str) -> dict:
    return generate_saliency_heatmap(source_path, analysis_id)


def build_heatmap_url(analysis_id: str) -> str:
    return f"/storage/heatmaps/{analysis_id}.jpg"
