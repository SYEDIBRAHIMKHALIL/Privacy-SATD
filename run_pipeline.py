from __future__ import annotations

import argparse
from pathlib import Path

from config import DATA_DIR, RESULTS_DIR, load_github_config, load_repo_list
from src.collector import GitHubCollector
from src.keyword_filter import filter_instances, load_keywords
from src.validator import write_label_studio_tasks
from src.export import export_csv, export_jsonl, export_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Privacy-SATD Miner")
    parser.add_argument("--repos", required=True, help="Path to repo list file")
    parser.add_argument("--max-items", type=int, default=None, help="Max items per source per repo")
    parser.add_argument("--out-jsonl", default=str(RESULTS_DIR / "raw.jsonl"))
    parser.add_argument("--filtered-jsonl", default=str(RESULTS_DIR / "filtered.jsonl"))
    parser.add_argument("--csv-out", default=str(RESULTS_DIR / "results.csv"))
    parser.add_argument("--summary-out", default=str(RESULTS_DIR / "summary.json"))
    parser.add_argument("--label-studio-out", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    repo_list = load_repo_list(Path(args.repos))
    if not repo_list:
        print("No repositories found. Add repos to the file and try again.")
        return

    collector = GitHubCollector(load_github_config())

    all_items: list[dict] = []
    for repo in repo_list:
        print(f"Collecting from {repo}...")
        all_items.extend(collector.collect_repo(repo, max_items=args.max_items))

    export_jsonl(all_items, Path(args.out_jsonl))

    keywords = load_keywords(DATA_DIR / "privacy_keywords.json")
    filtered = filter_instances(all_items, keywords)
    export_jsonl(filtered, Path(args.filtered_jsonl))

    if args.label_studio_out:
        write_label_studio_tasks(filtered, Path(args.label_studio_out))

    export_csv(filtered, Path(args.csv_out))
    export_summary(filtered, Path(args.summary_out))


if __name__ == "__main__":
    main()
