#!/usr/bin/env python3
"""Render {% day=XX %} tags in files using a supplied origin date.

Usage:
    python render_days.py --origin YYYY-MM-DD [-r] <path>

The path can be a file or a directory. Directory processing is non-recursive by
default; use -r/--recursive to scan subdirectories.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

from jinja2 import Environment, StrictUndefined

DAY_TAG_PATTERN = re.compile(r"{%\s*day\s*=\s*([+-]?\d+)\s*%}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replace {% day=XX %} fields with dates relative to an origin date."
        )
    )
    parser.add_argument(
        "--origin",
        required=True,
        help="Origin day (day 0) in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "path",
        help="Path to a file or directory to process.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively process files when path is a directory.",
    )
    return parser.parse_args()


def parse_origin(origin_text: str) -> dt.date:
    try:
        return dt.datetime.strptime(origin_text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(
            f"Invalid --origin value '{origin_text}'. Expected YYYY-MM-DD."
        ) from exc


def iter_target_files(target: Path, recursive: bool) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        if recursive:
            return sorted(path for path in target.rglob("*") if path.is_file())
        return sorted(path for path in target.iterdir() if path.is_file())
    raise FileNotFoundError(f"Path not found: {target}")


def render_text(text: str, origin: dt.date) -> str:
    transformed = DAY_TAG_PATTERN.sub(r"{{ day(\1) }}", text)

    env = Environment(undefined=StrictUndefined, autoescape=False)

    def day(offset: int | str) -> str:
        offset_days = int(offset)
        return (origin + dt.timedelta(days=offset_days)).isoformat()

    env.globals["day"] = day
    template = env.from_string(transformed)
    return template.render()


def process_file(file_path: Path, origin: dt.date) -> tuple[bool, str]:
    try:
        original = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, f"Skipped (not UTF-8 text): {file_path}"

    if not DAY_TAG_PATTERN.search(original):
        return False, f"No day tags found: {file_path}"

    rendered = render_text(original, origin)
    if rendered == original:
        return False, f"No changes needed: {file_path}"

    file_path.write_text(rendered, encoding="utf-8")
    return True, f"Updated: {file_path}"


def main() -> int:
    args = parse_args()

    try:
        origin = parse_origin(args.origin)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    target = Path(args.path)
    try:
        files = iter_target_files(target, recursive=args.recursive)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 2

    updated = 0
    skipped = 0

    for file_path in files:
        changed, message = process_file(file_path, origin)
        print(message)
        if changed:
            updated += 1
        else:
            skipped += 1

    print(f"\nDone. Updated {updated} file(s); skipped {skipped} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
