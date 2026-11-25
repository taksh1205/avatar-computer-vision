# Reproducibility and execution plan

## What runs without private data

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test,vision]'
pytest -q
python scripts/audit_notebooks.py
python -m compileall -q src tests scripts
```

The test cases use **synthetic in-memory** mapping records and small synthetic images. No participant data or original avatar images ship with the repository.

## Authorized private workflow

Only with access to the lab-approved research dataset, and from an output path outside this repository:

```bash
python scripts/audit_private_dataset.py \
  --mapping /path/to/private/OSU_avatar_mapping_input.csv \
  --catalog /path/to/private/OSU_avatar_image_metrics_input.csv \
  --participants /path/to/private/d_osu_final.csv

python scripts/build_private_features.py \
  --mapping /path/to/private/OSU_avatar_mapping_input.csv \
  --catalog /path/to/private/OSU_avatar_image_metrics_input.csv \
  --participants /path/to/private/d_osu_final.csv \
  --output /path/to/private/participant_avatar_join.csv
```

**Important:** The audit exits non-zero until every mapping status is definitively matched and every avatar reference resolves. That is deliberate. Resolve flagged mappings through human review, not automated guessing. The aggregation command maintains participant keys and therefore writes *only* to explicitly named private or restricted directories.

To recompute the measurable portion of the catalog from licensed images, call `avatar_vision.features.measure_file(path)` for each image. It returns documented design labels plus a limited set of actual pixel measurements. It does **not** reproduce historical model-estimated facial attributes, arbitrary 54-column schemas, or research judgments.

## Legacy research code

`legacy/` retains five historical notebooks and their R/R Markdown counterparts. They are **historical**, have unresolved method/provenance issues, and require local research tables. They are not the current validated workflow.

## Research validation boundaries

- Structural checks: executed on the private original catalog and mapping, summarized without identifiers.
- Synthetic test suite: executed locally with no private data.
- Full original image extraction: not rerun; only an original, rights-cleared image corpus can establish that result.
- Human codings and R regression results: historical and not independently validated.
- No trained AI model or measured predictive accuracy is claimed by this repository.

See [RESEARCH_INTEGRITY.md](RESEARCH_INTEGRITY.md) for scientific limitations and required corrections.
