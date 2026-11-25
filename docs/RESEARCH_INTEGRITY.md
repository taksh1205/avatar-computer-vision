# Research integrity and historical data audit

This is an engineering audit of previously supplied, **private** research inputs. The source package does **not** redistribute participant records, session filenames, original images, or research-owned tables.

## Source of the numerical scope

| Artifact | Observed private source shape | What it proves | What it does not prove |
|---|---:|---|---|
| Original OSU image-metrics catalog | 384 rows × 26 columns | 192 labeled female and 192 labeled male avatar names, across designed variants | Public source can reproduce image features without the images |
| Earlier feature notebook output | 168 rows × 54 columns | One version of female-image feature construction | All selected avatars were covered |
| Later female feature output | 192 rows × 54 columns | The female-image catalog was expanded | Male avatars were covered |
| Mapping input | 190 rows × 18 columns | Each participant/version composite key occurs in the mapping input | All assignments were decisively confirmed |
| Participant study data | 190 rows × 282 columns | Three experimental conditions represented | Every session and image feature is valid |

The image-metrics catalog has 384 records, but the provided public source package intentionally excludes the corresponding artwork, so these records are **not** shipped as data fixtures. The 54-column output includes design metadata and proxies; 54 is **not** a count of independently verified visual detections.

## Session alignment and coverage

The mapping source reports **182 `Matched`, seven `Matched - Review`, and one `Needs Review - No close session within threshold`**. The last eight assignments require manual adjudication before inference. Composite `(Version.ID, User.ID)` alignment must be one-to-one, and a session filename is not proof of an unambiguous match.

The study source contains **62 `create_av`, 64 `human_av`, and 64 `no_av`** participant rows. `No avatar` and `Default avatar` are meaningful sentinel conditions, not missing images to fabricate or substitute with female images. `final_avatar_name_source` was populated for only 124 mapping rows; do not fill missing outcomes by assuming final equals first.

**Historical blocker:** the image creation notebook operated on the female-only corpus, even though the participant mapping references male avatars. Downstream historical feature and model tables therefore cannot be treated as fully verified joined visual measures. Do not cite their statistical coefficients or p-values as validated study findings.

## Provenance rules

1. Design labels extracted from filenames (type, recorded design gender, expression, color, logo, attire and image variant) must be marked `design_*`. These are generator/template labels, not learned CV predictions.
2. Pixel-derived measures (HSV, contrast, entropy, texture, edges, symmetry proxy) require direct image decoding. They are measurable quantities, not psychological interpretations.
3. Human judgments (realism, warmth, apparent age, role congruence, perceived ethnicity, ethnicity/skin-tone judgments) must have an explicit human-coding protocol and coder agreement to be used as ground truth. The repository provides no verified protocol for these measurements.
4. Do **not** infer eyelashes, iris, skin shading, blush, eyebrows, teeth, mechanical neck, panel seams, name badges or tie/bow-tie from design gender, template or heuristics and then call them observed visual details.
5. Distinguish the feature *count* from coverage: 192 × 54 is the size of a female-only tabular artifact, **not** 10,368 validated participant-linked observations.
6. Do not infer effects of avatar design from observational associations without confirming study design, condition restrictions, data missingness, model specification, and multiplicity control.

## Acceptance gates before inferential claims

- Resolve or explicitly exclude the eight non-definitive session matches according to the supervisor's rules.
- Verify a complete, rights-cleared catalog for the actual first/second/third/final avatar selections, including male avatars and sentinel conditions.
- Document mapping extraction from original session logs and filename features with stable versioned code.
- Establish per-feature source (filename design, pixel measurement, human annotation, or derived statistic) and refuse unvalidated proxies.
- Audit join cardinality, condition-specific missingness and outcome inclusion; rerun authorized R analysis using pre-specified models.
- Report exact sample sizes, uncertainty estimates and missingness handling; keep all participant-level outputs outside public GitHub.

**Conclusion:** This package demonstrates documented data-engineering and computer-vision methods and openly exposes unresolved research validation. It does not claim the original inferential study is complete or independently reproduced.
