#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rdkit==2026.3.4",
# ]
# ///
"""Verify that an output is the exact deterministic JSON conversion."""

from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path

from convert import (
    Chem,
    OUTPUT_TYPES,
    convert,
    delimiter_for_output_type,
    load_records,
    sdf_property_value,
)

OUTPUT_TYPE_BY_SUFFIX = {f".{output_type}": output_type for output_type in OUTPUT_TYPES}


def output_type_for_path(path: Path) -> str:
    try:
        return OUTPUT_TYPE_BY_SUFFIX[path.suffix.lower()]
    except KeyError as error:
        supported = ", ".join(sorted(OUTPUT_TYPE_BY_SUFFIX))
        raise ValueError(
            f"unsupported output format {path.suffix or '<none>'}; expected {supported}"
        ) from error


def verify_sdf(records: list[dict], output_path: Path) -> None:
    if Chem is None:
        raise RuntimeError(
            "RDKit is required for SDF verification; run this script with uv"
        )

    molecules = list(Chem.SDMolSupplier(str(output_path), removeHs=False))
    if len(molecules) != len(records):
        raise ValueError(
            f"row count mismatch: JSON has {len(records)} records, "
            f"SDF has {len(molecules)}"
        )

    for index, (record, molecule) in enumerate(zip(records, molecules), start=1):
        if molecule is None:
            raise ValueError(f"SDF molecule {index} could not be parsed")
        symbol = str(record.get("PQ_SYMBOL") or "")
        if molecule.GetProp("_Name") != symbol:
            raise ValueError(f"SDF molecule {index} has an unexpected title")
        if not molecule.HasProp("rName") or molecule.GetProp("rName") != symbol:
            raise ValueError(f"SDF molecule {index} has an unexpected rName")

        for field, value in record.items():
            expected = sdf_property_value(value)
            if not molecule.HasProp(field) or molecule.GetProp(field) != expected:
                raise ValueError(
                    f"SDF molecule {index} has an unexpected {field} property"
                )

        source_molecule = Chem.MolFromSmiles(record["SMILES"])
        if source_molecule is None:
            raise ValueError(f"JSON record {index} has an invalid SMILES value")
        expected_smiles = Chem.MolToSmiles(source_molecule, isomericSmiles=True)
        actual_smiles = Chem.MolToSmiles(molecule, isomericSmiles=True)
        if actual_smiles != expected_smiles:
            raise ValueError(f"SDF molecule {index} does not match its JSON SMILES")


def verify(json_path: Path, output_path: Path) -> None:
    records = load_records(json_path)
    output_type = output_type_for_path(output_path)
    format_name = output_type.upper()

    with tempfile.TemporaryDirectory() as temporary_directory:
        expected_output = Path(temporary_directory) / "expected-output"
        convert(json_path, expected_output, output_type)
        if output_path.read_bytes() != expected_output.read_bytes():
            raise ValueError(
                f"{format_name} does not exactly match the deterministic JSON conversion"
            )

    if output_type == "sdf":
        verify_sdf(records, output_path)
        return

    delimiter = delimiter_for_output_type(output_type)
    with output_path.open(encoding="utf-8", newline="") as output_file:
        output_rows = list(csv.DictReader(output_file, delimiter=delimiter))
    if len(output_rows) != len(records):
        raise ValueError(
            f"row count mismatch: JSON has {len(records)} records, "
            f"{format_name} has {len(output_rows)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("output_file", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        verify(args.json_file, args.output_file)
    except (OSError, RuntimeError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"verification failed: {error}") from error
    print(f"verified {args.json_file} and {args.output_file}")
