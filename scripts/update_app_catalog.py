#!/usr/bin/env python3
"""Refresh reviewed App Store IDs; search prints candidates for manual review."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
import urllib.parse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))
from wda_apps import CATALOG_PATH, fetch_apple, parse_apple


def refresh(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    apps = document["apps"]
    groups = {}
    for app in apps:
        groups.setdefault(app["country"], []).append(app)
    verified = {}
    for index, (country, rows) in enumerate(sorted(groups.items())):
        if index:
            time.sleep(3.1)
        url = "https://itunes.apple.com/lookup?" + urllib.parse.urlencode(
            {"id": ",".join(str(row["trackId"]) for row in rows), "country": country, "entity": "software"})
        metadata = {row["track_id"]: row for row in parse_apple(fetch_apple(url), country, url)}
        for row in rows:
            result = metadata.get(row["trackId"])
            if not result or result["bundle_id"] != row["bundleId"]:
                raise ValueError(f"Lookup missing or changed identifier for {row['name']} ({row['trackId']}); catalog was not written. Review the publisher/storefront manually.")
            verified[row["trackId"]] = result
    for row in apps:
        result = verified[row["trackId"]]
        row.update(storeName=result["store_name"], publisher=result["publisher"], storeUrl=result["store_url"],
                   sourceUrl=result["source_url"], verifiedAt=result["verified_at"])
    document["verifiedAt"] = max(row["verifiedAt"] for row in apps)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Refreshed {len(apps)} reviewed apps in {path}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--refresh", action="store_true", help="Refresh existing reviewed track IDs; never choose the first search result.")
    mode.add_argument("--search", metavar="APP_NAME", help="Print Apple candidates with publisher evidence for manual review; does not modify the catalog.")
    parser.add_argument("--country", default="cn", help="Two-letter App Store storefront for search (default cn).")
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    args = parser.parse_args()
    try:
        if args.refresh:
            refresh(args.catalog)
        else:
            import re
            if not 1 <= len(args.search.strip()) <= 100 or not re.fullmatch(r"[A-Za-z]{2}", args.country):
                parser.error("search requires 1–100 characters and country must contain two letters")
            country = args.country.lower()
            url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(
                {"term": args.search, "country": country, "media": "software", "entity": "software", "limit": 10})
            print(json.dumps(parse_apple(fetch_apple(url), country, url), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
