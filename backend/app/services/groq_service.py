import httpx

from app.core.config import settings
from app.core.security import is_placeholder_secret


def groq_ready() -> bool:
    return not is_placeholder_secret(settings.GROQ_API_KEY)


def call_groq_chat(
    prompt: str,
    system_instruction: str,
    temperature: float = 0.55,
    max_tokens: int = 900,
) -> str:
    base_url = settings.GROQ_BASE_URL.rstrip("/")
    response = httpx.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=25,
    )
    if response.status_code >= 400:
        raise RuntimeError(_safe_groq_error(response))

    data = response.json()
    try:
        answer = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Groq response did not include text content: {data}") from exc
    if not answer:
        raise RuntimeError(f"Groq returned empty text: {data}")
    return answer


def missing_groq_key_message() -> str:
    return (
        "Chatbot đã chuyển sang Groq nhưng backend chưa có `GROQ_API_KEY` hợp lệ.\n\n"
        "Bạn mở `backend/.env`, đặt `CHATBOT_PROVIDER=groq` và dán key Groq vào `GROQ_API_KEY`, "
        "sau đó khởi động lại backend."
    )


def groq_error_message(error_text: str) -> str:
    lowered = error_text.lower()
    if "groq http 401" in lowered or "invalid api key" in lowered:
        return (
            "Groq từ chối API key hiện tại. Bạn kiểm tra `GROQ_API_KEY` trong `backend/.env`, "
            "đảm bảo key bắt đầu bằng `gsk_`, chưa bị revoke và không có dấu cách thừa."
        )
    if "groq http 403" in lowered:
        return "Groq trả lỗi 403. Có thể key chưa được phép dùng model hiện tại."
    if "groq http 404" in lowered or "model" in lowered:
        return "Groq không tìm thấy model trong `GROQ_MODEL`. Hãy thử `llama-3.1-8b-instant`."
    if "connecterror" in lowered or "timed out" in lowered:
        return "Backend chưa gọi được Groq. Bạn kiểm tra mạng Internet hoặc thử lại sau."
    return "Groq đang lỗi hoặc cấu hình chưa đúng. Bạn kiểm tra `GROQ_API_KEY`, `GROQ_MODEL` và mạng backend nhé."


def _safe_groq_error(response: httpx.Response) -> str:
    message = "Groq request failed."
    try:
        payload = response.json()
        error = payload.get("error") or {}
        message = error.get("message") or message
    except ValueError:
        if response.text:
            message = response.text[:300]
    return f"Groq HTTP {response.status_code}: {message}"
