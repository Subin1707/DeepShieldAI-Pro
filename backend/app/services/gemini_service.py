import httpx

from app.core.config import settings
from app.core.security import is_placeholder_secret


def gemini_ready() -> bool:
    return not is_placeholder_secret(settings.GEMINI_API_KEY)


def call_gemini(prompt: str, system_instruction: str, temperature: float = 0.35, max_tokens: int = 1100) -> str:
    base_url = settings.GEMINI_BASE_URL.rstrip("/")
    url = f"{base_url}/models/{settings.GEMINI_MODEL}:generateContent"
    response = httpx.post(
        url,
        params={"key": settings.GEMINI_API_KEY},
        json={
            "systemInstruction": {
                "parts": [{"text": system_instruction}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        },
        timeout=25,
    )
    if response.status_code >= 400:
        raise RuntimeError(gemini_http_error(response))

    data = response.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "\n".join(part.get("text", "") for part in parts).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Gemini response did not include text content: {data}") from exc

    if not text:
        raise RuntimeError(f"Gemini returned empty text: {data}")
    return text


def missing_gemini_key_message() -> str:
    return (
        "Chatbot dang chon Gemini nhung backend chua co `GEMINI_API_KEY` hop le. "
        "Hay dat `CHATBOT_PROVIDER=gemini`, `GEMINI_API_KEY` va tuy chon `GEMINI_MODEL` trong backend/.env."
    )


def gemini_http_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
        message = payload.get("error", {}).get("message", response.text[:300])
    except ValueError:
        message = response.text[:300]
    return f"Gemini HTTP {response.status_code}: {message}"


def gemini_error_message(error_text: str) -> str:
    lowered = error_text.lower()
    if "api key" in lowered or "permission" in lowered or "401" in lowered or "403" in lowered:
        return "Gemini tu choi API key hien tai. Hay kiem tra `GEMINI_API_KEY` trong backend/.env."
    if "not found" in lowered or "404" in lowered:
        return "Gemini khong tim thay model trong `GEMINI_MODEL`. Hay kiem tra ten model."
    return "Gemini dang loi hoac cau hinh chua dung. Hay kiem tra `GEMINI_API_KEY`, `GEMINI_MODEL` va mang backend."
