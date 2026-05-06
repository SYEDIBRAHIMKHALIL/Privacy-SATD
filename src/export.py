from __future__ import annotations

from pathlib import Path
import csv
import json


def export_jsonl(items: list[dict], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def export_csv(items: list[dict], out_path: Path) -> None:
    if not items:
        out_path.write_text("", encoding="utf-8")
        return

    fieldnames = sorted({key for item in items for key in item.keys()})
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def export_summary(items: list[dict], out_path: Path) -> None:
    summary = {
        "total_instances": len(items),
        "by_source_type": {},
    }
    for item in items:
        source = item.get("source_type", "unknown")
        summary["by_source_type"][source] = summary["by_source_type"].get(source, 0) + 1
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
