from fastapi import APIRouter

from app.schemas.chatbot_schema import ChatbotExplainRequest
from app.services.ai_text_service import generate_chatbot_answer
from app.utils.response_utils import success_response

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("/explain")
def explain_result(request: ChatbotExplainRequest):
    payload = request.model_dump()
    analysis = payload.pop("analysis", None) or {}
    question = payload.pop("question", None) or "Hãy giải thích kết quả phân tích này."
    merged = {**payload, **analysis}

    answer = generate_chatbot_answer(question, merged)
    return success_response(data=answer, message="Chatbot answer generated.")


@router.get("/suggestions")
def get_suggested_questions():
    return success_response(
        data=[
            "Vì sao hệ thống đưa ra kết luận này?",
            "Độ tin cậy này có ý nghĩa gì?",
            "Những vùng nào trên khuôn mặt đáng nghi nhất?",
            "Mình nên kiểm tra thủ công như thế nào?",
            "Chatbot đang dùng AI thật hay fallback?",
        ],
        message="Suggested questions loaded.",
    )
