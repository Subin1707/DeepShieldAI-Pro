import argparse
import gc
import json
import math
import os
import random
import shutil
import sys
from datetime import datetime
from pathlib import Path

os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.face_detector import crop_face_or_frame


FAKE_METHODS = [
    "DeepFakeDetection",
    "Deepfakes",
    "Face2Face",
    "FaceShifter",
    "FaceSwap",
    "NeuralTextures",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Train a temporal video deepfake model from FaceForensics++ videos.")
    parser.add_argument("--source", required=True, help="FaceForensics++ C23 root folder.")
    parser.add_argument("--output", default="models/video_deepfake.keras")
    parser.add_argument("--sequence-length", type=int, default=16)
    parser.add_argument("--image-size", type=int, default=160)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--backbone", choices=["tiny", "mobilenet", "efficientnet"], default="tiny")
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--max-real-videos", type=int, default=0)
    parser.add_argument("--max-fake-videos-per-method", type=int, default=0)
    parser.add_argument("--methods", nargs="*", default=FAKE_METHODS)
    parser.add_argument("--no-balance", action="store_true", help="Do not downsample classes to a balanced real/fake set.")
    parser.add_argument("--resume", action="store_true", help="Resume training from --output when it already exists.")
    parser.add_argument("--log-dir", default="training_logs/video_temporal")
    parser.add_argument("--run-id", default="", help="Optional stable run id. Defaults to a timestamped id.")
    parser.add_argument("--tensorboard", action="store_true", help="Enable TensorBoard logging when tensorboard is installed.")
    return parser.parse_args()


def list_videos(folder: Path, limit: int = 0) -> list[Path]:
    videos = sorted(folder.glob("*.mp4"))
    return videos[:limit] if limit > 0 else videos


def build_samples(
    source: Path,
    methods: list[str],
    max_real: int,
    max_fake_per_method: int,
    balance: bool = True,
) -> list[tuple[Path, int]]:
    real_videos = [(path, 0) for path in list_videos(source / "original", max_real)]
    fake_videos = []
    for method in methods:
        method_dir = source / method
        if not method_dir.exists():
            print(f"Skip missing method: {method_dir}")
            continue
        fake_videos.extend((path, 1) for path in list_videos(method_dir, max_fake_per_method))

    rng = random.Random(42)
    rng.shuffle(real_videos)
    rng.shuffle(fake_videos)

    if balance:
        keep = min(len(real_videos), len(fake_videos))
        real_videos = real_videos[:keep]
        fake_videos = fake_videos[:keep]

    samples = real_videos + fake_videos
    rng.shuffle(samples)
    return samples


def split_balanced(samples: list[tuple[Path, int]], validation_split: float) -> tuple[list[tuple[Path, int]], list[tuple[Path, int]]]:
    rng = random.Random(123)
    real = [sample for sample in samples if sample[1] == 0]
    fake = [sample for sample in samples if sample[1] == 1]
    rng.shuffle(real)
    rng.shuffle(fake)

    def split_class(items):
        cut = int(len(items) * (1 - validation_split))
        return items[:cut], items[cut:]

    train_real, val_real = split_class(real)
    train_fake, val_fake = split_class(fake)
    train = train_real + train_fake
    val = val_real + val_fake
    rng.shuffle(train)
    rng.shuffle(val)
    return train, val


def sample_indices(total_frames: int, sequence_length: int) -> list[int]:
    if total_frames <= 0:
        return []
    if total_frames == 1:
        return [0] * sequence_length
    return [round(i * (total_frames - 1) / (sequence_length - 1)) for i in range(sequence_length)]


def load_video_sequence(video_path: Path, sequence_length: int, image_size: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not read video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    last_frame = None

    for frame_index in sample_indices(total_frames, sequence_length):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            frame = last_frame
        if frame is None:
            frame = np.zeros((image_size, image_size, 3), dtype=np.uint8)

        crop, _ = crop_face_or_frame(frame)
        crop = cv2.resize(crop, (image_size, image_size))
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        frames.append(crop.astype("uint8"))
        last_frame = frame

    cap.release()
    return np.stack(frames, axis=0)


def get_sequence_base():
    from tensorflow import keras

    return keras.utils.Sequence


class VideoSequence(get_sequence_base()):
    def __init__(self, samples, batch_size: int, sequence_length: int, image_size: int, shuffle: bool = True):
        super().__init__()
        self.samples = list(samples)
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.image_size = image_size
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        return math.ceil(len(self.samples) / self.batch_size)

    def __getitem__(self, index):
        batch = self.samples[index * self.batch_size : (index + 1) * self.batch_size]
        x = np.stack(
            [load_video_sequence(path, self.sequence_length, self.image_size) for path, _ in batch],
            axis=0,
        )
        y = np.asarray([label for _, label in batch], dtype="float32")
        gc.collect()
        return x, y

    def on_epoch_end(self):
        if self.shuffle:
            random.shuffle(self.samples)


def build_frame_encoder(backbone: str, image_size: int):
    from tensorflow import keras
    from tensorflow.keras import layers

    if backbone == "efficientnet":
        frame_encoder = keras.applications.EfficientNetB0(
            include_top=False,
            weights="imagenet",
            input_shape=(image_size, image_size, 3),
            pooling="avg",
        )
        frame_encoder.trainable = False
        return frame_encoder

    if backbone == "mobilenet":
        frame_encoder = keras.applications.MobileNetV2(
            include_top=False,
            weights="imagenet",
            input_shape=(image_size, image_size, 3),
            pooling="avg",
            alpha=0.35,
        )
        frame_encoder.trainable = False
        return frame_encoder

    inputs = keras.Input(shape=(image_size, image_size, 3), dtype="uint8")
    x = layers.Rescaling(1.0 / 255.0)(inputs)
    x = layers.Conv2D(24, 3, strides=2, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.SeparableConv2D(48, 3, strides=2, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.SeparableConv2D(96, 3, strides=2, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.SeparableConv2D(128, 3, strides=2, padding="same", activation="relu")(x)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu")(x)
    return keras.Model(inputs, x, name="tiny_frame_encoder")


def build_model(sequence_length: int, image_size: int, learning_rate: float, backbone: str):
    from tensorflow import keras
    from tensorflow.keras import layers

    frame_encoder = build_frame_encoder(backbone, image_size)
    frame_encoder.trainable = backbone == "tiny"

    inputs = keras.Input(shape=(sequence_length, image_size, image_size, 3), dtype="uint8")
    x = layers.TimeDistributed(frame_encoder)(inputs)
    x = layers.Bidirectional(layers.GRU(64, return_sequences=True))(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Bidirectional(layers.GRU(32))(x)
    x = layers.Dropout(0.35)(x)
    outputs = layers.Dense(1, activation="sigmoid", name="fake_probability")(x)
    model = keras.Model(inputs, outputs)

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate),
        loss="binary_crossentropy",
        metrics=[
            keras.metrics.BinaryAccuracy(name="accuracy"),
            keras.metrics.AUC(name="auc"),
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def build_run_id(prefix: str = "video") -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def archive_existing_latest_history(log_dir: Path, latest_history_path: Path) -> None:
    if not latest_history_path.exists() or latest_history_path.stat().st_size == 0:
        return

    runs_dir = log_dir / "runs"
    if any(runs_dir.glob("*/history.csv")):
        return

    legacy_dir = runs_dir / f"legacy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(latest_history_path, legacy_dir / "history.csv")
    latest_report = log_dir / "validation_report.json"
    if latest_report.exists() and latest_report.stat().st_size > 0:
        shutil.copyfile(latest_report, legacy_dir / "validation_report.json")
    write_json(
        legacy_dir / "manifest.json",
        {
            "runId": legacy_dir.name,
            "createdAt": datetime.utcnow().isoformat(),
            "modelType": "video_temporal",
            "importedFrom": str(latest_history_path),
        },
    )


def class_counts(samples: list[tuple[Path, int]]) -> dict:
    return {
        "real": sum(1 for _, label in samples if label == 0),
        "fake": sum(1 for _, label in samples if label == 1),
    }


def save_validation_report(model, val_seq, run_dir: Path, args, run_id: str) -> dict:
    from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support, roc_auc_score

    y_true = np.asarray([label for _, label in val_seq.samples], dtype="int32")
    probabilities = np.asarray(model.predict(val_seq, verbose=0)).reshape(-1)
    y_pred = (probabilities >= 0.5).astype("int32")
    labels = [0, 1]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )
    auc = roc_auc_score(y_true, probabilities) if len(set(y_true.tolist())) > 1 else None
    report = {
        "runId": run_id,
        "modelType": "video_temporal",
        "threshold": 0.5,
        "sampleCount": int(len(y_true)),
        "classCounts": class_counts(val_seq.samples),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "auc": float(auc) if auc is not None else None,
        "confusionMatrix": {
            "labels": ["real", "fake"],
            "matrix": matrix.astype(int).tolist(),
            "tn": int(matrix[0][0]),
            "fp": int(matrix[0][1]),
            "fn": int(matrix[1][0]),
            "tp": int(matrix[1][1]),
        },
        "perClass": {
            "real": {"precision": float(precision[0]), "recall": float(recall[0]), "f1": float(f1[0])},
            "fake": {"precision": float(precision[1]), "recall": float(recall[1]), "f1": float(f1[1])},
        },
        "config": {
            "sequenceLength": args.sequence_length,
            "imageSize": args.image_size,
            "batchSize": args.batch_size,
            "backbone": args.backbone,
            "validationSplit": args.validation_split,
        },
    }
    write_json(run_dir / "validation_report.json", report)
    return report


def main():
    args = parse_args()
    source = Path(args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    samples = build_samples(
        source,
        args.methods,
        args.max_real_videos,
        args.max_fake_videos_per_method,
        balance=not args.no_balance,
    )
    if not samples:
        raise ValueError("No training videos found.")

    train_samples, val_samples = split_balanced(samples, args.validation_split)
    train_counts = class_counts(train_samples)
    val_counts = class_counts(val_samples)

    print(f"Train videos: {len(train_samples)}")
    print(f"Validation videos: {len(val_samples)}")
    print(f"Train balance: real={train_counts['real']}, fake={train_counts['fake']}")
    print(f"Validation balance: real={val_counts['real']}, fake={val_counts['fake']}")

    train_seq = VideoSequence(train_samples, args.batch_size, args.sequence_length, args.image_size, shuffle=True)
    val_seq = VideoSequence(val_samples, args.batch_size, args.sequence_length, args.image_size, shuffle=False)

    from tensorflow import keras

    output_exists = output.exists() and output.stat().st_size > 0
    if args.resume and output_exists:
        print(f"Resuming from existing model: {output}")
        model = keras.models.load_model(output)
    else:
        model = build_model(args.sequence_length, args.image_size, args.learning_rate, args.backbone)
    model.summary()

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or build_run_id()
    run_dir = log_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    history_path = run_dir / "history.csv"
    latest_history_path = log_dir / "history.csv"
    archive_existing_latest_history(log_dir, latest_history_path)

    write_json(
        run_dir / "manifest.json",
        {
            "runId": run_id,
            "createdAt": datetime.utcnow().isoformat(),
            "modelType": "video_temporal",
            "source": str(source),
            "output": str(output),
            "resume": args.resume,
            "methods": args.methods,
            "balanced": not args.no_balance,
            "totalSamples": len(samples),
            "trainSamples": len(train_samples),
            "validationSamples": len(val_samples),
            "trainClassCounts": train_counts,
            "validationClassCounts": val_counts,
            "config": vars(args),
        },
    )

    callbacks = [
        keras.callbacks.ModelCheckpoint(str(output), save_best_only=True, monitor="val_auc", mode="max"),
        keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True, monitor="val_auc", mode="max"),
        keras.callbacks.ReduceLROnPlateau(patience=2, factor=0.3, monitor="val_loss"),
        keras.callbacks.CSVLogger(str(history_path), append=False),
    ]
    if args.tensorboard:
        try:
            import tensorboard  # noqa: F401

            callbacks.append(keras.callbacks.TensorBoard(log_dir=str(run_dir / "tensorboard")))
        except ImportError:
            print("TensorBoard chưa được cài, bỏ qua TensorBoard callback.")

    model.fit(train_seq, validation_data=val_seq, epochs=args.epochs, callbacks=callbacks)
    save_validation_report(model, val_seq, run_dir, args, run_id)
    model.save(output)
    shutil.copyfile(history_path, latest_history_path)
    shutil.copyfile(run_dir / "validation_report.json", log_dir / "validation_report.json")
    print(f"Saved temporal video model to {output}")
    print(f"Saved training run to {run_dir}")


if __name__ == "__main__":
    main()
