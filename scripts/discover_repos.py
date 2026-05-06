from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
CACHE_FILE = CACHE_DIR / "repo_discovery.json"

SECURITY_KEYWORDS = [
    "security",
    "privacy",
    "cryptography",
    "crypto",
    "authentication",
    "authorization",
    "auth",
    "oauth",
    "oidc",
    "jwt",
    "tls",
    "ssl",
    "x509",
    "vulnerability",
    "vuln",
    "pentest",
    "fuzz",
    "fuzzer",
    "static analysis",
    "sast",
    "dast",
    "malware",
    "sandbox",
    "secret",
    "secrets",
    "threat",
    "intrusion",
    "differential privacy",
]

SEARCH_TERMS = [
    "security",
    "privacy",
    "cryptography",
    "authentication",
    "authorization",
    "vulnerability",
    "fuzzing",
    "sast",
]

GERMANY_LOCATIONS = [
    "Germany",
    "Deutschland",
    "Berlin",
    "Munich",
    "Hamburg",
    "Frankfurt",
    "Cologne",
    "Koeln",
    "Stuttgart",
    "Dresden",
    "Leipzig",
    "Karlsruhe",
    "Heidelberg",
    "Bonn",
    "Duesseldorf",
    "Dusseldorf",
    "Nuremberg",
    "Nuernberg",
    "Hannover",
    "Bremen",
    "Freiburg",
    "Aachen",
]

EUROPE_LOCATIONS = [
    "Austria",
    "Switzerland",
    "Netherlands",
    "Belgium",
    "Denmark",
    "Sweden",
    "Norway",
    "Finland",
    "France",
    "Spain",
    "Italy",
    "Poland",
    "Portugal",
    "Greece",
    "Romania",
    "Bulgaria",
    "Hungary",
    "Slovakia",
    "Slovenia",
    "Croatia",
    "Estonia",
    "Latvia",
    "Lithuania",
    "Iceland",
    "Luxembourg",
    "Czechia",
    "United Kingdom",
    "Ireland",
]

LANG_LIMITS = {
    "Python": 16,
    "C++": 8,
    "C#": 7,
    "Java": 7,
    "Go": 6,
    "Rust": 5,
    "JavaScript": 6,
    "TypeScript": 6,
    "C": 4,
}

OTHER_LANG_LIMIT = 5


def load_env() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def api_get(path: str, token: str | None, params: dict | None = None, accept: str | None = None) -> dict:
    base = os.getenv("GITHUB_API_BASE", "https://api.github.com").rstrip("/")
    url = f"{base}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    headers = {"User-Agent": "privacy-as-code"}
    if token:
        headers["Authorization"] = f"token {token}"
    if accept:
        headers["Accept"] = accept
    request = Request(url, headers=headers)
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def safe_get(path: str, token: str | None, params: dict | None = None, accept: str | None = None) -> dict:
    try:
        return api_get(path, token, params=params, accept=accept)
    except (HTTPError, URLError, ValueError) as exc:
        print(f"Request failed: {path} - {exc}")
        return {}


def search_users(locations: list[str], user_type: str, token: str | None, per_page: int) -> list[dict]:
    items: list[dict] = []
    for location in locations:
        query = f'location:"{location}" type:{user_type}'
        data = safe_get(
            "/search/users",
            token,
            params={"q": query, "per_page": per_page},
            accept="application/vnd.github+json",
        )
        items.extend(data.get("items", []))
    return items


def list_repos(owner: str, owner_type: str, token: str | None, per_page: int) -> list[dict]:
    if owner_type == "org":
        path = f"/orgs/{owner}/repos"
    else:
        path = f"/users/{owner}/repos"
    return safe_get(
        path,
        token,
        params={"per_page": per_page, "sort": "stars", "direction": "desc"},
        accept="application/vnd.github+json,application/vnd.github.mercy-preview+json",
    ) or []


def matches_security(repo: dict) -> bool:
    text_parts = [repo.get("name") or "", repo.get("description") or ""]
    topics = repo.get("topics") or []
    text_parts.extend(topics)
    text = " ".join(text_parts).lower()
    return any(keyword in text for keyword in SECURITY_KEYWORDS)


def build_candidates(owners: list[tuple[str, str]], token: str | None, min_stars: int, per_page: int) -> list[dict]:
    candidates: list[dict] = []
    seen: set[str] = set()
    for owner, owner_type in owners:
        repos = list_repos(owner, owner_type, token, per_page)
        for repo in repos:
            full_name = repo.get("full_name")
            if not full_name or full_name in seen:
                continue
            if repo.get("fork") or repo.get("archived"):
                continue
            if int(repo.get("stargazers_count") or 0) < min_stars:
                continue
            if not matches_security(repo):
                continue
            candidates.append(
                {
                    "full_name": full_name,
                    "stars": int(repo.get("stargazers_count") or 0),
                    "language": repo.get("language") or "Other",
                }
            )
            seen.add(full_name)
    candidates.sort(key=lambda item: item["stars"], reverse=True)
    return candidates


def location_matches(location: str | None, locations: list[str]) -> bool:
    if not location:
        return False
    lowered = location.lower()
    return any(term.lower() in lowered for term in locations)


def search_repositories(terms: list[str], token: str | None, min_stars: int, per_page: int) -> list[dict]:
    repos: list[dict] = []
    seen: set[str] = set()
    for term in terms:
        query = f"{term} in:description,readme stars:>={min_stars}"
        data = safe_get(
            "/search/repositories",
            token,
            params={"q": query, "per_page": per_page, "sort": "stars", "order": "desc"},
            accept="application/vnd.github+json,application/vnd.github.mercy-preview+json",
        )
        for repo in data.get("items", []):
            full_name = repo.get("full_name")
            if not full_name or full_name in seen:
                continue
            if repo.get("fork") or repo.get("archived"):
                continue
            if not matches_security(repo):
                continue
            repos.append(repo)
            seen.add(full_name)
    return repos


def get_owner_location(owner_login: str, token: str | None, owner_cache: dict) -> str:
    if owner_login in owner_cache:
        return owner_cache[owner_login]
    data = safe_get(f"/users/{owner_login}", token, accept="application/vnd.github+json")
    location = data.get("location") or ""
    owner_cache[owner_login] = location
    return location


def filter_repo_candidates_by_location(
    repos: list[dict],
    locations: list[str],
    token: str | None,
    owner_cache: dict,
) -> list[dict]:
    candidates: list[dict] = []
    seen: set[str] = set()
    for repo in repos:
        full_name = repo.get("full_name")
        if not full_name or full_name in seen:
            continue
        owner = repo.get("owner") or {}
        login = owner.get("login")
        if not login:
            continue
        location = get_owner_location(login, token, owner_cache)
        if not location_matches(location, locations):
            continue
        candidates.append(
            {
                "full_name": full_name,
                "stars": int(repo.get("stargazers_count") or 0),
                "language": repo.get("language") or "Other",
            }
        )
        seen.add(full_name)
    candidates.sort(key=lambda item: item["stars"], reverse=True)
    return candidates


def merge_candidates(primary: list[dict], extra: list[dict]) -> list[dict]:
    merged = {item["full_name"]: item for item in primary}
    for item in extra:
        if item["full_name"] not in merged:
            merged[item["full_name"]] = item
    merged_list = list(merged.values())
    merged_list.sort(key=lambda item: item["stars"], reverse=True)
    return merged_list


def add_repo(
    repo: dict,
    selected: list[dict],
    selected_set: set[str],
    lang_counts: dict[str, int],
    other_count: int,
    strict: bool,
) -> int:
    if repo["full_name"] in selected_set:
        return other_count
    language = repo.get("language") or "Other"
    if strict:
        if language in LANG_LIMITS:
            if lang_counts[language] >= LANG_LIMITS[language]:
                return other_count
        else:
            if other_count >= OTHER_LANG_LIMIT:
                return other_count
    if language in LANG_LIMITS:
        lang_counts[language] += 1
    else:
        other_count += 1
    selected.append(repo)
    selected_set.add(repo["full_name"])
    return other_count


def select_repos(candidates: list[dict], target_count: int, strict: bool) -> list[dict]:
    selected: list[dict] = []
    selected_set: set[str] = set()
    lang_counts = {lang: 0 for lang in LANG_LIMITS}
    other_count = 0
    for repo in candidates:
        if len(selected) >= target_count:
            break
        other_count = add_repo(repo, selected, selected_set, lang_counts, other_count, strict=strict)
    return selected


def merge_with_limits(
    selected: list[dict],
    candidates: list[dict],
    target_count: int,
    strict: bool,
) -> list[dict]:
    selected_set = {item["full_name"] for item in selected}
    lang_counts = {lang: 0 for lang in LANG_LIMITS}
    other_count = 0
    for item in selected:
        language = item.get("language") or "Other"
        if language in LANG_LIMITS:
            lang_counts[language] += 1
        else:
            other_count += 1

    for repo in candidates:
        if len(selected) >= target_count:
            break
        other_count = add_repo(repo, selected, selected_set, lang_counts, other_count, strict=strict)
    return selected


def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except ValueError:
        return {}


def save_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def build_owner_list(locations: list[str], token: str | None, owner_limit: int) -> list[tuple[str, str]]:
    owners: list[tuple[str, str]] = []
    seen: set[str] = set()
    for user_type in ["org", "user"]:
        items = search_users(locations, user_type, token, per_page=100)
        for item in items:
            login = item.get("login")
            if not login or login in seen:
                continue
            owners.append((login, user_type))
            seen.add(login)
            if len(owners) >= owner_limit:
                return owners
    return owners


def write_seed_file(selected: list[dict], out_path: Path) -> None:
    lines = [item["full_name"] for item in selected]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(selected: list[dict]) -> None:
    lang_counts: dict[str, int] = {}
    for item in selected:
        lang = item.get("language") or "Other"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    print(f"Selected repos: {len(selected)}")
    for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover security repos with Germany preference")
    parser.add_argument("--out", default=str(PROJECT_ROOT / "data" / "seed_repos.txt"))
    parser.add_argument("--target-count", type=int, default=50)
    parser.add_argument("--min-stars", type=int, default=100)
    parser.add_argument("--owner-limit", type=int, default=120)
    parser.add_argument("--per-page", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_env()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("GITHUB_TOKEN not set. Add it to .env or your environment.")
        return

    cache = load_cache()
    owner_locations = cache.get("owner_locations", {})

    germany_owners = cache.get("germany_owners")
    if not germany_owners:
        germany_owners = build_owner_list(GERMANY_LOCATIONS, token, owner_limit=args.owner_limit)
        cache["germany_owners"] = germany_owners
        save_cache(cache)

    germany_candidates = build_candidates(germany_owners, token, args.min_stars, args.per_page)

    repo_search_candidates = search_repositories(SEARCH_TERMS, token, args.min_stars, args.per_page)
    if repo_search_candidates:
        germany_from_search = filter_repo_candidates_by_location(
            repo_search_candidates,
            GERMANY_LOCATIONS,
            token,
            owner_locations,
        )
        germany_candidates = merge_candidates(germany_candidates, germany_from_search)

    selected = select_repos(germany_candidates, args.target_count, strict=True)
    if len(selected) < min(args.target_count, len(germany_candidates)):
        selected = merge_with_limits(selected, germany_candidates, args.target_count, strict=False)

    if len(selected) < args.target_count:
        europe_owners = cache.get("europe_owners")
        if not europe_owners:
            europe_owners = build_owner_list(EUROPE_LOCATIONS, token, owner_limit=args.owner_limit)
            cache["europe_owners"] = europe_owners
            save_cache(cache)
        europe_candidates = build_candidates(europe_owners, token, args.min_stars, args.per_page)
        if repo_search_candidates:
            europe_from_search = filter_repo_candidates_by_location(
                repo_search_candidates,
                EUROPE_LOCATIONS,
                token,
                owner_locations,
            )
            europe_candidates = merge_candidates(europe_candidates, europe_from_search)
        selected = merge_with_limits(selected, europe_candidates, args.target_count, strict=True)

    cache["owner_locations"] = owner_locations
    save_cache(cache)

    out_path = Path(args.out)
    write_seed_file(selected[: args.target_count], out_path)
    print_summary(selected[: args.target_count])


if __name__ == "__main__":
    main()
