from functools import lru_cache
from importlib import import_module
from pathlib import Path

from app.core.config import settings


class LoadedModel:
    def __init__(self, model, backend: str, path: Path):
        self.model = model
        self.backend = backend
        self.path = path
        self.image_size = infer_model_image_size(model, backend)

    def predict(self, input_tensor):
        if self.backend == "keras":
            return self.model.predict(input_tensor, verbose=0)

        if self.backend == "onnx":
            input_name = self.model.get_inputs()[0].name
            return self.model.run(None, {input_name: input_tensor.astype("float32")})[0]

        if self.backend == "torchscript":
            torch = import_module("torch")

            tensor = torch.from_numpy(input_tensor).permute(0, 3, 1, 2).float()
            with torch.no_grad():
                output = self.model(tensor)
            return output.detach().cpu().numpy()

        raise ValueError(f"Unsupported model backend: {self.backend}")


def get_model_path() -> Path:
    return Path(settings.MODEL_PATH)


def _shape_dim(value) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _infer_image_size_from_shape(shape) -> int | None:
    if isinstance(shape, list) and shape and isinstance(shape[0], (list, tuple)):
        shape = shape[0]

    if not isinstance(shape, (list, tuple)) or len(shape) != 4:
        return None

    dims = [_shape_dim(dim) for dim in shape]
    if dims[-1] == 3 and dims[1] and dims[2] and dims[1] == dims[2]:
        return dims[1]
    if dims[1] == 3 and dims[2] and dims[3] and dims[2] == dims[3]:
        return dims[2]
    return None


def infer_model_image_size(model, backend: str | None = None) -> int:
    if backend == "onnx" and hasattr(model, "get_inputs"):
        try:
            size = _infer_image_size_from_shape(model.get_inputs()[0].shape)
            if size:
                return size
        except Exception:
            pass

    for attr in ("input_shape", "inputs"):
        try:
            value = getattr(model, attr, None)
            if attr == "inputs" and value:
                value = getattr(value[0], "shape", None)
            size = _infer_image_size_from_shape(value)
            if size:
                return size
        except Exception:
            pass

    return settings.IMAGE_MODEL_SIZE


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
        "imageSize": loaded_model.image_size if loaded_model else settings.IMAGE_MODEL_SIZE,
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
        from keras.models import load_model
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
        torch = import_module("torch")
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
