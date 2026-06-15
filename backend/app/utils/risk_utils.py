RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"


def normalize_prediction(prediction: str) -> str:
    value = (prediction or "").strip().upper()
    if value not in {"REAL", "FAKE"}:
        return "UNKNOWN"
    return value


def clamp_confidence(confidence: float) -> float:
    return max(0.0, min(100.0, float(confidence)))


def calculate_risk_level(confidence: float, prediction: str) -> str:
    prediction = normalize_prediction(prediction)
    confidence = clamp_confidence(confidence)

    if prediction == "REAL":
        return RISK_LOW

    if prediction == "UNKNOWN":
        return RISK_MEDIUM

    if confidence >= 95:
        return RISK_CRITICAL

    if confidence >= 85:
        return RISK_HIGH

    if confidence >= 65:
        return RISK_MEDIUM

    return RISK_LOW


def calculate_risk_score(confidence: float, prediction: str) -> int:
    prediction = normalize_prediction(prediction)
    confidence = clamp_confidence(confidence)

    if prediction == "REAL":
        return max(0, int(100 - confidence))

    if prediction == "UNKNOWN":
        return 50

    return min(100, int(confidence))


def is_high_risk(risk_level: str) -> bool:
    return risk_level.upper() in {RISK_HIGH, RISK_CRITICAL}


def get_risk_color(risk_level: str) -> str:
    colors = {
        RISK_LOW: "green",
        RISK_MEDIUM: "yellow",
        RISK_HIGH: "orange",
        RISK_CRITICAL: "red",
    }
    return colors.get(risk_level.upper(), "gray")


def get_risk_message(risk_level: str) -> str:
    messages = {
        RISK_LOW: "Low risk. The content does not show strong deepfake indicators.",
        RISK_MEDIUM: "Medium risk. Some suspicious signals were detected.",
        RISK_HIGH: "High risk. Multiple deepfake indicators were detected.",
        RISK_CRITICAL: "Critical risk. The content shows very strong deepfake indicators.",
    }
    return messages.get(risk_level.upper(), "Risk level could not be determined.")
