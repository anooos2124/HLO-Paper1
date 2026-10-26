#!/usr/bin/env python3
"""Merge the parent and reference scenario sets into one reproducible evaluation set."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def _read(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def merge(parent_csv: Path, reference_csv: Path, output_csv: Path) -> List[Dict[str, str]]:
    parent = _read(parent_csv)
    reference = _read(reference_csv)

    if len(parent) != 300:
        raise ValueError(f"Expected 300 parent scenarios; found {len(parent)}")
    if len(reference) != 200:
        raise ValueError(f"Expected 200 reference scenarios; found {len(reference)}")

    rows = parent + reference
    if len(rows) != 500:
        raise ValueError(f"Expected 500 combined scenarios; found {len(rows)}")

    scenario_ids = [r["scenario_id"] for r in rows]
    source_ids = [r["source_identifier"] for r in rows]
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("Duplicate scenario_id detected")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("The parent and reference sets must not overlap")

    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = merge(args.parent, args.reference, args.output)
    print(f"Combined scenarios: {len(rows)} -> {args.output}")


if __name__ == "__main__":
    main()
