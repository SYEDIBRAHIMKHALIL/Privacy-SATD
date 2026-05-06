from __future__ import annotations

from pathlib import Path
import json
from typing import Iterable


def load_gdpr_articles(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("articles", [])


def _score_by_keywords(text: str, keywords: Iterable[str]) -> int:
    score = 0
    lowered = text.lower()
    for kw in keywords:
        if kw.lower() in lowered:
            score += 1
    return score


def map_to_gdpr_articles(text: str, articles: list[dict], top_k: int = 2) -> list[str]:
    scored = []
    for article in articles:
        score = _score_by_keywords(text, article.get("keywords", []))
        scored.append((score, article.get("id")))
    scored.sort(reverse=True)
    return [article_id for score, article_id in scored if score > 0][:top_k]
