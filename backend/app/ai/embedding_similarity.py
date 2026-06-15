import cv2
import numpy as np


def _face_embedding(file_path: str, bins_per_channel: int = 16) -> np.ndarray | None:
    image = cv2.imread(str(file_path))
    if image is None:
        return None

    image = cv2.resize(image, (112, 112), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    features = []
    for channel in cv2.split(hsv) + cv2.split(ycrcb):
        hist = cv2.calcHist([channel], [0], None, [bins_per_channel], [0, 256]).flatten()
        features.append(hist)

    texture = cv2.Laplacian(gray, cv2.CV_32F)
    features.extend(
        [
            np.array([float(gray.mean()), float(gray.std())], dtype=np.float32),
            np.array([float(texture.mean()), float(texture.std())], dtype=np.float32),
        ]
    )

    embedding = np.concatenate(features).astype(np.float32)
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return None
    return embedding / norm


def _cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
    if denominator == 0:
        return 0.0
    return float(np.dot(vector_a, vector_b) / denominator)


def build_embedding_similarity(face_paths: list[str]) -> dict:
    embeddings = [_face_embedding(path) for path in face_paths]
    pairs = []

    for index in range(1, len(embeddings)):
        previous = embeddings[index - 1]
        current = embeddings[index]
        if previous is None or current is None:
            continue

        similarity = _cosine_similarity(previous, current)
        drop = 1.0 - similarity
        pairs.append(
            {
                "fromFrame": index,
                "toFrame": index + 1,
                "cosineSimilarity": round(similarity, 4),
                "similarityDrop": round(drop, 4),
                "suspicious": similarity < 0.82 or drop > 0.18,
            }
        )

    values = [item["cosineSimilarity"] for item in pairs]
    suspicious_pairs = [item for item in pairs if item["suspicious"]]

    if not values:
        return {
            "available": False,
            "method": "Color/texture face embedding + cosine similarity",
            "meanSimilarity": None,
            "minSimilarity": None,
            "maxSimilarityDrop": None,
            "suspiciousTransitions": [],
            "pairs": [],
        }

    drops = [item["similarityDrop"] for item in pairs]
    return {
        "available": True,
        "method": "Color/texture face embedding + cosine similarity",
        "meanSimilarity": round(float(np.mean(values)), 4),
        "minSimilarity": round(float(np.min(values)), 4),
        "maxSimilarityDrop": round(float(np.max(drops)), 4),
        "suspiciousTransitionRatio": round((len(suspicious_pairs) / len(pairs)) * 100, 2),
        "suspiciousTransitions": suspicious_pairs[:5],
        "pairs": pairs,
    }
