# Monomer database source

A curated, openly-licensed database of 2,400+ peptide monomers — canonical and non-canonical amino-acid backbones (α/β/γ/δ/ε), N-/C-terminal caps, and side-chain modifications — with physicochemical properties (MW, cLogP, tPSA), usage/availability signals, and structure identifiers (SMILES, InChIKey), for peptide and macrocycle design.

This repository is the editable source of truth and build tooling for the
ProteinQure monomer database. Data changes belong in
[`data/monomers.json`](data/monomers.json). Output formats are generated and
must not be edited by hand.

## Repository roles

| Repository | Responsibility | Accepts changes? |
| --- | --- | --- |
| `monomer-database-source` (this repository) | Authoritative JSON, conversion and verification code, tests, and release automation | Yes |
| [`monomer-database-datasets`](https://github.com/ProteinQure/monomer-database-datasets) | Versioned output formats intended for download and Zenodo archival | No; report changes here |

The generated repository is deliberately not an independent data source. Each
of its releases corresponds to a release tag in this repository.

## Work locally

Install [uv](https://docs.astral.sh/uv/) and run:

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

The converter requires an explicit `--output-type` of `csv`, `tsv`, or `sdf`;
the destination filename extension does not select conversion behavior. Input
must be a non-empty JSON array of objects. Every object must have exactly the
same fields; the first object determines column order in tabular formats.
Booleans become `true` or `false`, null becomes an empty cell, and nested
arrays or objects become compact, key-sorted JSON strings.

The SDF output uses each record's `SMILES` value to create a 2D structure. Its
molecule title and `rName` property are the `PQ_SYMBOL`, and every JSON field is
included as an SD property. RDKit is pinned in the converters' inline PEP 723
metadata so `uv run` creates the required isolated environment and the
generated structure blocks remain reproducible. All outputs use UTF-8 and LF
line endings.

Every executable helper declares its third-party dependencies in inline PEP
723 metadata. No persistent virtual environment or requirements file is
needed.

The machine-readable field and type contract is
[`schema/monomers.schema.json`](schema/monomers.schema.json).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the data-change workflow and
review expectations.

## Releases and reproducibility

A published GitHub release with a semantic version tag such as `v0.0.1`
triggers the release workflow. After tests pass, it:

1. validates the source JSON against its schema;
2. builds and verifies every supported output format;
3. copies the outputs plus the schema into the datasets repository;
4. generates `SHA256SUMS`;
5. commits the generated files to the datasets repository's `main` branch;
6. pushes the same immutable tag; and
7. lets the datasets repository verify the files and create the GitHub release
   that Zenodo archives.

The exact maintainer setup and release procedure are in
[RELEASE.md](RELEASE.md).

## Citation and licenses

The data, schema, and documentation are licensed under
[Creative Commons Attribution-ShareAlike 4.0 International](LICENSE-DATA). Executable
code, tests, and automation are licensed under the
[GNU Affero General Public License v3.0 or later](LICENSE-CODE). `LICENSE-DATA`
contains a second copy of the data license for explicit downstream reuse.
The requested attribution name is **ProteinQure**.

ProteinQure is the organizational creator in the repository's active citation
and Zenodo metadata.
