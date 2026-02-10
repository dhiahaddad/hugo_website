#!/usr/bin/env python3

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path


def _norm_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").strip().lower())


def _pick(row: dict, *candidates: str) -> str:
    for key in row.keys():
        normalized = _norm_header(key)
        for cand in candidates:
            if normalized == cand:
                return (row.get(key) or "").strip()
    return ""


def _display_name(name: str, email: str) -> str:
    name = (name or "").strip()
    if name:
        # Prefer first name + last initial (privacy-friendly)
        parts = [p for p in re.split(r"\s+", name) if p]
        if len(parts) == 1:
            return parts[0]
        first = parts[0]
        last_initial = parts[-1][0] + "." if parts[-1] else ""
        return f"{first} {last_initial}".strip()

    email = (email or "").strip()
    if "@" in email:
        local = email.split("@", 1)[0]
        local = re.sub(r"[^a-zA-Z0-9]+", " ", local).strip()
        local = re.sub(r"\s+", " ", local)
        return local or "Supporter"

    return "Supporter"


def _format_joined(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""

    # Try a few common formats; fall back to date prefix if present.
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass

    m = re.match(r"^(\d{4}-\d{2}-\d{2})", value)
    return m.group(1) if m else ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import supporters from a CSV export and write Hugo data file (JSON)."
    )
    parser.add_argument("csv", type=Path, help="Path to CSV export")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/supporters.json"),
        help="Output JSON path (default: data/supporters.json)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit of rows to include (0 = no limit)",
    )
    args = parser.parse_args()

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    supporters = []
    seen_emails = set()

    with args.csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = _pick(row, "email", "emailaddress", "supporteremail")
            name = _pick(row, "name", "fullname", "supportername")
            created = _pick(row, "createdat", "timestamp", "date", "submittedat")

            normalized_email = email.strip().lower()
            if normalized_email:
                if normalized_email in seen_emails:
                    continue
                seen_emails.add(normalized_email)

            display = _display_name(name, email)
            joined = _format_joined(created)

            item = {"name": display}
            if joined:
                item["joined"] = joined

            supporters.append(item)

            if args.limit and len(supporters) >= args.limit:
                break

    out_path.write_text(json.dumps(supporters, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(supporters)} supporters to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
