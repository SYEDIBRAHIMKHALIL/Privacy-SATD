from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = DATA_DIR / "results"


def _get_env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value else None


@dataclass(frozen=True)
class GitHubConfig:
    token: str | None
    api_base: str
    per_page: int
    max_items_per_source: int
    include_review_comments: bool


@dataclass(frozen=True)
class ModelConfig:
    huggingface_token: str | None
    codebert_model: str


def load_github_config() -> GitHubConfig:
    return GitHubConfig(
        token=_get_env("GITHUB_TOKEN"),
        api_base=os.getenv("GITHUB_API_BASE", "https://api.github.com"),
        per_page=int(os.getenv("GITHUB_PER_PAGE", "100")),
        max_items_per_source=int(os.getenv("GITHUB_MAX_ITEMS_PER_SOURCE", "500")),
        include_review_comments=os.getenv("GITHUB_INCLUDE_REVIEW_COMMENTS", "false").lower() == "true",
    )


def load_model_config() -> ModelConfig:
    return ModelConfig(
        huggingface_token=_get_env("HUGGINGFACE_TOKEN"),
        codebert_model=os.getenv("CODEBERT_MODEL", "microsoft/codebert-base"),
    )


def load_repo_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    repos: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        repos.append(line)
    return repos
