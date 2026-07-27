from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from rdkit import Chem

SCRIPTS_DIRECTORY = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from convert import convert, load_records  # noqa: E402
from verify import verify  # noqa: E402


class ConversionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory_context = tempfile.TemporaryDirectory()
        self.temporary_directory = Path(self.temporary_directory_context.name)
        self.source = self.temporary_directory / "source.json"
        self.source.write_text(
            json.dumps(
                [
                    {"id": 1, "enabled": True, "note": None},
                    {"id": 2, "enabled": False, "note": "a,b"},
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory_context.cleanup()

    def test_csv_conversion_is_deterministic(self) -> None:
        output = self.temporary_directory / "output.csv"

        convert(self.source, output, "csv")

        self.assertEqual(
            output.read_text(encoding="utf-8"),
            'id,enabled,note\n1,true,\n2,false,"a,b"\n',
        )
        verify(self.source, output)

    def test_tsv_conversion_is_deterministic(self) -> None:
        output = self.temporary_directory / "output.tsv"

        convert(self.source, output, "tsv")

        self.assertEqual(
            output.read_text(encoding="utf-8"),
            "id\tenabled\tnote\n1\ttrue\t\n2\tfalse\ta,b\n",
        )
        verify(self.source, output)

    def test_sdf_conversion_preserves_structure_and_properties(self) -> None:
        self.source.write_text(
            json.dumps(
                [
                    {
                        "PQ_SYMBOL": "A",
                        "SMILES": "N[C@@H](C)C(=O)O",
                        "POPULARITY": 98.6,
                        "PROTECTED": "TRUE",
                        "ENABLED": True,
                        "NOTE": None,
                    },
                    {
                        "PQ_SYMBOL": "G",
                        "SMILES": "NCC(=O)O",
                        "POPULARITY": 99.8,
                        "PROTECTED": "FALSE",
                        "ENABLED": False,
                        "NOTE": None,
                    },
                ]
            ),
            encoding="utf-8",
        )
        output = self.temporary_directory / "output.sdf"

        convert(self.source, output, "sdf")
        first_output = output.read_bytes()
        convert(self.source, output, "sdf")

        self.assertEqual(output.read_bytes(), first_output)
        molecules = list(Chem.SDMolSupplier(str(output), removeHs=False))
        self.assertEqual(len(molecules), 2)
        self.assertEqual(molecules[0].GetProp("_Name"), "A")
        self.assertEqual(molecules[0].GetProp("rName"), "A")
        self.assertEqual(molecules[0].GetProp("POPULARITY"), "98.6")
        self.assertEqual(molecules[0].GetProp("ENABLED"), "true")
        self.assertEqual(molecules[0].GetProp("NOTE"), "")
        self.assertEqual(molecules[1].GetProp("PROTECTED"), "FALSE")
        self.assertEqual(
            Chem.MolToSmiles(molecules[0], isomericSmiles=True),
            Chem.MolToSmiles(
                Chem.MolFromSmiles("N[C@@H](C)C(=O)O"), isomericSmiles=True
            ),
        )
        verify(self.source, output)

    def test_sdf_conversion_rejects_invalid_smiles(self) -> None:
        self.source.write_text(
            '[{"PQ_SYMBOL": "bad", "SMILES": "not a smiles"}]',
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "invalid SMILES"):
            convert(self.source, self.temporary_directory / "output.sdf", "sdf")

    def test_explicit_output_type_does_not_depend_on_filename_extension(self) -> None:
        output = self.temporary_directory / "output.without-a-format-extension"

        convert(self.source, output, "tsv")

        self.assertEqual(
            output.read_text(encoding="utf-8"),
            "id\tenabled\tnote\n1\ttrue\t\n2\tfalse\ta,b\n",
        )

    def test_rejects_unsupported_output_type(self) -> None:
        output = self.temporary_directory / "output.txt"

        with self.assertRaisesRegex(ValueError, "unsupported output type"):
            convert(self.source, output, "text")

    def test_rejects_inconsistent_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            source.write_text('[{"id": 1}, {"id": 2, "extra": 3}]', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "inconsistent fields"):
                load_records(source)


if __name__ == "__main__":
    unittest.main()
