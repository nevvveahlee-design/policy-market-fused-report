# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DIV_OPEN_RE = re.compile(r"<div\b", re.IGNORECASE)
DIV_CLOSE_RE = re.compile(r"</div>", re.IGNORECASE)
SLIDE_RE = re.compile(r"<div[^>]*class=['\"][^'\"]*\bslide\b[^'\"]*['\"][^>]*>", re.IGNORECASE)
HEADLINE_RE = re.compile(r"<h1\b", re.IGNORECASE)
KEY_NUMBER_RE = re.compile(r"class=['\"][^'\"]*\bn\b[^'\"]*['\"]", re.IGNORECASE)
KEY_LABEL_RE = re.compile(r"class=['\"][^'\"]*\bl\b[^'\"]*['\"]", re.IGNORECASE)


def validate_html(path: Path) -> list[str]:
    errors = []
    html_path = Path(path)
    try:
        content = html_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["file is not valid UTF-8"]

    if '<meta charset="utf-8">' not in content.lower():
        errors.append("missing UTF-8 charset declaration")

    div_diff = len(DIV_OPEN_RE.findall(content)) - len(DIV_CLOSE_RE.findall(content))
    if div_diff != 0:
        errors.append(f"unbalanced <div> tags: diff={div_diff}")

    slide_count = len(SLIDE_RE.findall(content))
    headline_count = len(HEADLINE_RE.findall(content))
    if slide_count and headline_count < slide_count:
        errors.append("one or more slides are missing headline <h1> elements")

    key_numbers = len(KEY_NUMBER_RE.findall(content))
    key_labels = len(KEY_LABEL_RE.findall(content))
    if key_numbers != key_labels:
        errors.append("key-number labels do not match key-number values")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a rendered deck HTML file.")
    parser.add_argument("path", help="Path to the HTML deck file.")
    args = parser.parse_args()

    errors = validate_html(Path(args.path))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
