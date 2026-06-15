from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import validate_upload_dependency
from app.services.analysis_service import analyze_uploaded_file
from app.utils.response_utils import success_response

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("")
async def analyze_file(file: UploadFile = Depends(validate_upload_dependency)):
    result = await analyze_uploaded_file(file)
    return success_response(data=result, message="Analysis completed.")
