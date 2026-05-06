from __future__ import annotations

from pathlib import Path
import json
import re


def load_keywords(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [kw.strip().lower() for kw in data.get("keywords", []) if kw.strip()]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def filter_instances(instances: list[dict], keywords: list[str]) -> list[dict]:
    normalized_keywords = [normalize_text(k) for k in keywords]
    result: list[dict] = []
    for item in instances:
        text = normalize_text(item.get("text", ""))
        if not text:
            continue
        if any(kw in text for kw in normalized_keywords):
            result.append(item)
    return result
