"""Explicit structural gating of participant-level analysis.

The joining utility may preserve unresolved rows for private QA; those rows must
never be silently treated as authorized inferential observations.
"""

from __future__ import annotations

import pandas as pd

from .audit import DataContractError, KEYS


def require_inference_ready(joined: pd.DataFrame, audit: dict, *, approved_by_lab: bool = False) -> pd.DataFrame:
    """Return a defensive copy only when structural and manual review gates pass.

    This check does not prove causal inference, rater reliability or the validity
    of a statistical model; that additionally requires a registered analysis plan.
    """
    if not audit.get('ready_for_inference', False):
        raise DataContractError('session, catalog or condition audit unresolved; inference blocked')
    if not approved_by_lab:
        raise DataContractError('lab adjudication and analysis authorization required')
    required = set(KEYS) | {'version_enc', 'mapping_status_source'}
    if not required.issubset(joined.columns):
        raise DataContractError('inference table missing required audit fields')
    if joined.empty or joined[list(KEYS)].isna().any().any() or joined.duplicated(list(KEYS)).any():
        raise DataContractError('inference table has missing or duplicate participant keys')
    if not joined['mapping_status_source'].fillna('').astype(str).str.strip().str.casefold().eq('matched').all():
        raise DataContractError('inference table contains unreviewed mappings')
    for reference in ('first', 'second', 'third', 'final'):
        flag = f'{reference}_catalog_match'
        if flag not in joined.columns:
            raise DataContractError(f'inference table missing {flag}')
    if (joined.loc[joined['version_enc'].eq('no_av'), [f'{i}_catalog_match' for i in ('first','second','third','final')]]
            .fillna(False).astype(bool).any().any()):
        raise DataContractError('no-avatar condition includes an actual avatar feature')
    return joined.copy(deep=True)
