from typing import Any, Literal

from pydantic import BaseModel, Field


PredictionLabel = Literal["REAL", "FAKE", "UNKNOWN"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class MediaMetadata(BaseModel):
    type: Literal["image", "video"]
    width: int | None = None
    height: int | None = None
    format: str | None = None
    mode: str | None = None
    fps: float | None = None
    frameCount: int | None = None
    durationSeconds: float | None = None
    sizeBytes: int | None = None


class FrameResult(BaseModel):
    frameIndex: int
    prediction: PredictionLabel
    confidence: float = Field(ge=0, le=100)
    filePath: str | None = None
    framePath: str | None = None
    facePath: str | None = None
    face: dict[str, Any] | None = None
    inferenceMode: str | None = None
    signals: list[str] = []
    fakeProbability: float | None = Field(default=None, ge=0, le=1)
    realProbability: float | None = Field(default=None, ge=0, le=1)
    decisionThreshold: float | None = Field(default=None, ge=0, le=1)
    decisionMargin: float | None = Field(default=None, ge=0, le=1)
    requiresReview: bool = False


class AnalysisResult(BaseModel):
    analysisId: str
    fileName: str
    filePath: str
    sourceFile: str | None = None
    prediction: PredictionLabel
    confidence: float = Field(ge=0, le=100)
    riskLevel: RiskLevel
    riskScore: int = Field(ge=0, le=100)
    modelPrediction: PredictionLabel | None = None
    modelConfidence: float | None = None
    modelRiskScore: int | float | None = None
    modelUsed: bool = False
    inferenceMode: str | None = None
    fakeProbability: float | None = Field(default=None, ge=0, le=1)
    realProbability: float | None = Field(default=None, ge=0, le=1)
    decisionThreshold: float | None = Field(default=None, ge=0, le=1)
    decisionMargin: float | None = Field(default=None, ge=0, le=1)
    decisionThresholds: dict[str, float] | None = None
    requiresReview: bool = False
    totalFrames: int = 1
    suspiciousFrames: int = 0
    focusAreas: list[str] = []
    explanation: list[str] = []
    frameResults: list[FrameResult] = []
    sequenceLength: int | None = None
    sequenceResult: dict[str, Any] | None = None
    temporalStats: dict[str, Any] | None = None
    suspiciousSegments: list[dict[str, Any]] = []
    sampledFrames: list[str] = []
    sampledFaces: list[str] = []
    faceDetections: list[dict[str, Any]] = []
    media: MediaMetadata | dict[str, Any] | None = None
    heatmapUrl: str | None = None
    heatmapMethod: str | None = None
    heatmapFaceBoxSource: str | None = None
    suspiciousRegions: list[dict[str, Any]] = []
    embeddingSimilarity: dict[str, Any] | None = None
    hybridForensics: dict[str, Any] | None = None
    fusion: dict[str, Any] | None = None
    trainingHistory: dict[str, Any] | None = None
    processingTimes: dict[str, Any] | None = None
    aiReport: str | None = None
    reportId: str | None = None
    reportUrl: str | None = None
    reportTextPath: str | None = None
    reportJsonPath: str | None = None
    createdAt: str | None = None


class AnalysisResponse(BaseModel):
    status: str
    message: str
    data: AnalysisResult
    timestamp: str
