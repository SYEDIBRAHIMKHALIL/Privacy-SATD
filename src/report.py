from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from src.keyword_filter import normalize_text


@dataclass
class ReportData:
    total_instances: int
    unique_repos: int
    source_counts: list[tuple[str, int]]
    top_repos: list[tuple[str, int]]
    top_keywords: list[tuple[str, int]]
    gdpr_counts: list[tuple[str, int]]


def count_top(items: list[dict], key: str, top_n: int) -> list[tuple[str, int]]:
    counter = Counter()
    for item in items:
        value = item.get(key)
        if value:
            counter[value] += 1
    return counter.most_common(top_n)


def count_keywords(items: list[dict], keywords: list[str], top_n: int) -> list[tuple[str, int]]:
    normalized_keywords = [normalize_text(keyword) for keyword in keywords if keyword]
    counter = Counter()
    for item in items:
        text = normalize_text(item.get("text", ""))
        if not text:
            continue
        for keyword in normalized_keywords:
            if keyword and keyword in text:
                counter[keyword] += 1
    return counter.most_common(top_n)


def count_gdpr(items: list[dict], top_n: int) -> list[tuple[str, int]]:
    counter = Counter()
    for item in items:
        for article in item.get("gdpr_articles", []) or []:
            counter[article] += 1
    return counter.most_common(top_n)


def build_report_data(items: list[dict], keywords: list[str], top_n: int) -> ReportData:
    source_counts = count_top(items, "source_type", top_n)
    top_repos = count_top(items, "repo", top_n)
    top_keywords = count_keywords(items, keywords, top_n)
    gdpr_counts = count_gdpr(items, top_n)
    unique_repos = len({item.get("repo") for item in items if item.get("repo")})

    return ReportData(
        total_instances=len(items),
        unique_repos=unique_repos,
        source_counts=source_counts,
        top_repos=top_repos,
        top_keywords=top_keywords,
        gdpr_counts=gdpr_counts,
    )


def write_report(report: ReportData, out_path: Path, generated_at: datetime) -> None:
    lines = [
        "# Privacy-SATD Miner Report",
        "",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        f"- Total instances: {report.total_instances}",
        f"- Unique repos: {report.unique_repos}",
        "",
        "## Top repositories",
    ]
    for repo, count in report.top_repos:
        lines.append(f"- {repo}: {count}")

    lines.extend(["", "## Top keywords"]) 
    for keyword, count in report.top_keywords:
        lines.append(f"- {keyword}: {count}")

    lines.extend(["", "## Top GDPR articles"]) 
    for article, count in report.gdpr_counts:
        lines.append(f"- {article}: {count}")

    lines.extend(["", "## Source types"]) 
    for source, count in report.source_counts:
        lines.append(f"- {source}: {count}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_examples(items: list[dict], out_path: Path, max_examples: int) -> None:
    trimmed = items[:max_examples]
    out_path.write_text(json.dumps(trimmed, indent=2), encoding="utf-8")


def generate_figures(report: ReportData, out_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. Install it to generate figures.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    def plot_bar(title: str, items: list[tuple[str, int]], filename: str) -> None:
        if not items:
            return
        labels = [item[0] for item in items]
        values = [item[1] for item in items]

        plt.figure(figsize=(10, 6))
        plt.barh(labels, values)
        plt.title(title)
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(out_dir / filename, dpi=160)
        plt.close()

    plot_bar("Top repositories", report.top_repos, "top_repos.png")
    plot_bar("Top keywords", report.top_keywords, "top_keywords.png")
    plot_bar("Source types", report.source_counts, "source_types.png")
    plot_bar("GDPR article mapping", report.gdpr_counts, "gdpr_articles.png")


def generate_report(
    items: list[dict],
    keywords: list[str],
    report_out: Path | None,
    figures_dir: Path | None,
    examples_out: Path | None,
    report_json_out: Path | None,
    top_n: int = 10,
    max_examples: int = 25,
) -> None:
    report_data = build_report_data(items, keywords, top_n)
    generated_at = datetime.now()

    if report_out:
        write_report(report_data, report_out, generated_at)

    if report_json_out:
        write_report_json(report_data, report_json_out, generated_at)

    if figures_dir:
        generate_figures(report_data, figures_dir)

    if examples_out:
        write_examples(items, examples_out, max_examples)


def _format_counts(items: list[tuple[str, int]]) -> list[dict]:
    return [{"label": label, "count": count} for label, count in items]


def write_report_json(report: ReportData, out_path: Path, generated_at: datetime) -> None:
    payload = {
        "generated_at": generated_at.isoformat(),
        "total_instances": report.total_instances,
        "unique_repos": report.unique_repos,
        "top_repos": _format_counts(report.top_repos),
        "top_keywords": _format_counts(report.top_keywords),
        "source_counts": _format_counts(report.source_counts),
        "gdpr_counts": _format_counts(report.gdpr_counts),
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
