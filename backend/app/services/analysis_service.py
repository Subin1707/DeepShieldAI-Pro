from datetime import datetime
from time import perf_counter

from fastapi import HTTPException, UploadFile

from app.ai.deepfake_pipeline import run_deepfake_pipeline
from app.ai.hybrid_forensics import fuse_deepfake_and_forensics, run_hybrid_forensics
from app.core.config import settings
from app.database.repositories.analysis_repository import create_analysis
from app.services.ai_text_service import generate_deepfake_report
from app.services.gradcam_service import build_heatmap_url, generate_saliency_heatmap
from app.services.image_service import get_image_metadata, save_image_frame
from app.services.report_service import save_analysis_report
from app.services.training_history_service import load_training_history
from app.services.video_service import get_video_metadata, sample_video_frames
from app.utils.file_utils import is_image_file, save_upload_file
from app.utils.id_utils import generate_analysis_id


async def analyze_uploaded_file(file: UploadFile) -> dict:
    started_at = perf_counter()
    timings = {}
    settings.ensure_storage_dirs()
    analysis_id = generate_analysis_id()

    try:
        stage_started = perf_counter()
        file_path = await save_upload_file(
            file=file,
            upload_dir=settings.UPLOAD_DIR,
            analysis_id=analysis_id,
        )
        timings["uploadMs"] = round((perf_counter() - stage_started) * 1000, 2)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        stage_started = perf_counter()
        if is_image_file(file_path):
            media_metadata = get_image_metadata(file_path)
            frame_paths = [save_image_frame(file_path, analysis_id)]
            is_video = False
        else:
            media_metadata = get_video_metadata(file_path)
            frame_paths = sample_video_frames(file_path, analysis_id)
            is_video = True
        timings["preprocessMs"] = round((perf_counter() - stage_started) * 1000, 2)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        stage_started = perf_counter()
        result = run_deepfake_pipeline(frame_paths=frame_paths, analysis_id=analysis_id, is_video=is_video)
        timings.update(result.get("processingTimes") or {})
        timings["inferenceMs"] = round((perf_counter() - stage_started) * 1000, 2)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    result["analysisId"] = analysis_id
    result["fileName"] = file.filename
    result["filePath"] = file_path
    result["media"] = media_metadata
    result["sampledFrames"] = frame_paths
    result["createdAt"] = datetime.utcnow().isoformat()

    stage_started = perf_counter()
    hybrid = run_hybrid_forensics(file_path=file_path, frame_paths=frame_paths)
    timings.update(hybrid.get("processingTimes") or {})
    timings["hybridForensicsMs"] = round((perf_counter() - stage_started) * 1000, 2)
    result = fuse_deepfake_and_forensics(result, hybrid)

    suspicious = sorted(
        result.get("frameResults", []),
        key=lambda item: item.get("fakeProbability", 0),
        reverse=True,
    )
    heatmap_source = (
        suspicious[0].get("facePath")
        if suspicious and suspicious[0].get("facePath")
        else frame_paths[0] if frame_paths else file_path
    )
    heatmap_face_metadata = suspicious[0].get("face") if suspicious else None
    stage_started = perf_counter()
    heatmap = generate_saliency_heatmap(heatmap_source, analysis_id, heatmap_face_metadata)
    timings["explainabilityMs"] = round((perf_counter() - stage_started) * 1000, 2)
    result["heatmapUrl"] = build_heatmap_url(analysis_id)
    result["suspiciousRegions"] = heatmap["regions"]
    result["heatmapMethod"] = heatmap.get("method", "saliency_fallback")
    result["heatmapFaceBoxSource"] = heatmap.get("faceBoxSource")
    result["trainingHistory"] = load_training_history()

    stage_started = perf_counter()
    result["aiReport"] = generate_deepfake_report(result)
    timings["aiReportMs"] = round((perf_counter() - stage_started) * 1000, 2)
    timings["totalMs"] = round((perf_counter() - started_at) * 1000, 2)
    result["processingTimes"] = timings

    result.update(save_analysis_report(result))
    create_analysis(result)

    return result
