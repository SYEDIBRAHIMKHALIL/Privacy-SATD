from __future__ import annotations

from pathlib import Path
import json


def write_label_studio_tasks(instances: list[dict], out_path: Path) -> None:
    tasks = []
    for item in instances:
        tasks.append(
            {
                "data": {
                    "text": item.get("text", ""),
                    "repo": item.get("repo"),
                    "source_type": item.get("source_type"),
                    "url": item.get("url"),
                }
            }
        )
    out_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
