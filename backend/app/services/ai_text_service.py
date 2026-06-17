import httpx

from app.core.config import settings
from app.services.chatbot_knowledge import load_forensics_knowledge
from app.services.gemini_service import (
    call_gemini,
    gemini_error_message,
    gemini_ready,
    missing_gemini_key_message,
)
from app.services.groq_service import (
    call_groq_chat,
    groq_error_message,
    groq_ready,
    missing_groq_key_message,
)


RISK_LABELS = {
    "LOW": "Thấp",
    "MEDIUM": "Trung bình",
    "HIGH": "Cao",
    "CRITICAL": "Rất cao",
}


def generate_deepfake_report(result: dict) -> str:
    prompt = f"""
Bạn là chuyên gia AI Forensics. Hãy viết báo cáo ngắn bằng tiếng Việt có dấu,
giải thích kết quả phát hiện deepfake theo cách dễ hiểu.

Prediction: {result.get("prediction")}
Confidence: {result.get("confidence")}%
Risk Level: {result.get("riskLevel")}
Risk Score: {result.get("riskScore")}
Inference Mode: {result.get("inferenceMode")}
Heatmap Method: {result.get("heatmapMethod")}
Hybrid Forensics: {result.get("hybridForensics")}
Fusion: {result.get("fusion")}
Suspicious Frames: {result.get("suspiciousFrames")}/{result.get("totalFrames")}
Temporal Stats: {result.get("temporalStats")}
Embedding Similarity: {result.get("embeddingSimilarity")}
Suspicious Segments: {result.get("suspiciousSegments")}
Suspicious Regions: {result.get("suspiciousRegions")}
Explanation Signals: {result.get("explanation")}

Yêu cầu:
- Không khẳng định tuyệt đối.
- Giải thích rõ từng vùng nghi ngờ.
- Nêu lý do vì sao vùng đó đáng chú ý.
- Nêu cách kiểm tra thủ công.
- Nếu tín hiệu yếu hoặc model chưa chắc, phải nói rõ.
"""

    provider = (settings.CHATBOT_PROVIDER or "groq").lower()
    if provider == "gemini":
        if not gemini_ready():
            return fallback_report(result)
        try:
            return call_gemini(prompt, _chat_system_instruction(), temperature=0.35, max_tokens=1100)
        except Exception as exc:
            print("Gemini Report Error:", exc)
            return fallback_report(result)

    if not groq_ready():
        return fallback_report(result)

    try:
        return call_groq_chat(prompt, _chat_system_instruction(), temperature=0.35, max_tokens=1100)
    except Exception as exc:
        print("Groq Report Error:", exc)
        return fallback_report(result)


def generate_chatbot_answer(question: str, analysis: dict | None = None) -> dict:
    analysis = analysis or {}
    provider = (settings.CHATBOT_PROVIDER or "groq").lower()
    prompt = _build_chat_prompt(question, analysis)

    if provider == "groq":
        if not groq_ready():
            return {"answer": missing_groq_key_message(), "mode": "fallback_no_llm_key"}
        try:
            answer = call_groq_chat(prompt, _chat_system_instruction(), temperature=0.55, max_tokens=900)
            return {"answer": answer, "mode": "groq"}
        except Exception as exc:
            print("Groq Chatbot Error:", exc)
            return {"answer": groq_error_message(str(exc)), "mode": "groq_error"}

    if provider == "gemini":
        if not gemini_ready():
            return {"answer": missing_gemini_key_message(), "mode": "fallback_no_gemini_key"}
        try:
            answer = call_gemini(prompt, _chat_system_instruction(), temperature=0.55, max_tokens=900)
            return {"answer": answer, "mode": "gemini"}
        except Exception as exc:
            print("Gemini Chatbot Error:", exc)
            return {"answer": gemini_error_message(str(exc)), "mode": "gemini_error"}

    if provider == "ollama":
        try:
            answer = _call_ollama_chat(prompt)
            return {"answer": answer, "mode": "ollama"}
        except Exception as exc:
            print("Ollama Chatbot Error:", exc)
            return {"answer": _ollama_error_message(str(exc)), "mode": "ollama_error"}

    return {
        "answer": f"CHATBOT_PROVIDER='{settings.CHATBOT_PROVIDER}' chưa được hỗ trợ. Hãy dùng `groq`, `gemini` hoặc `ollama`.",
        "mode": "unsupported_provider",
    }


def fallback_report(result: dict) -> str:
    prediction = result.get("prediction", "UNKNOWN")
    risk_level = RISK_LABELS.get(result.get("riskLevel"), result.get("riskLevel", "Không rõ"))
    confidence = result.get("confidence", 0)
    mode = result.get("inferenceMode", "không rõ")
    verdict = "có dấu hiệu giả mạo" if prediction == "FAKE" else "chưa thấy dấu hiệu giả mạo rõ ràng"

    return f"""Kết luận sơ bộ
Hệ thống đánh giá nội dung {verdict}, với độ tin cậy khoảng {confidence}%.
Mức rủi ro hiện tại: {risk_level}.
Chế độ phân tích: {mode}.

Phân tích theo thời gian
{_temporal_lines(result)}

Face embedding similarity
{_embedding_lines(result)}

Các điểm nghi ngờ chính
{_region_lines(result)}

Khuyến nghị kiểm tra thủ công
- Không kết luận tuyệt đối chỉ dựa vào một lần phân tích.
- Xem chậm các đoạn có điểm nghi ngờ cao.
- So sánh vùng mắt, miệng, viền mặt giữa nhiều frame liên tiếp.
- Nếu video bị mờ, nén mạnh hoặc khuôn mặt quá nhỏ, nên dùng video rõ hơn để tăng độ tin cậy.
"""


def _build_chat_prompt(question: str, analysis: dict) -> str:
    return f"""
Câu hỏi của người dùng:
{question}

Ngữ cảnh phân tích DeepShield hiện có:
{_compact_analysis_context(analysis)}

Kho kiến thức DeepShield để giải thích:
{load_forensics_knowledge()}

Hãy trả lời bằng tiếng Việt có dấu.
Yêu cầu:
- Trả lời đúng câu hỏi người dùng, không tự động lặp lại toàn bộ báo cáo.
- Nếu câu hỏi không liên quan trực tiếp đến deepfake, vẫn trả lời hữu ích ở mức tổng quát.
- Nếu dùng dữ liệu phân tích, nói rõ đó là dữ liệu hỗ trợ chứ không phải kết luận tuyệt đối.
- Không bịa rằng đã xem file gốc nếu ngữ cảnh không có thông tin đó.
- Trình bày ngắn gọn, dễ hiểu.
"""


def _chat_system_instruction() -> str:
    return (
        "Bạn là chatbot DeepShield AI Pro. Bạn trả lời linh hoạt câu hỏi của người dùng bằng tiếng Việt, "
        "có thể giải thích kết quả deepfake, hướng dẫn kiểm tra thủ công và nói rõ giới hạn của hệ thống."
    )


def _compact_analysis_context(analysis: dict) -> str:
    if not analysis:
        return "Chưa có kết quả phân tích nào được gửi kèm."

    fields = {
        "prediction": analysis.get("prediction"),
        "confidence": analysis.get("confidence"),
        "riskLevel": analysis.get("riskLevel"),
        "riskScore": analysis.get("riskScore"),
        "inferenceMode": analysis.get("inferenceMode"),
        "totalFrames": analysis.get("totalFrames"),
        "suspiciousFrames": analysis.get("suspiciousFrames"),
        "focusAreas": analysis.get("focusAreas"),
        "temporalStats": analysis.get("temporalStats"),
        "embeddingSimilarity": analysis.get("embeddingSimilarity"),
        "hybridForensics": analysis.get("hybridForensics"),
        "fusion": analysis.get("fusion"),
        "suspiciousSegments": analysis.get("suspiciousSegments"),
        "suspiciousRegions": analysis.get("suspiciousRegions"),
    }
    lines = [f"- {key}: {value}" for key, value in fields.items() if value not in (None, "", [], {})]
    return "\n".join(lines) if lines else "Ngữ cảnh phân tích trống."


def _call_ollama_chat(prompt: str) -> str:
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    response = httpx.post(
        f"{base_url}/api/chat",
        json={
            "model": settings.OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": _chat_system_instruction()},
                {"role": "user", "content": prompt},
            ],
            "options": {"temperature": 0.55},
        },
        timeout=120,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Ollama HTTP {response.status_code}: {response.text[:300]}")
    data = response.json()
    answer = data.get("message", {}).get("content", "").strip()
    if not answer:
        raise RuntimeError(f"Ollama returned empty answer: {data}")
    return answer


def _ollama_error_message(error_text: str) -> str:
    lowered = error_text.lower()
    if "connecterror" in lowered or "connection refused" in lowered or "winerror 10061" in lowered:
        return (
            "Ollama chưa chạy ở máy bạn. Nếu muốn dùng AI local, cài Ollama từ https://ollama.com "
            "và chạy `ollama pull llama3.1:8b`."
        )
    if "not found" in lowered or "404" in lowered:
        return f"Ollama đang chạy nhưng chưa có model `{settings.OLLAMA_MODEL}`. Hãy chạy `ollama pull {settings.OLLAMA_MODEL}`."
    return "Ollama local đang lỗi hoặc chưa sẵn sàng."


def _region_lines(result: dict) -> str:
    regions = result.get("suspiciousRegions") or []
    if not regions:
        return "Không có vùng nghi ngờ cụ thể được khoanh rõ. Nên kiểm tra lại video hoặc chọn đoạn có khuôn mặt rõ hơn."

    lines = []
    for index, region in enumerate(regions, start=1):
        lines.append(
            "\n".join(
                [
                    f"{index}. {region.get('label')} - mức {region.get('severity', 'Không rõ')} ({region.get('score', 0)}%)",
                    f"   Lý do: {region.get('reason', 'Chưa có giải thích chi tiết.')}",
                    f"   Cách kiểm tra: {region.get('manualCheck', 'Phóng to vùng này và so sánh với các frame liền kề.')}",
                ]
            )
        )
    return "\n".join(lines)


def _temporal_lines(result: dict) -> str:
    stats = result.get("temporalStats") or {}
    segments = result.get("suspiciousSegments") or []
    lines = [
        f"- Xác suất nghi giả trung bình theo frame: {_percent(stats.get('meanFakeProbability'))}",
        f"- Xác suất nghi giả cao nhất: {_percent(stats.get('maxFakeProbability'))}",
        f"- Tỷ lệ frame nghi ngờ: {stats.get('suspiciousFrameRatio', 0)}%",
    ]
    if segments:
        lines.append("- Các đoạn đáng xem lại:")
        for segment in segments:
            lines.append(
                f"  + Frame {segment.get('startFrame')} đến {segment.get('endFrame')}: "
                f"đỉnh {_percent(segment.get('maxFakeProbability'))}"
            )
    return "\n".join(lines)


def _embedding_lines(result: dict) -> str:
    similarity = result.get("embeddingSimilarity") or {}
    if not similarity or not similarity.get("available"):
        return "- Khong co du frame khuon mat lien tiep de tinh cosine similarity."

    lines = [
        f"- Cosine similarity trung binh: {_percent(similarity.get('meanSimilarity'))}",
        f"- Cosine similarity thap nhat: {_percent(similarity.get('minSimilarity'))}",
        f"- Muc giam similarity lon nhat: {_percent(similarity.get('maxSimilarityDrop'))}",
        f"- Ty le chuyen frame nghi ngo: {similarity.get('suspiciousTransitionRatio', 0)}%",
    ]
    transitions = similarity.get("suspiciousTransitions") or []
    if transitions:
        lines.append("- Cac chuyen frame can soi lai:")
        for item in transitions:
            lines.append(
                f"  + Frame {item.get('fromFrame')} -> {item.get('toFrame')}: "
                f"cosine {_percent(item.get('cosineSimilarity'))}, "
                f"giam {_percent(item.get('similarityDrop'))}."
            )
    return "\n".join(lines)


def _percent(value) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    if number <= 1:
        number *= 100
    return f"{round(number)}%"
