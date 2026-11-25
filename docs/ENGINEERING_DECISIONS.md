# Technical decisions, trade-offs and review questions

The project prioritizes scientific traceability over an inflated count of AI models.

## Why preserve original notebooks instead of replacing them?

The prior work includes valuable CV and R methods, but its female-only extraction and proxy-based variables cannot be silently converted into a validated mixed-gender study. All five notebooks and the R sources are retained under `legacy/` with execution outputs stripped. The tested pipeline lives in `src/avatar_vision/`.

## Why an image-metrics catalog rather than one big multimodal model?

The feature family matters for reproducibility: generator design factors are known from filenames, image statistics require actual pixel processing, and subjective traits require blinded human annotation and agreement checks. Mixing these categories produces plausible-looking but scientifically unsupported results.

## Why block downstream inference when session matches are uncertain?

A mislabeled participant-to-avatar mapping may produce an association between survey answers and the wrong image. Such contamination can systematically bias an effect estimate while escaping code-level type checks. The tool therefore reports the seven review matches and one unresolved match and returns a non-ready flag until adjudicated.

## Why preserve the no-avatar condition as missing instead of imputing an avatar?

The experimental arms have different exposure mechanisms. Treating `No avatar` as an unobserved female image or a missing row conflates assignment with image attributes. The join preserves all 190 participants, including all 64 records in the no-avatar condition.

## Why use deterministic image measurements?

HSV mean saturation, mean brightness, edge density, entropy and contrast are directly reproducible given an image and preprocessing choices. They do not require training or fabricate demographic or psychological labels. The current library does not claim equivalence with historic pixel metrics without preprocessing parity checks.

## Why exclude legacy model-derived facial attributes?

The original feature generation included outputs with names like eyelash presence and skin shading. Their extraction or human validation was not established for the full source corpus. The new participant join only accepts a documented allowlist of design factors and pixel-derived statistics; unapproved columns are listed in audit diagnostics.

## Questions to resolve with the lab before scientific publication

1. Which session record is authoritative for the eight non-definitive matches? Are the original session parsing and timestamp tolerances documented?
2. Is the 384-image all-gender design catalog the correct experimental asset inventory, and what rights govern male-avatar artwork not supplied in the uploaded archive?
3. Which attributes were measured automatically, which manually coded, and where are coding rules and inter-rater agreement recorded?
4. Which study outcomes and experimental conditions belong in each model, and what is the missingness/inclusion rule?
5. Are the historical statistical coefficients exploratory or approved for reporting?

No response to these questions is invented by this public repository.
