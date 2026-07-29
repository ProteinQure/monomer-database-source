from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

REPOSITORY_ROOT = Path(__file__).parents[1]
MONOMERS_PATH = REPOSITORY_ROOT / "data" / "monomers.json"
SCHEMA_PATH = REPOSITORY_ROOT / "schema" / "monomers.schema.json"


class MonomersSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.monomers = json.loads(MONOMERS_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)

    def test_monomers_match_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.monomers)

    def test_symbols_are_unique_and_include_canonical_amino_acids(self) -> None:
        canonical_symbols = set("ACDEFGHIKLMNPQRSTVWY")
        actual_symbols = [record["PQ_SYMBOL"] for record in self.monomers]

        self.assertEqual(len(actual_symbols), len(set(actual_symbols)))
        self.assertLessEqual(canonical_symbols, set(actual_symbols))


if __name__ == "__main__":
    unittest.main()
