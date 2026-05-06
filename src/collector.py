from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from config import GitHubConfig


@dataclass(frozen=True)
class CollectedItem:
    source_type: str
    repo: str
    text: str
    timestamp: str | None
    author: str | None
    url: str | None
    file_path: str | None = None
    line_number: int | None = None

    def as_dict(self) -> dict:
        return {
            "source_type": self.source_type,
            "repo": self.repo,
            "text": self.text,
            "timestamp": self.timestamp,
            "author": self.author,
            "url": self.url,
            "file_path": self.file_path,
            "line_number": self.line_number,
        }


def _iso(dt: str | None) -> str | None:
    if not dt:
        return None
    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except ValueError:
        return dt
    return parsed.astimezone(timezone.utc).isoformat()


def compact_text(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def _parse_link_header(link_header: str | None) -> dict[str, str]:
    if not link_header:
        return {}
    links: dict[str, str] = {}
    for part in link_header.split(","):
        section = part.strip().split(";")
        if len(section) < 2:
            continue
        url_part = section[0].strip()
        rel_part = section[1].strip()
        if not url_part.startswith("<") or not url_part.endswith(">"):
            continue
        url = url_part[1:-1]
        if "rel=\"" in rel_part:
            rel = rel_part.split("rel=\"")[-1].rstrip("\"")
            links[rel] = url
    return links


class GitHubCollector:
    def __init__(self, config: GitHubConfig) -> None:
        self._config = config

    def collect_repo(self, repo_full_name: str, max_items: int | None = None) -> list[dict]:
        max_items = max_items or self._config.max_items_per_source
        items: list[CollectedItem] = []

        owner, name = self._split_repo(repo_full_name)
        if not owner or not name:
            print(f"Invalid repo name: {repo_full_name}")
            return []

        items.extend(self._collect_commits(owner, name, repo_full_name, max_items))
        items.extend(self._collect_issues(owner, name, repo_full_name, max_items))
        items.extend(self._collect_pull_requests(owner, name, repo_full_name, max_items))
        items.extend(self._collect_commit_comments(owner, name, repo_full_name, max_items))

        if self._config.include_review_comments:
            items.extend(self._collect_review_comments(owner, name, repo_full_name, max_items))

        return [item.as_dict() for item in items if item.text]

    def _split_repo(self, repo_full_name: str) -> tuple[str, str]:
        if "/" not in repo_full_name:
            return "", ""
        owner, name = repo_full_name.split("/", 1)
        return owner, name

    def _request_json(self, path: str, params: dict[str, Any] | None = None) -> tuple[list[Any], dict[str, str]]:
        base = self._config.api_base.rstrip("/")
        url = f"{base}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {"User-Agent": "privacy-as-code", "Accept": "application/vnd.github+json"}
        if self._config.token:
            headers["Authorization"] = f"token {self._config.token}"

        request = Request(url, headers=headers)
        try:
            with urlopen(request) as response:
                payload = response.read().decode("utf-8")
                data = json.loads(payload)
                return data if isinstance(data, list) else [], dict(response.headers)
        except (HTTPError, URLError, ValueError) as exc:
            print(f"Request failed: {path} - {exc}")
            return [], {}

    def _respect_rate_limit(self, headers: dict[str, str]) -> None:
        remaining = headers.get("X-RateLimit-Remaining")
        reset = headers.get("X-RateLimit-Reset")
        if not remaining or not reset:
            return
        try:
            remaining_int = int(remaining)
            reset_ts = int(reset)
        except ValueError:
            return
        if remaining_int <= 1:
            sleep_for = max(reset_ts - int(time.time()) + 5, 0)
            time.sleep(min(sleep_for, 900))

    def _paginate(self, path: str, params: dict[str, Any], max_items: int) -> list[dict]:
        items: list[dict] = []
        next_url = None
        current_params = dict(params)

        while True:
            if next_url:
                data, headers = self._request_json(next_url, params=None)
            else:
                data, headers = self._request_json(path, current_params)
            if not data:
                break
            items.extend(data)
            if len(items) >= max_items:
                break
            self._respect_rate_limit(headers)
            links = _parse_link_header(headers.get("Link"))
            next_url = links.get("next")
            if not next_url:
                break
        return items[:max_items]

    def _collect_commits(self, owner: str, name: str, repo_name: str, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        params = {"per_page": self._config.per_page}
        commits = self._paginate(f"/repos/{owner}/{name}/commits", params, max_items)
        for commit in commits:
            commit_info = commit.get("commit", {})
            message = compact_text(commit_info.get("message"))
            if not message:
                continue
            author = commit.get("author", {}) or {}
            items.append(
                CollectedItem(
                    source_type="commit",
                    repo=repo_name,
                    text=message,
                    timestamp=_iso(commit_info.get("author", {}).get("date")),
                    author=author.get("login"),
                    url=commit.get("html_url"),
                )
            )
        return items

    def _collect_issues(self, owner: str, name: str, repo_name: str, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        params = {"state": "all", "per_page": self._config.per_page}
        issues = self._paginate(f"/repos/{owner}/{name}/issues", params, max_items)
        for issue in issues:
            if "pull_request" in issue:
                continue
            text = compact_text(f"{issue.get('title', '')}\n{issue.get('body') or ''}")
            if not text:
                continue
            user = issue.get("user") or {}
            items.append(
                CollectedItem(
                    source_type="issue",
                    repo=repo_name,
                    text=text,
                    timestamp=_iso(issue.get("created_at")),
                    author=user.get("login"),
                    url=issue.get("html_url"),
                )
            )
        return items

    def _collect_pull_requests(self, owner: str, name: str, repo_name: str, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        params = {"state": "all", "per_page": self._config.per_page}
        pulls = self._paginate(f"/repos/{owner}/{name}/pulls", params, max_items)
        for pull in pulls:
            text = compact_text(f"{pull.get('title', '')}\n{pull.get('body') or ''}")
            if not text:
                continue
            user = pull.get("user") or {}
            items.append(
                CollectedItem(
                    source_type="pull_request",
                    repo=repo_name,
                    text=text,
                    timestamp=_iso(pull.get("created_at")),
                    author=user.get("login"),
                    url=pull.get("html_url"),
                )
            )
        return items

    def _collect_commit_comments(self, owner: str, name: str, repo_name: str, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        params = {"per_page": self._config.per_page}
        comments = self._paginate(f"/repos/{owner}/{name}/comments", params, max_items)
        for comment in comments:
            text = compact_text(comment.get("body"))
            if not text:
                continue
            user = comment.get("user") or {}
            items.append(
                CollectedItem(
                    source_type="commit_comment",
                    repo=repo_name,
                    text=text,
                    timestamp=_iso(comment.get("created_at")),
                    author=user.get("login"),
                    url=comment.get("html_url"),
                    file_path=comment.get("path"),
                    line_number=comment.get("line") or comment.get("position"),
                )
            )
        return items

    def _collect_review_comments(self, owner: str, name: str, repo_name: str, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        params = {"per_page": self._config.per_page}
        comments = self._paginate(f"/repos/{owner}/{name}/pulls/comments", params, max_items)
        for comment in comments:
            text = compact_text(comment.get("body"))
            if not text:
                continue
            user = comment.get("user") or {}
            items.append(
                CollectedItem(
                    source_type="review_comment",
                    repo=repo_name,
                    text=text,
                    timestamp=_iso(comment.get("created_at")),
                    author=user.get("login"),
                    url=comment.get("html_url"),
                    file_path=comment.get("path"),
                    line_number=comment.get("line") or comment.get("position"),
                )
            )
        return items
