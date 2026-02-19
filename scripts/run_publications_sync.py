#!/usr/bin/env python3
"""Local/CI entrypoint for publication sync using fetch_scholar's main path."""

import argparse

import fetch_scholar


def main() -> int:
    parser = argparse.ArgumentParser(description="Run publication sync with shared defaults")
    parser.add_argument("--strict", action="store_true", help="Fail if first fetch cannot produce data")
    parser.add_argument("--attempts", type=int, default=3, help="Retry attempts (default: 3)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--no-proxy", action="store_true", help="Disable FreeProxies setup")
    args = parser.parse_args()

    argv = ["--attempts", str(max(1, args.attempts))]
    if args.debug:
        argv.append("--debug")
    if args.strict:
        argv.append("--strict")
    if args.no_proxy:
        argv.append("--no-proxy")

    return fetch_scholar.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
