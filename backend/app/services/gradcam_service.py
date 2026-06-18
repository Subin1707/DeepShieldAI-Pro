from pathlib import Path

import cv2
import numpy as np

from app.ai.face_detector import detect_largest_face
from app.ai.model_loader import infer_model_image_size, load_deepfake_model
from app.ai.preprocess import preprocess_image_file
from app.core.config import settings


DEFAULT_GRADCAM_LAYER = "top_activation"

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


def _smooth_resized_heatmap(heatmap: np.ndarray) -> np.ndarray:
    height, width = heatmap.shape[:2]
    sigma = max(4.0, min(width, height) * 0.045)
    return cv2.GaussianBlur(heatmap, (0, 0), sigmaX=sigma, sigmaY=sigma)


def _find_last_conv_layer_name(model):
    if hasattr(model, "layers"):
        for layer in reversed(model.layers):
            if hasattr(layer, "layers"):
                nested_layer_name = _find_last_conv_layer_name(layer)
                if nested_layer_name:
                    return nested_layer_name

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
            if hasattr(layer, "layers"):
                nested_layer_name = _find_last_conv_layer_name(layer)
                if nested_layer_name:
                    return nested_layer_name

            output = getattr(layer, "output", None)
            shape = getattr(output, "shape", None)
            if shape is not None and len(shape) == 4:
                return last_conv_layer_name
        except Exception:
            pass

        for layer in model.layers:
            if not hasattr(layer, "layers"):
                continue
            try:
                nested_layer = layer.get_layer(last_conv_layer_name)
                output = getattr(nested_layer, "output", None)
                shape = getattr(output, "shape", None)
                if shape is not None and len(shape) == 4:
                    return last_conv_layer_name
            except Exception:
                pass

    return _find_last_conv_layer_name(model)


def _call_layer(layer, inputs):
    try:
        return layer(inputs, training=False)
    except TypeError:
        return layer(inputs)


def _find_nested_model_with_layer(model, layer_name: str):
    for index, layer in enumerate(model.layers):
        if hasattr(layer, "layers"):
            try:
                nested_layer = layer.get_layer(layer_name)
                output = getattr(nested_layer, "output", None)
                shape = getattr(output, "shape", None)
                if shape is not None and len(shape) == 4:
                    return index, layer, nested_layer
            except Exception:
                pass
    return None


def make_gradcam_heatmap(img_array, model, last_conv_layer_name: str | None = DEFAULT_GRADCAM_LAYER):
    """
    Compute a class-discriminative Grad-CAM heatmap from the last convolutional
    activation map and the gradient of the predicted fake score.
    """
    import tensorflow as tf

    resolved_layer_name = _resolve_last_conv_layer_name(model, last_conv_layer_name)
    if not resolved_layer_name:
        available_layers = [layer.name for layer in model.layers]
        raise ValueError(f"No 4D convolution layer found for Grad-CAM. Available layers: {available_layers}")

    try:
        img_tensor = tf.cast(img_array, tf.float32)
        nested = _find_nested_model_with_layer(model, resolved_layer_name)

        if nested:
            nested_index, nested_model, target_layer = nested
            nested_grad_model = tf.keras.Model(
                nested_model.inputs,
                [target_layer.output, nested_model.output],
            )

            with tf.GradientTape() as tape:
                x = img_tensor
                for layer in model.layers[1:nested_index]:
                    x = _call_layer(layer, x)

                conv_outputs, x = nested_grad_model(x, training=False)
                tape.watch(conv_outputs)
                feature_tensor = x

                for layer in model.layers[nested_index + 1 :]:
                    if layer.__class__.__name__ == "Multiply":
                        x = _call_layer(layer, [feature_tensor, x])
                    else:
                        x = _call_layer(layer, x)

                predictions = x
                values = tf.reshape(predictions, (tf.shape(predictions)[0], -1))
                class_score = values[:, -1]
        else:
            target_layer = model.get_layer(resolved_layer_name)
            grad_model = tf.keras.Model(model.inputs, [target_layer.output, model.output])
            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(img_tensor, training=False)
                tape.watch(conv_outputs)
                values = tf.reshape(predictions, (tf.shape(predictions)[0], -1))
                class_score = values[:, -1]

        grads = tape.gradient(class_score, conv_outputs)
        if grads is None:
            return None

        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_sum(conv_outputs * pooled_grads, axis=-1)
        heatmap = tf.maximum(heatmap, 0).numpy()

        max_val = np.max(heatmap)
        if max_val <= 0:
            return None

        return (heatmap / max_val).astype("float32")

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Grad-CAM failed ({e}), falling back to saliency")
        return None


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
    image_size = infer_model_image_size(model, backend="keras")
    img = cv2.resize(img, (image_size, image_size))
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
        input_tensor = preprocess_image_file(source_path, image_size=loaded.image_size)
        heatmap = make_gradcam_heatmap(input_tensor, model, DEFAULT_GRADCAM_LAYER)
        if heatmap is None:
            # Grad-CAM returned None, saliency will be used as fallback
            return None
        return (heatmap * 255).astype(np.uint8)
    except Exception as exc:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Grad-CAM map building failed: {exc}")
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


def _face_ellipse_mask(shape: tuple[int, int], face_box: tuple[int, int, int, int]) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    fx, fy, fw, fh = _clip_box(face_box, width, height)
    center = (fx + fw // 2, fy + fh // 2)
    axes = (max(1, int(fw * 0.48)), max(1, int(fh * 0.56)))
    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
    return mask


def _mask_saliency_to_face(saliency: np.ndarray, face_box: tuple[int, int, int, int]) -> np.ndarray:
    mask = _face_ellipse_mask(saliency.shape[:2], face_box)
    masked = cv2.bitwise_and(saliency, saliency, mask=mask)
    max_value = int(np.max(masked))
    if max_value <= 0:
        return masked
    return cv2.normalize(masked, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def _metadata_face_box(image: np.ndarray, face_metadata: dict | None) -> tuple[int, int, int, int] | None:
    if not face_metadata or not face_metadata.get("faceDetected"):
        return None

    face_box = face_metadata.get("faceBbox")
    crop_size = face_metadata.get("cropSize") or {}
    if not face_box:
        return None

    try:
        source_width = float(crop_size.get("width") or 0)
        source_height = float(crop_size.get("height") or 0)
        x = float(face_box["x"])
        y = float(face_box["y"])
        box_width = float(face_box["width"])
        box_height = float(face_box["height"])
    except (TypeError, ValueError, KeyError):
        return None

    if source_width <= 0 or source_height <= 0 or box_width <= 0 or box_height <= 0:
        return None

    image_height, image_width = image.shape[:2]
    scale_x = image_width / source_width
    scale_y = image_height / source_height

    scaled_x = int(round(x * scale_x))
    scaled_y = int(round(y * scale_y))
    scaled_width = int(round(box_width * scale_x))
    scaled_height = int(round(box_height * scale_y))

    scaled_x = max(0, min(image_width - 1, scaled_x))
    scaled_y = max(0, min(image_height - 1, scaled_y))
    scaled_width = max(1, min(image_width - scaled_x, scaled_width))
    scaled_height = max(1, min(image_height - scaled_y, scaled_height))
    return scaled_x, scaled_y, scaled_width, scaled_height


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


def _clip_box(
    box: tuple[int, int, int, int],
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    x, y, box_width, box_height = box
    x = max(0, min(width - 1, int(x)))
    y = max(0, min(height - 1, int(y)))
    box_width = max(1, min(width - x, int(box_width)))
    box_height = max(1, min(height - y, int(box_height)))
    return x, y, box_width, box_height


def _box_overlap(candidate: tuple[int, int, int, int], reference: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = candidate
    bx, by, bw, bh = reference
    ax2 = ax + aw
    ay2 = ay + ah
    bx2 = bx + bw
    by2 = by + bh
    overlap_w = max(0, min(ax2, bx2) - max(ax, bx))
    overlap_h = max(0, min(ay2, by2) - max(ay, by))
    return (overlap_w * overlap_h) / max(1, aw * ah)


def _saliency_region_label(
    box: tuple[int, int, int, int],
    face_box: tuple[int, int, int, int],
    image_width: int,
    image_height: int,
) -> str:
    best_label = "High-saliency artifact"
    best_overlap = 0.0
    for part in _face_parts(face_box):
        if part["label"] == "Face boundary":
            continue
        part_box = _clip_box(part["bbox_px"], image_width, image_height)
        overlap = _box_overlap(box, part_box)
        if overlap > best_overlap:
            best_label = part["label"]
            best_overlap = overlap

    return best_label if best_overlap >= 0.18 else "High-saliency artifact"


def _normalized_bbox(
    box: tuple[int, int, int, int],
    image_width: int,
    image_height: int,
) -> dict:
    x, y, box_width, box_height = box
    return {
        "x": round(x / image_width, 4),
        "y": round(y / image_height, 4),
        "width": round(box_width / image_width, 4),
        "height": round(box_height / image_height, 4),
    }


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


def _score_region_saliency(crop: np.ndarray) -> float:
    if crop.size == 0:
        return 0.0

    mean_score = float(np.mean(crop) / 255.0) * 100
    peak_score = float(np.percentile(crop, 90) / 255.0) * 100
    return (mean_score * 0.65) + (peak_score * 0.35)


def _extract_face_part_regions(
    saliency: np.ndarray,
    face_box: tuple[int, int, int, int],
    include_boundary: bool = False,
) -> list[dict]:
    height, width = saliency.shape[:2]
    regions = []

    for part in _face_parts(face_box):
        if part["label"] == "Face boundary" and not include_boundary:
            continue

        box = _clip_box(part["bbox_px"], width, height)
        x, y, box_width, box_height = box
        crop = saliency[y : y + box_height, x : x + box_width]
        region = _region_payload(part["label"], _score_region_saliency(crop), _normalized_bbox(box, width, height))
        region["source"] = "face_part"
        regions.append(region)

    return regions


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
    selected = []
    face_parts = [region for region in regions if region.get("source") == "face_part"]
    face_parts.sort(key=lambda item: float(item.get("score", 0)), reverse=True)
    for region in face_parts:
        if region.get("rawLabel") == "Face boundary":
            continue
        selected.append(region)
        if len(selected) >= min(3, limit):
            break

    candidates = []
    fallback_candidates = []
    for region in regions:
        if region.get("source") == "face_part":
            continue
        if region.get("rawLabel") == "Face boundary" or _bbox_area(region) > 0.42:
            continue
        fallback_candidates.append(region)
        if float(region.get("score", 0)) >= minimum_score or region.get("rawLabel") == "High-saliency artifact":
            candidates.append(region)

    if not candidates:
        candidates = fallback_candidates[:]

    candidates.sort(key=lambda item: (float(item.get("score", 0)), -_bbox_area(item)), reverse=True)

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
    fx, fy, fw, fh = _clip_box(face_box, width, height)
    face_mask = _face_ellipse_mask(saliency.shape[:2], (fx, fy, fw, fh))
    saliency = cv2.bitwise_and(saliency, saliency, mask=face_mask)

    nonzero_saliency = saliency[saliency > 0]
    if nonzero_saliency.size == 0:
        return []

    part_regions = _extract_face_part_regions(saliency, (fx, fy, fw, fh)) if include_face_parts else []

    threshold_value = max(1, int(np.percentile(nonzero_saliency, 88)))
    _, mask = cv2.threshold(saliency, threshold_value, 255, cv2.THRESH_BINARY)
    kernel_size = max(3, int(min(width, height) * 0.025))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_regions = []
    face_area = max(1, fw * fh)
    min_area = max(12, int(face_area * 0.001))
    max_area = max(min_area + 1, int(face_area * 0.45))

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue

        x, y, box_width, box_height = _clip_box(cv2.boundingRect(contour), width, height)
        crop = saliency[y : y + box_height, x : x + box_width]
        score = _score_region_saliency(crop)
        label = _saliency_region_label((x, y, box_width, box_height), (fx, fy, fw, fh), width, height)
        region = _region_payload(label, score, _normalized_bbox((x, y, box_width, box_height), width, height))
        region["source"] = "hotspot"
        contour_regions.append(region)

    contour_regions.sort(key=lambda item: (item["score"], _bbox_area(item)), reverse=True)
    if contour_regions:
        return (part_regions + contour_regions[:limit])[:limit]

    max_value = int(np.max(saliency))
    if max_value <= 0:
        return part_regions[:limit]

    _, _, _, max_location = cv2.minMaxLoc(saliency)
    center_x, center_y = max_location
    hotspot_width = max(16, int(fw * 0.22))
    hotspot_height = max(16, int(fh * 0.18))
    hotspot_box = _clip_box(
        (
            center_x - hotspot_width // 2,
            center_y - hotspot_height // 2,
            hotspot_width,
            hotspot_height,
        ),
        width,
        height,
    )
    x, y, box_width, box_height = hotspot_box
    crop = saliency[y : y + box_height, x : x + box_width]
    score = _score_region_saliency(crop)
    label = _saliency_region_label(hotspot_box, (fx, fy, fw, fh), width, height)
    hotspot_region = _region_payload(label, score, _normalized_bbox(hotspot_box, width, height))
    hotspot_region["source"] = "hotspot"
    return (part_regions + [hotspot_region])[:limit]


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


def generate_saliency_heatmap(source_path: str, analysis_id: str, face_metadata: dict | None = None) -> dict:
    heatmap_dir = Path(settings.HEATMAP_DIR)
    heatmap_dir.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(source_path)
    if image is None:
        image = np.zeros((224, 224, 3), dtype=np.uint8)

    image = _resize_for_viewer(image)
    metadata_face_box = _metadata_face_box(image, face_metadata)
    detected_face_box = metadata_face_box or detect_largest_face(image)
    face_box = detected_face_box or _fallback_face_box(image)
    gradcam = _build_gradcam_map(source_path)
    if gradcam is not None:
        saliency = cv2.resize(gradcam, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_CUBIC)
        saliency = _smooth_resized_heatmap(saliency)
        saliency = np.uint8(255 * _normalize_heatmap(saliency))
        method = "Grad-CAM"
    else:
        saliency = _build_saliency_map(image)
        method = "saliency_fallback"

    saliency = _mask_saliency_to_face(saliency, face_box)
    heatmap = cv2.applyColorMap(saliency, cv2.COLORMAP_TURBO)
    overlay = cv2.addWeighted(image, 0.56, heatmap, 0.44, 0)
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
        "faceBoxSource": "metadata" if metadata_face_box is not None else "detector" if detected_face_box is not None else "image_fallback",
        "method": method,
    }


def generate_demo_heatmap(source_path: str, analysis_id: str) -> dict:
    return generate_saliency_heatmap(source_path, analysis_id)


def build_heatmap_url(analysis_id: str) -> str:
    return f"/storage/heatmaps/{analysis_id}.jpg"
