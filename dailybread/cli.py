"""Command-line interface for DailyBreadPlusNine."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import Iterable

from .generator import generate_entry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Daily Bread insight inspired by NASA science and reflective practice.",
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="Date to generate for (defaults to today).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    return parser


def parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise SystemExit(f"Invalid date '{value}'. Use YYYY-MM-DD.") from exc


def render(entry, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(entry.to_dict(), indent=2, ensure_ascii=False)
    return entry.to_text()


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    entry = generate_entry(parse_date(args.date))
    print(render(entry, args.format))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
