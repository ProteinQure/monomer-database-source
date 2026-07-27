# Release checklist

This checklist coordinates the source and generated datasets repositories.
Repeat the validation and release sections for every subsequent version.

## Validate a release candidate

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
git status --short
```

Review the diff, confirm the schema and provenance documentation still match,
and confirm the target tag does not already exist in either repository.
Release tags are immutable and must match `vMAJOR.MINOR.PATCH`, optionally with
a SemVer pre-release or build suffix.

## Publish

1. Create and publish the GitHub release in this source repository from the
   reviewed commit, using a tag as described above.
2. Monitor `Verify and publish monomers`.
3. Confirm that the datasets repository receives the generated commit and
   matching tag, then that `Verify generated monomers` creates its GitHub release
   with all six downloadable files.
4. Confirm the Zenodo record, metadata, archived files, version DOI, and concept
   DOI before announcing the release.

Never manually edit or retarget a released tag. Correct published data with a
new version.
