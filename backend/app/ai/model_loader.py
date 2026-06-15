from functools import lru_cache
from pathlib import Path

from app.core.config import settings


class LoadedModel:
    def __init__(self, model, backend: str, path: Path):
        self.model = model
        self.backend = backend
        self.path = path

    def predict(self, input_tensor):
        if self.backend == "keras":
            return self.model.predict(input_tensor, verbose=0)

        if self.backend == "onnx":
            input_name = self.model.get_inputs()[0].name
            return self.model.run(None, {input_name: input_tensor.astype("float32")})[0]

        if self.backend == "torchscript":
            import torch

            tensor = torch.from_numpy(input_tensor).permute(0, 3, 1, 2).float()
            with torch.no_grad():
                output = self.model(tensor)
            return output.detach().cpu().numpy()

        raise ValueError(f"Unsupported model backend: {self.backend}")


def get_model_path() -> Path:
    return Path(settings.MODEL_PATH)


def model_file_exists() -> bool:
    path = get_model_path()
    return path.exists() and path.stat().st_size > 0


def get_model_status() -> dict:
    path = get_model_path()
    loaded_model = load_deepfake_model()
    return {
        "modelPath": str(path),
        "exists": path.exists(),
        "sizeBytes": path.stat().st_size if path.exists() else 0,
        "ready": loaded_model is not None,
        "backend": loaded_model.backend if loaded_model else None,
        "supportedExtensions": [".h5", ".keras", ".onnx", ".pt", ".pth"],
    }


@lru_cache
def load_deepfake_model():
    if not model_file_exists():
        return None

    path = get_model_path()
    suffix = path.suffix.lower()

    if suffix in {".h5", ".keras"}:
        return _load_keras_model(path)

    if suffix == ".onnx":
        return _load_onnx_model(path)

    if suffix in {".pt", ".pth"}:
        return _load_torchscript_model(path)

    print(f"Unsupported model extension: {suffix}")
    return None


def _load_keras_model(path: Path):
    try:
        from tensorflow.keras.models import load_model
    except ImportError:
        return None

    try:
        return LoadedModel(load_model(path), backend="keras", path=path)
    except Exception as exc:
        print("Keras model load error:", exc)
        return None


def _load_onnx_model(path: Path):
    try:
        import onnxruntime as ort
    except ImportError:
        return None

    try:
        return LoadedModel(ort.InferenceSession(str(path), providers=["CPUExecutionProvider"]), backend="onnx", path=path)
    except Exception as exc:
        print("ONNX model load error:", exc)
        return None


def _load_torchscript_model(path: Path):
    try:
        import torch
    except ImportError:
        return None

    try:
        model = torch.jit.load(str(path), map_location="cpu")
        model.eval()
        return LoadedModel(model, backend="torchscript", path=path)
    except Exception as exc:
        print("TorchScript model load error:", exc)
        return None


def is_model_ready() -> bool:
    return load_deepfake_model() is not None


def clear_model_cache():
    load_deepfake_model.cache_clear()
