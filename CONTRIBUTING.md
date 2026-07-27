# Contributing

Propose data, documentation, conversion, and validation changes in this source
repository. The generated datasets repository does not accept direct changes.

## Data changes

1. Edit only `data/monomers.json`.
2. Keep every record's field set consistent. The first record determines
   column order in tabular outputs, so reorder fields only as an intentional
   format change.
3. Run:

   ```shell
   mkdir -p build
   install -m 0644 data/monomers.json build/monomers.json
   uv run scripts/convert.py --output-type csv data/monomers.json build/monomers.csv
   uv run scripts/convert.py --output-type tsv data/monomers.json build/monomers.tsv
   uv run scripts/convert.py --output-type sdf data/monomers.json build/monomers.sdf
   uv run scripts/verify.py build/monomers.json build/monomers.csv
   uv run scripts/verify.py build/monomers.json build/monomers.tsv
   uv run scripts/verify.py build/monomers.json build/monomers.sdf
   uv run scripts/validate_schema.py data/monomers.json schema/monomers.schema.json
   uv run scripts/run_tests.py
   ```

4. Commit the authoritative JSON and any related tests or documentation. Do
   not commit `build/`, Python bytecode, virtual environments, or generated
   outputs.
5. In the pull request, describe the provenance of the added or changed data
   and any review or validation performed. Do not include confidential,
   personal, access-controlled, or third-party data without confirmed
   publication rights.

## Tooling changes

Preserve deterministic output and compatibility with Python 3.10 or newer.
Add or update unit tests for conversion behavior. A change that alters generated
bytes or the data schema should update
`schema/monomers.schema.json` and be called out as a release
compatibility change.

## Reporting problems

Open an issue in this repository with the affected record identifiers, expected
behavior or values, supporting provenance, and the dataset version or DOI when
available. Avoid including secrets or private data in public issues.
