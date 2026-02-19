#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
import sys
import time
import traceback
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml
from scholarly import ProxyGenerator, scholarly

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "_config.yml"
OUTPUT_PATH = ROOT / "_data" / "publications.json"


def extract_user_id(config: dict) -> str:
    scholar_cfg = config.get("scholar") or {}
    user_id = scholar_cfg.get("user_id")
    if user_id:
        return str(user_id)

    author_cfg = config.get("author") or {}
    scholar_url = author_cfg.get("scholar_url") or author_cfg.get("googlescholar")
    if scholar_url:
        parsed = urlparse(str(scholar_url))
        candidate = parse_qs(parsed.query).get("user")
        if candidate and candidate[0]:
            return candidate[0]

    raise ValueError(
        "Missing Scholar user id. Set `scholar.user_id` in _config.yml or provide author.scholar_url with ?user=..."
    )


def normalize_year(raw_year):
    if raw_year is None:
        return 0
    match = re.search(r"\d{4}", str(raw_year))
    if not match:
        return 0
    return int(match.group(0))


def scholar_url_for_pub(user_id: str, pub: dict) -> str:
    for key in ("pub_url", "eprint_url", "url_scholarbib"):
        value = pub.get(key)
        if value:
            return str(value)

    pub_id = pub.get("author_pub_id")
    if pub_id:
        return (
            "https://scholar.google.com/citations?"
            f"view_op=view_citation&hl=en&user={user_id}&citation_for_view={pub_id}"
        )
    return ""


def configure_proxy(debug: bool) -> None:
    """Try free rotating proxies because GitHub Actions IPs are often blocked by Scholar."""
    pg = ProxyGenerator()
    proxy_ok = pg.FreeProxies(timeout=10, wait_time=120)
    if proxy_ok:
        scholarly.use_proxy(pg)
        if debug:
            print("Proxy enabled via ProxyGenerator.FreeProxies")
    elif debug:
        print("Proxy setup failed; continuing without proxy")


def fetch_publications(user_id: str) -> list:
    author = scholarly.search_author_id(user_id)
    author = scholarly.fill(author, sections=["publications"])

    result = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        year = normalize_year(bib.get("pub_year") or bib.get("year"))
        title = (bib.get("title") or "").strip()
        if not title:
            continue

        venue = bib.get("journal") or bib.get("booktitle") or bib.get("publisher") or ""

        item = {
            "title": title,
            "authors": (bib.get("author") or "").strip(),
            "venue": str(venue).strip(),
            "year": year,
            "citations": int(pub.get("num_citations") or 0),
            "url": scholar_url_for_pub(user_id, pub),
        }
        result.append(item)

    result.sort(key=lambda x: (x["year"], x["citations"], x["title"]), reverse=True)
    return result


def fetch_with_retries(user_id: str, attempts: int, debug: bool) -> list:
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            if debug:
                print(f"Fetch attempt {attempt}/{attempts}")
            return fetch_publications(user_id)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if debug:
                print(f"Attempt {attempt} failed: {exc}")
                traceback.print_exc()
            if attempt < attempts:
                time.sleep(min(8 * attempt, 20))

    if last_error is not None:
        raise last_error
    raise RuntimeError("Unknown fetch failure")


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def load_existing() -> dict:
    if not OUTPUT_PATH.exists():
        return {"generated_at": None, "items": []}
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def write_output(items: list, note: str | None = None):
    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "note": note,
        "items": items,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch publications from Google Scholar")
    parser.add_argument("--debug", action="store_true", help="Print traceback details for fetch failures")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail with non-zero exit if Scholar is unavailable and no cache exists",
    )
    parser.add_argument("--attempts", type=int, default=3, help="Number of retry attempts (default: 3)")
    args = parser.parse_args()

    config = load_config()
    user_id = extract_user_id(config)

    configure_proxy(debug=args.debug)

    try:
        items = fetch_with_retries(user_id=user_id, attempts=max(1, args.attempts), debug=args.debug)
    except Exception as exc:  # noqa: BLE001
        existing = load_existing()
        if existing.get("items"):
            print(f"Scholar fetch failed, keeping existing cache: {exc}")
            return 0

        message = f"Scholar fetch failed on cold start: {exc}"
        write_output(items=[], note=message)
        print(message)
        if args.strict:
            return 1
        return 0

    write_output(items)
    print(f"Wrote {len(items)} publications for user {user_id} to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
