from pydantic import BaseModel


class ReportSummary(BaseModel):
    reportId: str
    fileName: str
    downloadUrl: str


class ReportFileInfo(BaseModel):
    reportId: str
    reportTextPath: str
    reportJsonPath: str
    reportUrl: str


class ReportCreateData(BaseModel):
    analysisId: str
    reportId: str | None = None
    fileName: str | None = None
    prediction: str
    confidence: float
    riskLevel: str
    riskScore: int
    suspiciousFrames: int = 0
    totalFrames: int = 1
    focusAreas: list[str] = []
    explanation: list[str] = []
    aiReport: str | None = None
    createdAt: str | None = None
