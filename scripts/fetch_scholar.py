#!/usr/bin/env python3
import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml
from scholarly import scholarly

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


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def load_existing() -> dict:
    if not OUTPUT_PATH.exists():
        return {"generated_at": None, "items": []}
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def write_output(items: list):
    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "items": items,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    config = load_config()
    user_id = extract_user_id(config)

    try:
        items = fetch_publications(user_id)
    except Exception as exc:  # noqa: BLE001
        existing = load_existing()
        if existing.get("items"):
            print(f"Scholar fetch failed, keeping existing cache: {exc}")
            return 0
        print(f"Scholar fetch failed and no cache exists: {exc}", file=sys.stderr)
        return 1

    write_output(items)
    print(f"Wrote {len(items)} publications for user {user_id} to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
