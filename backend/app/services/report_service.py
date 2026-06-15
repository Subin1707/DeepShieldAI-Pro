import json
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.utils.id_utils import generate_report_id


PREDICTION_LABELS = {
    "FAKE": "Có dấu hiệu giả mạo",
    "REAL": "Chưa thấy dấu hiệu giả mạo rõ",
    "UNKNOWN": "Cần xem xét thêm",
}

RISK_LABELS = {
    "LOW": "Thấp",
    "MEDIUM": "Trung bình",
    "HIGH": "Cao",
    "CRITICAL": "Rất cao",
}

FOCUS_AREA_LABELS = {
    "Eye region": "Vùng mắt",
    "Mouth boundary": "Viền miệng",
    "Skin texture": "Kết cấu da",
    "Face edge": "Viền khuôn mặt",
    "Face boundary": "Viền khuôn mặt",
    "Mouth motion": "Chuyển động miệng",
    "Lighting": "Ánh sáng",
}

SIGNAL_LABELS = {
    "Unnatural facial texture detected": "Phát hiện kết cấu da/khuôn mặt thiếu tự nhiên.",
    "Abnormal eye region artifacts": "Vùng mắt có dấu hiệu nhiễu, méo hoặc phản chiếu ánh sáng bất thường.",
    "Inconsistent lighting around face boundary": "Ánh sáng quanh viền khuôn mặt chưa đồng nhất với nền.",
    "Possible synthetic facial boundary artifacts": "Viền khuôn mặt có thể chứa dấu vết tổng hợp hoặc ghép mặt.",
}


def build_report_text(result: dict) -> str:
    prediction = result.get("prediction", "UNKNOWN")
    confidence = result.get("confidence", 0)
    risk_level = result.get("riskLevel", "UNKNOWN")
    created_at = _format_datetime(result.get("createdAt"))
    focus_areas = _format_focus_areas(result.get("focusAreas", []))
    signals = _format_signals(result.get("explanation", []))
    regions = _format_regions(result.get("suspiciousRegions", []))
    temporal = _format_temporal(result)
    hybrid = _format_hybrid_forensics(result)
    ai_summary = _format_ai_summary(result)

    return f"""BÁO CÁO PHÂN TÍCH DEEPSHIELD AI PRO

1. THÔNG TIN HỒ SƠ
- Mã báo cáo: {result.get("reportId", "Chưa có")}
- Mã phân tích: {result.get("analysisId", "Chưa có")}
- Tên tệp: {result.get("fileName", "Không rõ")}
- Thời điểm tạo: {created_at}

2. KẾT LUẬN SƠ BỘ
- Dự đoán: {PREDICTION_LABELS.get(prediction, prediction)}
- Nhãn mô hình: {prediction}
- Độ tin cậy: {confidence}%
- Mức rủi ro: {RISK_LABELS.get(risk_level, risk_level)}
- Điểm rủi ro: {result.get("riskScore", 0)}/100
- Frame nghi ngờ: {result.get("suspiciousFrames", 0)}/{result.get("totalFrames", 0)}

Giải thích ngắn:
{ai_summary}

3. VÙNG CẦN CHÚ Ý
{focus_areas}

4. TÍN HIỆU PHÁT HIỆN
{signals}

5. PHÂN TÍCH VÙNG NGHI NGỜ
{regions}

6. PHÂN TÍCH THEO THỜI GIAN
{temporal}

7. HYBRID AI-GENERATED FORENSICS
{hybrid}

8. KHUYẾN NGHỊ KIỂM TRA THỦ CÔNG
- Không xem kết quả này là kết luận tuyệt đối. Đây là báo cáo hỗ trợ điều tra.
- Xem chậm các đoạn hoặc frame có điểm nghi ngờ cao.
- So sánh vùng mắt, miệng, viền khuôn mặt và ánh sáng qua nhiều frame liên tiếp.
- Nếu tệp quá mờ, bị nén mạnh hoặc khuôn mặt quá nhỏ, nên dùng video/ảnh rõ hơn để tăng độ tin cậy.
"""


def save_analysis_report(result: dict) -> dict:
    report_dir = Path(settings.REPORT_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)

    report_id = result.get("reportId") or generate_report_id()
    result["reportId"] = report_id
    result["createdAt"] = result.get("createdAt") or datetime.utcnow().isoformat()

    text_path = report_dir / f"{report_id}.txt"
    json_path = report_dir / f"{report_id}.json"

    text_path.write_text(build_report_text(result), encoding="utf-8")
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "reportId": report_id,
        "reportTextPath": str(text_path),
        "reportJsonPath": str(json_path),
        "reportUrl": f"/storage/reports/{report_id}.txt",
    }


def _format_datetime(value: str | None) -> str:
    if not value:
        return "Không rõ"
    try:
        return datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return value


def _format_focus_areas(focus_areas: list) -> str:
    if not focus_areas:
        return "- Chưa có vùng trọng tâm cụ thể."
    return "\n".join(f"- {FOCUS_AREA_LABELS.get(area, area)}" for area in focus_areas)


def _format_signals(signals: list) -> str:
    if not signals:
        return "- Chưa có tín hiệu mô tả chi tiết."
    return "\n".join(f"- {SIGNAL_LABELS.get(signal, signal)}" for signal in signals)


def _format_regions(regions: list) -> str:
    if not regions:
        return "- Chưa khoanh được vùng nghi ngờ cụ thể. Nên thử tệp rõ hơn hoặc chọn đoạn có khuôn mặt rõ."

    lines = []
    for index, region in enumerate(regions, start=1):
        label = region.get("label", "Điểm nghi ngờ")
        score = round(float(region.get("score", 0)))
        severity = region.get("severity", "Không rõ")
        reason = region.get("reason") or "Chưa có giải thích chi tiết cho vùng này."
        manual_check = region.get("manualCheck") or "Phóng to vùng này và so sánh với các frame liền kề."
        bbox = region.get("bbox") or {}
        position = ""
        if bbox:
            position = (
                f" Vị trí tương đối: x {round(float(bbox.get('x', 0)) * 100)}%, "
                f"y {round(float(bbox.get('y', 0)) * 100)}%, "
                f"rộng {round(float(bbox.get('width', 0)) * 100)}%, "
                f"cao {round(float(bbox.get('height', 0)) * 100)}%."
            )

        lines.append(
            "\n".join(
                [
                    f"{index}. {label} - mức {severity}, điểm {score}%.",
                    f"   Vì sao nghi ngờ: {reason}",
                    f"   Cách kiểm tra: {manual_check}",
                    f"   {position}".rstrip(),
                ]
            )
        )
    return "\n".join(lines)


def _format_temporal(result: dict) -> str:
    stats = result.get("temporalStats") or {}
    segments = result.get("suspiciousSegments") or []
    if not stats and not segments:
        return "- Không có dữ liệu phân tích theo thời gian cho tệp này."

    lines = [
        f"- Xác suất nghi giả trung bình: {_percent(stats.get('meanFakeProbability'))}",
        f"- Xác suất nghi giả cao nhất: {_percent(stats.get('maxFakeProbability'))}",
        f"- Độ dao động giữa các frame: {_percent(stats.get('temporalVariance'))}",
        f"- Tỷ lệ frame nghi ngờ: {stats.get('suspiciousFrameRatio', 0)}%",
    ]

    if segments:
        lines.append("- Các đoạn nên xem lại:")
        for segment in segments:
            lines.append(
                f"  + Frame {segment.get('startFrame')} đến {segment.get('endFrame')}: "
                f"trung bình {_percent(segment.get('meanFakeProbability'))}, "
                f"cao nhất {_percent(segment.get('maxFakeProbability'))}."
            )
    embedding = _format_embedding_similarity(result)
    if embedding:
        lines.append("")
        lines.append(embedding)
    return "\n".join(lines)


def _format_hybrid_forensics(result: dict) -> str:
    hybrid = result.get("hybridForensics") or {}
    if not hybrid:
        return "- Chua co du lieu hybrid forensics."

    metadata = hybrid.get("metadata") or {}
    frequency = hybrid.get("frequency") or {}
    artifacts = hybrid.get("artifacts") or {}
    generated_portrait = hybrid.get("generatedPortrait") or {}
    fusion = result.get("fusion") or {}

    lines = [
        f"- Metadata Forensics: {round(float(metadata.get('score', 0)))}%",
        f"- FFT Frequency Analysis: {round(float(frequency.get('score', 0)))}%",
        f"- AI Artifact Detection: {round(float(artifacts.get('score', 0)))}%",
        f"- Generated Portrait Consistency: {round(float(generated_portrait.get('score', 0)))}%",
        f"- Hybrid forensic risk: {round(float(hybrid.get('riskScore', 0)))}%",
        f"- Final fusion risk: {round(float(fusion.get('finalRiskScore', result.get('riskScore', 0))))}%",
    ]
    signals = hybrid.get("signals") or []
    if signals:
        lines.append("- Tin hieu noi bat:")
        lines.extend(f"  + {signal}" for signal in signals[:5])
    return "\n".join(lines)


def _format_embedding_similarity(result: dict) -> str:
    similarity = result.get("embeddingSimilarity") or {}
    if not similarity or not similarity.get("available"):
        return ""

    lines = [
        "Face Embedding Similarity:",
        f"- Cosine similarity trung binh: {_percent(similarity.get('meanSimilarity'))}",
        f"- Cosine similarity thap nhat: {_percent(similarity.get('minSimilarity'))}",
        f"- Muc giam similarity lon nhat: {_percent(similarity.get('maxSimilarityDrop'))}",
        f"- Ty le chuyen frame nghi ngo: {similarity.get('suspiciousTransitionRatio', 0)}%",
    ]
    transitions = similarity.get("suspiciousTransitions") or []
    if transitions:
        lines.append("- Chuyen frame can xem lai:")
        for item in transitions:
            lines.append(
                f"  + Frame {item.get('fromFrame')} -> {item.get('toFrame')}: "
                f"cosine {_percent(item.get('cosineSimilarity'))}, "
                f"giam {_percent(item.get('similarityDrop'))}."
            )
    return "\n".join(lines)


def _format_ai_summary(result: dict) -> str:
    prediction = result.get("prediction", "UNKNOWN")
    confidence = result.get("confidence", 0)
    risk_level = RISK_LABELS.get(result.get("riskLevel"), result.get("riskLevel", "Không rõ"))

    if prediction == "FAKE":
        verdict = "Hệ thống phát hiện các tín hiệu nghi ngờ nội dung có thể đã bị chỉnh sửa hoặc tổng hợp."
    elif prediction == "REAL":
        verdict = "Hệ thống chưa thấy dấu hiệu giả mạo rõ ràng trong dữ liệu hiện tại."
    else:
        verdict = "Hệ thống chưa đủ tín hiệu để đưa ra kết luận rõ."

    return (
        f"{verdict} Độ tin cậy hiện tại là {confidence}%, mức rủi ro {risk_level}. "
        "Cần đối chiếu thêm vùng nghi ngờ, nguồn gốc tệp và các frame liên tiếp trước khi kết luận."
    )


def _percent(value) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    if number <= 1:
        number *= 100
    return f"{round(number)}%"
