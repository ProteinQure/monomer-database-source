#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rdkit==2026.3.4",
# ]
# ///
"""Convert the source-of-truth JSON array into a deterministic output format."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

try:
    from rdkit import Chem
    from rdkit.Chem import rdDepictor
except ImportError:  # Keep CSV/TSV conversion usable without the SDF dependency.
    Chem = None
    rdDepictor = None

OUTPUT_DELIMITERS = {
    "csv": ",",
    "tsv": "\t",
}
OUTPUT_TYPES = (*OUTPUT_DELIMITERS, "sdf")


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as source_file:
        data = json.load(source_file)

    if not isinstance(data, list) or not data:
        raise ValueError("the JSON document must be a non-empty array of objects")
    if not all(isinstance(record, dict) for record in data):
        raise ValueError("every item in the JSON array must be an object")

    fieldnames = list(data[0])
    if not fieldnames:
        raise ValueError("records must contain at least one field")

    expected_fields = set(fieldnames)
    for index, record in enumerate(data, start=1):
        if set(record) != expected_fields:
            missing = sorted(expected_fields - set(record))
            extra = sorted(set(record) - expected_fields)
            raise ValueError(
                f"record {index} has inconsistent fields; missing={missing}, extra={extra}"
            )

    return data


def delimited_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value


def sdf_property_value(value: Any) -> str:
    """Return the stable string representation stored in an SD property."""
    return str(delimited_value(value))


def delimiter_for_output_type(output_type: str) -> str:
    try:
        return OUTPUT_DELIMITERS[output_type]
    except KeyError as error:
        supported = ", ".join(OUTPUT_TYPES)
        raise ValueError(
            f"unsupported output type {output_type!r}; expected one of: {supported}"
        ) from error


def write_delimited(
    records: list[dict[str, Any]], output_path: Path, delimiter: str
) -> None:
    fieldnames = list(records[0])

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
            delimiter=delimiter,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {key: delimited_value(value) for key, value in record.items()}
            )


def write_sdf(records: list[dict[str, Any]], output_path: Path) -> None:
    """Write structures and all source fields to an SD file using RDKit."""
    if Chem is None or rdDepictor is None:
        raise RuntimeError(
            "RDKit is required for SDF output; run this script with uv"
        )

    molecules = []
    for index, record in enumerate(records, start=1):
        symbol = record.get("PQ_SYMBOL")
        smiles = record.get("SMILES")
        record_name = symbol or f"record {index}"
        if not isinstance(smiles, str) or not smiles:
            raise ValueError(f"{record_name} has no non-empty SMILES value")

        molecule = Chem.MolFromSmiles(smiles)
        if molecule is None:
            raise ValueError(f"{record_name} has an invalid SMILES value")

        rdDepictor.Compute2DCoords(molecule, canonOrient=True)
        title = str(symbol or "")
        molecule.SetProp("_Name", title)
        molecule.SetProp("rName", title)
        for field, value in record.items():
            molecule.SetProp(field, sdf_property_value(value))
        molecules.append(molecule)

    with Chem.SDWriter(str(output_path)) as writer:
        for molecule in molecules:
            writer.write(molecule)


def convert(input_path: Path, output_path: Path, output_type: str) -> None:
    records = load_records(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_type == "sdf":
        write_sdf(records, output_path)
        return
    write_delimited(
        records,
        output_path,
        delimiter_for_output_type(output_type),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-type",
        required=True,
        choices=OUTPUT_TYPES,
        help="output data type",
    )
    parser.add_argument("input", type=Path, help="source JSON file")
    parser.add_argument("output", type=Path, help="destination file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        convert(args.input, args.output, args.output_type)
    except (OSError, RuntimeError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"conversion failed: {error}") from error
