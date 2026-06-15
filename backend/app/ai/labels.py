from app.core.config import settings

LABEL_REAL = "REAL"
LABEL_FAKE = "FAKE"
LABEL_UNKNOWN = "UNKNOWN"

CLASS_NAMES = {
    0: LABEL_REAL,
    1: LABEL_FAKE,
}

DEFAULT_THRESHOLD = settings.FAKE_THRESHOLD


def clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def label_from_probability(fake_probability: float, threshold: float = DEFAULT_THRESHOLD) -> str:
    fake_probability = clamp_probability(fake_probability)
    return LABEL_FAKE if fake_probability >= threshold else LABEL_REAL


def confidence_from_probability(fake_probability: float, prediction: str) -> float:
    fake_probability = clamp_probability(fake_probability)
    if prediction == LABEL_FAKE:
        return round(fake_probability * 100, 2)
    if prediction == LABEL_REAL:
        return round((1 - fake_probability) * 100, 2)
    return 0.0


def probability_payload(fake_probability: float) -> dict:
    fake_probability = clamp_probability(fake_probability)
    return {
        "realProbability": round(1 - fake_probability, 4),
        "fakeProbability": round(fake_probability, 4),
    }


def decision_payload(fake_probability: float, threshold: float = DEFAULT_THRESHOLD) -> dict:
    fake_probability = clamp_probability(fake_probability)
    margin = abs(fake_probability - threshold)
    return {
        "decisionThreshold": threshold,
        "decisionMargin": round(margin, 4),
        "requiresReview": margin < settings.REVIEW_MARGIN,
    }
