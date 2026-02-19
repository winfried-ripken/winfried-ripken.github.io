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


def extract_author_name(config: dict) -> str:
    author_cfg = config.get("author") or {}
    name = author_cfg.get("name")
    if name:
        return str(name)
    return ""


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


def configure_proxy(debug: bool, use_proxy: bool = True) -> None:
    """Try free rotating proxies because GitHub Actions IPs are often blocked by Scholar."""
    if not use_proxy:
        if debug:
            print("Proxy setup disabled by flag")
        return

    pg = ProxyGenerator()
    try:
        proxy_ok = pg.FreeProxies(timeout=10, wait_time=120)
    except TypeError as exc:
        if debug:
            print(f"Proxy setup failed with compatibility error: {exc}")
        return
    except Exception as exc:  # noqa: BLE001
        if debug:
            print(f"Proxy setup failed with unexpected error: {exc}")
        return

    if proxy_ok:
        scholarly.use_proxy(pg)
        if debug:
            print("Proxy enabled via ProxyGenerator.FreeProxies")
        return

    if debug:
        print("Proxy setup failed; continuing without proxy")


def get_author_by_name_fallback(author_name: str, user_id: str, debug: bool) -> dict | None:
    if not author_name:
        return None

    if debug:
        print(f"Trying fallback author lookup by name: {author_name}")

    try:
        query = scholarly.search_author(author_name)
        for _ in range(15):
            candidate = next(query)
            if candidate.get("scholar_id") == user_id:
                if debug:
                    print("Fallback lookup found matching scholar_id")
                return candidate
    except StopIteration:
        return None
    except Exception as exc:  # noqa: BLE001
        if debug:
            print(f"Fallback author lookup failed: {exc}")
        return None

    return None


def get_author_record(user_id: str, author_name: str, debug: bool) -> dict:
    try:
        author = scholarly.search_author_id(user_id)
        return scholarly.fill(author, sections=["publications"])
    except AttributeError as exc:
        # scholarly sometimes raises this when Google returns a block/captcha page
        if debug:
            print(f"Direct author lookup failed with AttributeError: {exc}")
    except Exception as exc:  # noqa: BLE001
        if debug:
            print(f"Direct author lookup failed: {exc}")

    fallback = get_author_by_name_fallback(author_name=author_name, user_id=user_id, debug=debug)
    if fallback is None:
        raise RuntimeError("Could not resolve author record from Google Scholar")
    return scholarly.fill(fallback, sections=["publications"])


def fetch_publications(user_id: str, author_name: str, debug: bool) -> list:
    author = get_author_record(user_id=user_id, author_name=author_name, debug=debug)

    result = []
    for pub in author.get("publications", []):
        detailed_pub = pub
        try:
            detailed_pub = scholarly.fill(pub)
        except Exception as exc:  # noqa: BLE001
            if debug:
                print(f"Publication detail fetch failed for one item: {exc}")

        bib = detailed_pub.get("bib", {}) if isinstance(detailed_pub, dict) else {}
        pub_obj = detailed_pub if isinstance(detailed_pub, dict) else pub

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
            "citations": int(pub_obj.get("num_citations") or pub.get("num_citations") or 0),
            "url": scholar_url_for_pub(user_id, pub_obj),
        }
        result.append(item)

    result.sort(key=lambda x: (x["year"], x["citations"], x["title"]), reverse=True)
    return result


def fetch_with_retries(user_id: str, author_name: str, attempts: int, debug: bool) -> list:
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            if debug:
                print(f"Fetch attempt {attempt}/{attempts}")
            return fetch_publications(user_id=user_id, author_name=author_name, debug=debug)
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch publications from Google Scholar")
    parser.add_argument("--debug", action="store_true", help="Print traceback details for fetch failures")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail with non-zero exit if Scholar is unavailable and no cache exists",
    )
    parser.add_argument("--attempts", type=int, default=3, help="Number of retry attempts (default: 3)")
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        help="Disable FreeProxies setup and fetch directly",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config()
        user_id = extract_user_id(config)
        author_name = extract_author_name(config)

        configure_proxy(debug=args.debug, use_proxy=not args.no_proxy)

        items = fetch_with_retries(
            user_id=user_id,
            author_name=author_name,
            attempts=max(1, args.attempts),
            debug=args.debug,
        )
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
