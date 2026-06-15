from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def success_response(
    data: Any = None,
    message: str = "Success",
    status: str = "success",
) -> dict:
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": utc_now_iso(),
    }


def error_response(
    message: str,
    error_code: str | None = None,
    details: Any = None,
    status: str = "error",
) -> dict:
    return {
        "status": status,
        "message": message,
        "errorCode": error_code,
        "details": details,
        "timestamp": utc_now_iso(),
    }


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
) -> dict:
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return success_response(
        data={
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrevious": page > 1,
            },
        },
        message=message,
    )
