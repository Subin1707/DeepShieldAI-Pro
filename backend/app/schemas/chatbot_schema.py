from typing import Any

from pydantic import BaseModel, Field


class ChatbotExplainRequest(BaseModel):
    question: str | None = None
    analysis: dict[str, Any] | None = None
    prediction: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=100)
    riskLevel: str | None = None
    riskScore: int | None = Field(default=None, ge=0, le=100)
    totalFrames: int = 1
    suspiciousFrames: int = 0
    focusAreas: list[str] = []
    explanation: list[str] = []


class ChatbotExplainResponseData(BaseModel):
    report: str


class SuggestedQuestionsResponseData(BaseModel):
    questions: list[str]
