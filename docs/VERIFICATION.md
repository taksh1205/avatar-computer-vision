# Avatar Vision — Engineering verification and release gates

**Status:** Public source and synthetic engineering checks pass; original study inference remains blocked until the supervisor adjudicates eight session mapping statuses and authorizes final model specifications.

## Independently executed in this review

| Gate | Result | Evidence or limitation |
|---|---|---|
| Synthetic research-contract and pixel-measurement tests | **26 passed, 0 failed, 0 skipped** | `PYTHONPATH=src pytest -q` on Python 3.13.5 |
| Feature dictionary matches source registry | **PASS** | `python scripts/build_feature_dictionary.py --check`; covers all ten computed pixel measurements and seven design factors |
| Original synthetic visual illustration | **PASS** | `python scripts/create_visual_demo.py --check`; SVG rendered and reviewed, no embedded external artwork |
| Independent inference authorization gate | **PASS** | New tests verify unresolved session records and missing manual approval prevent inferential use |
| Privacy-safe synthetic end-to-end example | **PASS** | `PYTHONPATH=src python scripts/demo_synthetic.py`, three fabricated participant records, two fabricated design labels, one synthetic pixel image |
| Historical notebook structural/syntax audit | **5 notebooks, 0 static findings** | `python scripts/audit_notebooks.py` (not notebook execution) |
| Python compilation | **PASS** | `python -m compileall -q src scripts tests` |
| Data / image asset scanner | **PASS** | `python scripts/scan_public_release.py` excludes original source datasets and artwork |
| Original private 384-name catalog structural checks | **PASS: 384 unique names; 14 range checks valid** | Tested in-memory on original private `OSU_avatar_image_metrics_input.csv`, without writing public rows |
| Original private participant mapping | **190/190 composite joins; 8 statuses require review** | 182 matched, 7 matched-review, 1 unresolved; the `ready_for_inference` gate correctly returns `false` |
| Original private catalog reference coverage | **PASS** | All 124 real first-avatar, 61 second, 48 third and 124 final named references resolve in the 384-name catalog; no-avatar sentinels are not hallucinated into image rows |
| Private participant-feature join | **PASS structurally; inference not approved** | 190 rows preserved; first 124, second 61, third 48, final 124 actual feature matches; five unapproved image fields excluded from new joined features |
| Private source image naming | **192/192 parsed, 192 distinct, 0 outside catalog** | Rights-restricted original ZIP inspected in memory; these are 192 female avatar images |
| Private source image decoding | **3 sampled images decoded and measured** | 1024×1024 BGR images, measured saturation within HSV bounds; no raw pixels redistributed |
| R research analysis | **NOT EXECUTED** | R was not installed in the review environment; guarded exploratory R script is source-reviewed, not validated |
| GitHub Actions CI | **CONFIGURED, NOT YET EXECUTED** | Workflow uses a three-Python-version matrix; verification requires GitHub runner after repository creation |
| Full original research inference | **BLOCKED** | Eight session mapping statuses and the historical female-only feature issue need resolution before any inferential claim |

## What this proves

The code demonstrably implements reproducible pixel-statistic extraction, explicit filename design labels, privacy-aware research-data auditing, data-quality checks and controlled joins across experimental conditions. It does **not** prove predictive classification accuracy, causal relationships, rater agreement, successful execution of historical R models or validity of the original model coefficients.

## Publication readiness

- **Source-only public repository:** ready after owner reviews legal attribution and pushes to a repository.
- **Model/accuracy claims:** not supported by released code; omit.
- **Raw dataset/artwork publication:** not authorized by the user's source-code-only permission.
- **Remote CI status:** needs a first green run; do not advertise CI as passing beforehand.

## Repeat exactly

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

See [RESEARCH_INTEGRITY.md](RESEARCH_INTEGRITY.md) for the eight unresolved source assignments and model-provenance constraints.

### Packaging/install check

The extracted project imported correctly after an editable install using `pip install --no-deps --no-build-isolation -e <extracted-project>` with the environment's preinstalled build tools. A normal isolated pip installation was **not** independently verified because this review environment cannot reach the package index to install its build requirements. On a connected machine, the documented `pip install -e '.[test,vision]'` is the intended installation route; verify it in GitHub Actions before claiming a green clean install.

### v0.3 scope

This final source-polishing pass added seven regression tests. They verify feature-registry coverage, distinct lab sign-off, protection from status edits after audit, refusal to use no-avatar condition rows containing image features, generated-document freshness and the absence of embedded image references in the SVG. R analyses were not executed; original study results remain out of scope. Hosted CI is configured but not run.
