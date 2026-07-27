#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "jsonschema>=4.18,<5",
# ]
# ///
"""Validate a monomers JSON document against its JSON Schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(json_path: Path, schema_path: Path) -> int:
    records = load_json(json_path)
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(records),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        for error in errors:
            location = "$"
            for part in error.absolute_path:
                location += f"[{part}]" if isinstance(part, int) else f".{part}"
            print(f"{location}: {error.message}", file=sys.stderr)
        return 1
    print(f"validated {json_path} against {schema_path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("schema_file", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        sys.exit(validate(args.json_file, args.schema_file))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"schema validation failed: {error}") from error
