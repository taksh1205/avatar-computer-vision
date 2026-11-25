# GitHub release checklist — Avatar Vision v0.3

## Code/source portfolio release

- [x] Retained the original five Jupyter notebooks and R/R Markdown source work in `legacy/`, without publishing datasets or original artwork.
- [x] Separated metadata encoded in avatar filenames from measurements computed from image pixels.
- [x] Documented all ten new OpenCV metric outputs with units, algorithms, and known limits.
- [x] Built an original **synthetic-only** visual feature illustration; no participant photos, avatar research artwork or source sessions are embedded.
- [x] Added an explicit structural + lab-approval gate for participant-level inference.
- [x] Added public synthetic tests and code-generated documentation checks.
- [x] Retained all unresolved mapping statuses and female-only historical feature scope in the README.
- [ ] Push the source-only code to the owner's new `avatar-computer-vision` GitHub repository.
- [ ] Observe first green hosted GitHub Actions run; configured CI is not the same as executed CI.
- [ ] Review collaborator attribution and the final repository license before selecting a public redistribution license.

## Scientific results — NOT signed off

- [ ] The lab resolves seven marked-review and one unresolved participant-session mappings, or documents approved exclusion rules.
- [ ] Verify full avatar-feature provenance for both female and male variants, or explicitly limit analysis to the authorized subset.
- [ ] Re-run the approved historical R model specification with a registered inclusion rule, outcome definition and approved private inputs.
- [ ] Check treatment assignment and selection timing for confounding, missingness and temporal leakage.
- [ ] Independently review any published effect sizes or claims about human–robot interaction.

## Reproduce software verification

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test,vision]'
pytest -q
python scripts/demo_synthetic.py
python scripts/build_feature_dictionary.py --check
python scripts/create_visual_demo.py --check
python scripts/audit_notebooks.py
python scripts/scan_public_release.py
python -m compileall -q src scripts tests
```

**Interpretation:** Passing all public checks proves the extracted code, deterministic synthetic feature example and research-data integrity contracts are functional. It does *not* validate historical statistical conclusions or provide a cross-gender, labeled model-performance estimate.
