#!/usr/bin/env python3
"""Build the static GitHub Pages dashboard from data/pipeline.csv."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

STAGE_LABELS = {
    0: "No dedicated human-vaccine pathway / gap lane",
    1: "Discovery / translational",
    2: "Preclinical or manufacturing-enabling",
    3: "Phase 1",
    4: "Phase 2",
    5: "Efficacy / Phase 3",
    6: "Regulatory authorization / WHO prequalification",
    7: "Programmatic use / stockpile / post-licensure",
}

CSV_EXPORT_NAME = "flavivirus_vaccine_development_pipeline_data.csv"
REPORT_EXPORT_NAME = "automation_summary.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_rows(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            row = dict(row)
            try:
                row["stage_order"] = int(row.get("stage_order", 0) or 0)
            except ValueError:
                row["stage_order"] = 0
            try:
                row["supporting_record_count"] = int(row.get("supporting_record_count", 0) or 0)
            except ValueError:
                row["supporting_record_count"] = 0
            rows.append(row)
    return rows


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Render static flavivirus vaccine dashboard HTML.")
    parser.add_argument("--data", default="data/pipeline.csv", help="Input pipeline CSV")
    parser.add_argument("--template", default="scripts/dashboard_template.html", help="HTML template")
    parser.add_argument("--out", default="public/index.html", help="Output dashboard HTML")
    parser.add_argument("--report", default="reports/automation_summary.md", help="Input automation summary")
    args = parser.parse_args(argv)

    data_path = Path(args.data)
    template_path = Path(args.template)
    out_path = Path(args.out)
    public_dir = out_path.parent
    rows = read_rows(data_path)
    built_at = utc_now()

    html = template_path.read_text(encoding="utf-8")
    html = html.replace("__DATA_JSON__", json.dumps(rows, ensure_ascii=False))
    html = html.replace("__STAGES_JSON__", json.dumps(STAGE_LABELS, ensure_ascii=False))
    html = html.replace("__BUILT_AT__", built_at)
    html = html.replace("__CSV_NAME__", CSV_EXPORT_NAME)
    html = html.replace("__REPORT_NAME__", REPORT_EXPORT_NAME)

    public_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    shutil.copyfile(data_path, public_dir / CSV_EXPORT_NAME)
    report_path = Path(args.report)
    if report_path.exists():
        shutil.copyfile(report_path, public_dir / REPORT_EXPORT_NAME)
    else:
        (public_dir / REPORT_EXPORT_NAME).write_text("# Automation summary\n\nNo report generated.\n", encoding="utf-8")
    print(f"Wrote {out_path} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
