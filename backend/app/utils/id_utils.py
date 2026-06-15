import uuid
from datetime import datetime


def generate_analysis_id() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = str(uuid.uuid4())[:8].upper()
    return f"ANL-{date_part}-{random_part}"


def generate_report_id() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = str(uuid.uuid4())[:8].upper()
    return f"RPT-{date_part}-{random_part}"


def generate_short_id(prefix: str) -> str:
    clean_prefix = prefix.strip().upper()
    random_part = str(uuid.uuid4())[:8].upper()
    return f"{clean_prefix}-{random_part}"
