from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
import time

from github import Github, GithubException

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


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc).isoformat()


def compact_text(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split())


class GitHubCollector:
    def __init__(self, config: GitHubConfig) -> None:
        self._config = config
        self._gh = Github(
            login_or_token=config.token,
            base_url=config.api_base,
            per_page=config.per_page,
        )

    def collect_repo(self, repo_full_name: str, max_items: int | None = None) -> list[dict]:
        max_items = max_items or self._config.max_items_per_source
        items: list[CollectedItem] = []

        try:
            repo = self._gh.get_repo(repo_full_name)
        except GithubException as exc:
            print(f"Failed to access {repo_full_name}: {exc}")
            return []

        items.extend(self._collect_commits(repo, max_items))
        items.extend(self._collect_issues(repo, max_items))
        items.extend(self._collect_pull_requests(repo, max_items))
        items.extend(self._collect_commit_comments(repo, max_items))

        if self._config.include_review_comments:
            items.extend(self._collect_review_comments(repo, max_items))

        return [item.as_dict() for item in items if item.text]

    def _respect_rate_limit(self) -> None:
        try:
            rate = self._gh.get_rate_limit().core
        except GithubException:
            return

        if rate.remaining < 10:
            sleep_for = max(rate.reset.timestamp() - time.time() + 5, 0)
            time.sleep(min(sleep_for, 900))

    def _collect_commits(self, repo, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        for commit in repo.get_commits():
            self._respect_rate_limit()
            message = compact_text(commit.commit.message)
            if message:
                items.append(
                    CollectedItem(
                        source_type="commit",
                        repo=repo.full_name,
                        text=message,
                        timestamp=_iso(commit.commit.author.date),
                        author=getattr(commit.author, "login", None),
                        url=commit.html_url,
                    )
                )
            if len(items) >= max_items:
                break
        return items

    def _collect_issues(self, repo, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        for issue in repo.get_issues(state="all"):
            self._respect_rate_limit()
            if issue.pull_request is not None:
                continue
            text = compact_text(f"{issue.title}\n{issue.body or ''}")
            if text:
                items.append(
                    CollectedItem(
                        source_type="issue",
                        repo=repo.full_name,
                        text=text,
                        timestamp=_iso(issue.created_at),
                        author=getattr(issue.user, "login", None),
                        url=issue.html_url,
                    )
                )
            if len(items) >= max_items:
                break
        return items

    def _collect_pull_requests(self, repo, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        for pr in repo.get_pulls(state="all"):
            self._respect_rate_limit()
            text = compact_text(f"{pr.title}\n{pr.body or ''}")
            if text:
                items.append(
                    CollectedItem(
                        source_type="pull_request",
                        repo=repo.full_name,
                        text=text,
                        timestamp=_iso(pr.created_at),
                        author=getattr(pr.user, "login", None),
                        url=pr.html_url,
                    )
                )
            if len(items) >= max_items:
                break
        return items

    def _collect_commit_comments(self, repo, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        for comment in repo.get_comments():
            self._respect_rate_limit()
            text = compact_text(comment.body)
            if text:
                items.append(
                    CollectedItem(
                        source_type="commit_comment",
                        repo=repo.full_name,
                        text=text,
                        timestamp=_iso(comment.created_at),
                        author=getattr(comment.user, "login", None),
                        url=comment.html_url,
                    )
                )
            if len(items) >= max_items:
                break
        return items

    def _collect_review_comments(self, repo, max_items: int) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        for pr in repo.get_pulls(state="all"):
            self._respect_rate_limit()
            for comment in pr.get_review_comments():
                text = compact_text(comment.body)
                if text:
                    items.append(
                        CollectedItem(
                            source_type="review_comment",
                            repo=repo.full_name,
                            text=text,
                            timestamp=_iso(comment.created_at),
                            author=getattr(comment.user, "login", None),
                            url=comment.html_url,
                            file_path=comment.path,
                            line_number=comment.position,
                        )
                    )
                if len(items) >= max_items:
                    break
            if len(items) >= max_items:
                break
        return items
