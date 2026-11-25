# Archived exploratory work — not the validated pipeline

These historical notebooks and R/R Markdown scripts are retained for transparent code review and provenance, not as evidence that the research conclusions have been reproduced.

**Critical limitations discovered in the historical source:**

- Female-image-only pipelines used 168 then 192 female avatars. The earlier original image-metrics catalog contained 384 distinct names (192 female and 192 male). Historical female-only outputs are **not** a complete representation of avatar selections by study participants.
- Several derived “visual proxy” fields were inferred from filename, template, or gender rather than direct image measurement. In particular, inferred eyelashes, iris, skin shading, blush, brows, teeth, neck mechanism, seams, badges and tie/bow-tie features are **not validated observed attributes**. Do not use them as measured features in statistical conclusions.
- Some session mappings were not unambiguously matched, and condition-specific missing values can cause selection bias in pooled models.
- Original paths, feature names and model formulas evolved across drafts; these historical scripts are not an interchangeable set of final notebooks.

Use `src/avatar_vision/` for *auditable data validation and measured feature extraction*, and validate actual session-to-avatar coverage privately before any inferential research publication.
