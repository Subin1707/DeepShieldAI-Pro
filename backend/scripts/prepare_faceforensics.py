import argparse
import gc
import sys
from pathlib import Path

import cv2

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
    parser = argparse.ArgumentParser(description="Prepare FaceForensics++ videos as image folders for training.")
    parser.add_argument("--source", required=True, help="FaceForensics++ C23 root folder.")
    parser.add_argument("--output", default="data/train_dataset", help="Output folder containing real/ and fake/.")
    parser.add_argument("--frames-per-video", type=int, default=8)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--max-real-videos", type=int, default=0, help="0 means all real videos.")
    parser.add_argument("--max-fake-videos-per-method", type=int, default=0, help="0 means all fake videos.")
    parser.add_argument("--max-real-images", type=int, default=0, help="0 means no image limit.")
    parser.add_argument("--max-fake-images", type=int, default=0, help="0 means no image limit.")
    parser.add_argument(
        "--crop-mode",
        choices=("face", "frame"),
        default="face",
        help="face crops the detected face; frame resizes the full frame and is much faster.",
    )
    parser.add_argument("--methods", nargs="*", default=FAKE_METHODS, help="Fake method folders to include.")
    parser.add_argument(
        "--sampling-mode",
        choices=("scan", "seek"),
        default="scan",
        help="scan reads each video forward once; seek uses random frame seeks.",
    )
    return parser.parse_args()


def sample_indices(total_frames: int, count: int) -> list[int]:
    if total_frames <= 0 or count <= 0:
        return []
    count = min(count, total_frames)
    if count == 1:
        return [total_frames // 2]
    return [round(i * (total_frames - 1) / (count - 1)) for i in range(count)]


def save_frame(frame, output_path: Path, image_size: int, crop_mode: str) -> bool:
    crop = frame
    if crop_mode == "face":
        crop, _ = crop_face_or_frame(frame)
    resized = cv2.resize(crop, (image_size, image_size))
    return cv2.imwrite(str(output_path), resized)


def extract_video_frames_seek(
    cap: cv2.VideoCapture,
    video_path: Path,
    output_dir: Path,
    prefix: str,
    frame_indices: list[int],
    image_size: int,
    crop_mode: str,
) -> int:
    saved = 0
    for frame_index in frame_indices:
        output_path = output_dir / f"{prefix}_f{frame_index:05d}.jpg"
        if output_path.exists() and output_path.stat().st_size > 0:
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        try:
            ok, frame = cap.read()
        except cv2.error as exc:
            print(f"Skip frame {frame_index} in {video_path}: {exc}")
            gc.collect()
            continue

        if not ok or frame is None:
            continue

        try:
            if save_frame(frame, output_path, image_size, crop_mode):
                saved += 1
        except cv2.error as exc:
            print(f"Skip frame {frame_index} in {video_path}: {exc}")
        finally:
            del frame
            gc.collect()
    return saved


def extract_video_frames_scan(
    cap: cv2.VideoCapture,
    video_path: Path,
    output_dir: Path,
    prefix: str,
    frame_indices: list[int],
    image_size: int,
    crop_mode: str,
) -> int:
    pending = {}
    for frame_index in frame_indices:
        output_path = output_dir / f"{prefix}_f{frame_index:05d}.jpg"
        if not output_path.exists() or output_path.stat().st_size == 0:
            pending[frame_index] = output_path

    if not pending:
        return 0

    saved = 0
    current_index = 0
    last_target = max(pending)
    while current_index <= last_target:
        try:
            ok, frame = cap.read()
        except cv2.error as exc:
            print(f"Skip remaining frames in {video_path}: {exc}")
            gc.collect()
            break

        if not ok or frame is None:
            break

        output_path = pending.get(current_index)
        if output_path is not None:
            try:
                if save_frame(frame, output_path, image_size, crop_mode):
                    saved += 1
            except cv2.error as exc:
                print(f"Skip frame {current_index} in {video_path}: {exc}")
            finally:
                gc.collect()

            if saved == len(pending):
                del frame
                break

        del frame
        current_index += 1

    return saved


def extract_video_frames(
    video_path: Path,
    output_dir: Path,
    prefix: str,
    frames_per_video: int,
    image_size: int,
    sampling_mode: str,
    crop_mode: str,
) -> int:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Skip unreadable video: {video_path}")
        return 0

    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = sample_indices(total_frames, frames_per_video)
        if not frame_indices:
            print(f"Skip video with no readable frame count: {video_path}")
            return 0

        if sampling_mode == "seek":
            return extract_video_frames_seek(cap, video_path, output_dir, prefix, frame_indices, image_size, crop_mode)
        return extract_video_frames_scan(cap, video_path, output_dir, prefix, frame_indices, image_size, crop_mode)
    finally:
        cap.release()
        gc.collect()


def prepare_split(
    videos: list[Path],
    output_dir: Path,
    label: str,
    frames_per_video: int,
    image_size: int,
    sampling_mode: str,
    max_images: int,
    crop_mode: str,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    total_saved = 0

    for index, video_path in enumerate(videos, start=1):
        if max_images > 0 and total_saved >= max_images:
            break

        prefix = f"{label}_{video_path.parent.name}_{video_path.stem}"
        saved = extract_video_frames(video_path, output_dir, prefix, frames_per_video, image_size, sampling_mode, crop_mode)
        total_saved += saved

        if max_images > 0 and total_saved > max_images:
            overflow = total_saved - max_images
            created_files = sorted(output_dir.glob(f"{prefix}_*.jpg"), key=lambda path: path.stat().st_mtime, reverse=True)
            for extra_path in created_files[:overflow]:
                extra_path.unlink(missing_ok=True)
            total_saved = max_images

        if index == 1 or index % 10 == 0:
            print(f"{label}: processed {index}/{len(videos)} videos, saved {total_saved} images")

    return total_saved


def list_videos(folder: Path, limit: int = 0) -> list[Path]:
    videos = sorted(folder.glob("*.mp4"))
    return videos[:limit] if limit > 0 else videos


def first_existing_path(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def resolve_real_dir(source: Path) -> Path:
    real_dir = first_existing_path(
        [
            source / "original",
            source / "original_sequences" / "youtube" / "c23" / "videos",
        ]
    )
    if real_dir is None:
        raise FileNotFoundError(
            "Missing real videos folder. Expected either "
            f"{source / 'original'} or "
            f"{source / 'original_sequences' / 'youtube' / 'c23' / 'videos'}"
        )
    return real_dir


def resolve_fake_method_dir(source: Path, method: str) -> Path | None:
    return first_existing_path(
        [
            source / method,
            source / "manipulated_sequences" / method / "c23" / "videos",
        ]
    )


def main():
    args = parse_args()
    source = Path(args.source)
    output = Path(args.output)

    real_dir = resolve_real_dir(source)
    real_videos = list_videos(real_dir, args.max_real_videos)

    fake_videos = []
    for method in args.methods:
        method_dir = resolve_fake_method_dir(source, method)
        if method_dir is None:
            print(f"Skip missing method folder: {source / method}")
            print(f"Skip missing official method folder: {source / 'manipulated_sequences' / method / 'c23' / 'videos'}")
            continue
        fake_videos.extend(list_videos(method_dir, args.max_fake_videos_per_method))

    print(f"Real videos: {len(real_videos)}")
    print(f"Fake videos: {len(fake_videos)}")
    print(f"Output: {output}")

    real_saved = prepare_split(
        real_videos,
        output / "real",
        "real",
        frames_per_video=args.frames_per_video,
        image_size=args.image_size,
        sampling_mode=args.sampling_mode,
        max_images=args.max_real_images,
        crop_mode=args.crop_mode,
    )
    fake_saved = prepare_split(
        fake_videos,
        output / "fake",
        "fake",
        frames_per_video=args.frames_per_video,
        image_size=args.image_size,
        sampling_mode=args.sampling_mode,
        max_images=args.max_fake_images,
        crop_mode=args.crop_mode,
    )

    print(f"Done. Saved {real_saved} real images and {fake_saved} fake images.")


if __name__ == "__main__":
    main()
