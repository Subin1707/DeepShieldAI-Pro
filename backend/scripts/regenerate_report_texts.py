import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import settings  # noqa: E402
from app.services.ai_text_service import fallback_report  # noqa: E402
from app.services.report_service import build_report_text  # noqa: E402


def main() -> None:
    report_dir = ROOT / settings.REPORT_DIR
    if not report_dir.exists():
        print(f"Report directory not found: {report_dir}")
        return

    count = 0
    for json_path in sorted(report_dir.glob("*.json")):
        result = json.loads(json_path.read_text(encoding="utf-8"))
        result["reportId"] = result.get("reportId") or json_path.stem
        result["aiReport"] = fallback_report(result)
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        txt_path = json_path.with_suffix(".txt")
        txt_path.write_text(build_report_text(result), encoding="utf-8")
        count += 1

    print(f"Regenerated {count} report text files.")


if __name__ == "__main__":
    main()
