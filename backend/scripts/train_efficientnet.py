import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")


def parse_args():
    parser = argparse.ArgumentParser(description="Train an EfficientNet deepfake image classifier.")
    parser.add_argument("--data-dir", required=True, help="Dataset root containing real/ and fake/ folders.")
    parser.add_argument("--output", default="models/efficientnet_deepfake.keras", help="Model output path.")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--fine-tune-epochs", type=int, default=6)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--fine-tune-learning-rate", type=float, default=1e-5)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--prefetch-size", type=int, default=1)
    parser.add_argument("--log-dir", default="training_logs/efficientnet")
    parser.add_argument("--run-id", default="", help="Optional stable run id. Defaults to a timestamped id.")
    parser.add_argument("--append-log", action="store_true", help="Append metrics to an existing history.csv instead of replacing it.")
    return parser.parse_args()


def build_run_id(prefix: str = "efficientnet") -> str:
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
            "modelType": "efficientnet_image",
            "importedFrom": str(latest_history_path),
        },
    )


def dataset_labels(dataset):
    import numpy as np

    labels = []
    for _, batch_labels in dataset:
        labels.extend(np.asarray(batch_labels).reshape(-1).astype("int32").tolist())
    return np.asarray(labels, dtype="int32")


def save_validation_report(model, val_ds, run_dir: Path, args, run_id: str) -> dict:
    import numpy as np
    from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support, roc_auc_score

    y_true = dataset_labels(val_ds)
    probabilities = np.asarray(model.predict(val_ds, verbose=0)).reshape(-1)
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
        "modelType": "efficientnet_image",
        "threshold": 0.5,
        "sampleCount": int(len(y_true)),
        "classCounts": {
            "real": int((y_true == 0).sum()),
            "fake": int((y_true == 1).sum()),
        },
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
            "imageSize": args.image_size,
            "batchSize": args.batch_size,
            "validationSplit": args.validation_split,
            "epochs": args.epochs,
            "fineTuneEpochs": args.fine_tune_epochs,
        },
    }
    write_json(run_dir / "validation_report.json", report)
    return report


def main():
    args = parse_args()

    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    data_dir = Path(args.data_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or build_run_id()
    run_dir = log_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    history_path = run_dir / "history.csv"
    latest_history_path = log_dir / "history.csv"
    archive_existing_latest_history(log_dir, latest_history_path)

    train_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="binary",
        validation_split=args.validation_split,
        subset="training",
        seed=42,
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
    )
    val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="binary",
        validation_split=args.validation_split,
        subset="validation",
        seed=42,
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
    )

    class_names = train_ds.class_names
    print("Class order:", class_names)
    if "fake" not in class_names or "real" not in class_names:
        raise ValueError("Dataset must contain folders named real and fake.")

    fake_index = class_names.index("fake")
    if fake_index != 1:
        print("Remapping labels so the sigmoid output remains FAKE probability.")

        def to_fake_probability_label(images, labels):
            labels = tf.cast(tf.equal(tf.cast(labels, tf.int32), fake_index), tf.float32)
            return images, labels

        train_ds = train_ds.map(to_fake_probability_label, num_parallel_calls=tf.data.AUTOTUNE)
        val_ds = val_ds.map(to_fake_probability_label, num_parallel_calls=tf.data.AUTOTUNE)

    autotune = tf.data.AUTOTUNE
    prefetch_size = autotune if args.prefetch_size <= 0 else args.prefetch_size
    train_ds = train_ds.prefetch(prefetch_size)
    val_ds = val_ds.prefetch(prefetch_size)

    write_json(
        run_dir / "manifest.json",
        {
            "runId": run_id,
            "createdAt": datetime.utcnow().isoformat(),
            "modelType": "efficientnet_image",
            "dataDir": str(data_dir),
            "output": str(output_path),
            "classNames": class_names,
            "config": vars(args),
        },
    )

    augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.04),
            layers.RandomZoom(0.08),
            layers.RandomContrast(0.12),
        ],
        name="augmentation",
    )

    base = keras.applications.EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(args.image_size, args.image_size, 3),
    )
    base.trainable = False

    inputs = keras.Input(shape=(args.image_size, args.image_size, 3))
    x = augmentation(inputs)
    x = keras.applications.efficientnet.preprocess_input(x)
    x = base(x, training=False)
    attention = layers.Conv2D(1, 1, activation="sigmoid", name="spatial_attention")(x)
    x = layers.Multiply(name="attention_weighted_features")([x, attention])
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.35)(x)
    outputs = layers.Dense(1, activation="sigmoid", name="fake_probability")(x)
    model = keras.Model(inputs, outputs)

    metrics = [
        keras.metrics.BinaryAccuracy(name="accuracy"),
        keras.metrics.AUC(name="auc"),
        keras.metrics.Precision(name="precision"),
        keras.metrics.Recall(name="recall"),
    ]
    model.compile(
        optimizer=keras.optimizers.Adam(args.learning_rate),
        loss="binary_crossentropy",
        metrics=metrics,
    )

    def build_callbacks(append_history: bool):
        return [
            keras.callbacks.ModelCheckpoint(str(output_path), save_best_only=True, monitor="val_auc", mode="max"),
            keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True, monitor="val_auc", mode="max"),
            keras.callbacks.ReduceLROnPlateau(patience=2, factor=0.3, monitor="val_loss"),
            keras.callbacks.CSVLogger(str(history_path), append=append_history),
        ]

    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=build_callbacks(False))

    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(args.fine_tune_learning_rate),
        loss="binary_crossentropy",
        metrics=metrics,
    )
    model.fit(train_ds, validation_data=val_ds, epochs=args.fine_tune_epochs, callbacks=build_callbacks(True))
    save_validation_report(model, val_ds, run_dir, args, run_id)
    model.save(output_path)
    shutil.copyfile(history_path, latest_history_path)
    shutil.copyfile(run_dir / "validation_report.json", log_dir / "validation_report.json")
    print(f"Saved model to {output_path}")
    print(f"Saved training run to {run_dir}")
    print(f"Saved latest training history to {latest_history_path}")


if __name__ == "__main__":
    main()
