# Monomer database source
[![Release](https://img.shields.io/github/v/release/ProteinQure/monomer-database-source?label=release&color=f5995b)](https://github.com/ProteinQure/monomer-database-source/releases/latest)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21684533-1682D4)](https://doi.org/10.5281/zenodo.21684533)
![Monomers](https://img.shields.io/badge/monomers-2488-2e6e8e)
[![Data: CC BY-SA 4.0](https://img.shields.io/badge/data-CC%20BY--SA%204.0-lightgrey.svg)](LICENSE-DATA)
[![Code: AGPL v3](https://img.shields.io/badge/code-AGPL%20v3-lightgrey.svg)](LICENSE-CODE)

The Monomer Database is a curated, openly licensed resource for peptide and macrocycle design. 2,488 chemically standardized canonical and non-canonical monomers spanning α/β/γ/δ/ε backbones plus N- and C-terminal caps, with SMILES, InChIKeys, systematic IUPAC names, natural-analogue mapping, computed physicochemical properties (MW, cLogP, tPSA), and commercial-availability signals. Each entry carries a ProteinQure-derived HELM-style monomer shorthand.

**This repository is the editable source of truth and build tooling for the
ProteinQure monomer database.** Data changes belong in
[`data/monomers.json`](data/monomers.json). Output formats are generated and
must not be edited by hand.

## Interactive Monomer Explorer UI

The Monomer Database can be interactively browsed, explored and searched via the free [Monomer Explorer](https://monomers.proteinqure.com/) hosted by [ProteinQure](https://proteinqure.com). Search the database by name, SMILES, or even a partially remembered name, and retrieve the nearest neighbours of any monomer ranked by Tanimoto similarity. The Chemical Exploration view maps the space around a selected monomer across four regions; close analogues, potential activity cliffs, putative scaffold hops, and the far edge of the space.

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

When using version `v1.0.0`, cite the archived dataset:

> ProteinQure. (2026). *Monomer database datasets* (Version v1.0.0)
> [Dataset]. Zenodo.
> https://doi.org/10.5281/zenodo.21684534

For another version, use the citation and version-specific DOI on its Zenodo
record. GitHub-readable citation metadata is provided in
[`CITATION.cff`](https://github.com/ProteinQure/monomer-database-datasets/blob/main/CITATION.cff) in the [`monomer-database-datasets`](https://github.com/ProteinQure/monomer-database-datasets)
repository but the authoritative data source is this [`monomer-database-source`](https://github.com/ProteinQure/monomer-database-source) repository.

The data, schema, and documentation are licensed under
[Creative Commons Attribution-ShareAlike 4.0 International](LICENSE-DATA). Executable
code, tests, and automation are licensed under the
[GNU Affero General Public License v3.0 or later](LICENSE-CODE). `LICENSE-DATA`
contains a second copy of the data license for explicit downstream reuse.
The requested attribution name is **ProteinQure**.
Repository-side Zenodo and GitHub citation metadata are described in
[ZENODO.md](https://github.com/ProteinQure/monomer-database-datasets/blob/main/ZENODO.md) in the [`monomer-database-datasets`](https://github.com/ProteinQure/monomer-database-datasets)
repository.
