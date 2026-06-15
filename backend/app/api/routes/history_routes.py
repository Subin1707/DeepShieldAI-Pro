from fastapi import APIRouter, HTTPException, Query

from app.database.repositories.analysis_repository import get_analysis_by_id, list_analyses
from app.utils.response_utils import paginated_response, success_response

router = APIRouter(prefix="/history", tags=["History"])


@router.get("")
def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    offset = (page - 1) * page_size
    items, total = list_analyses(limit=page_size, offset=offset)
    return paginated_response(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        message="Analysis history loaded.",
    )


@router.get("/{analysis_id}")
def get_history_detail(analysis_id: str):
    item = get_analysis_by_id(analysis_id)
    if item:
        return success_response(data=item, message="Analysis detail loaded.")

    raise HTTPException(status_code=404, detail="Analysis not found.")
