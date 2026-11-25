"""Auditable joins between participant sessions and avatar image metrics.

Resulting participant-level data must remain in an approved private location.
"""

from __future__ import annotations

import pandas as pd

from .audit import (
    AVATAR_FIELDS,
    KEYS,
    DataContractError,
    _avatar_key,
    _key_integrity,
    audit_mapping,
    validate_catalog,
)

# Avoid carrying template-inferred labels, unvalidated model detections or
# subjective human ratings forward as if they were actual image observations.
APPROVED_CATALOG_FEATURES = frozenset(
    {
        "avatar_type",
        "avatar_gender",
        "avatar_emotion",
        "clothing_color",
        "attire_style",
        "logo_presence",
        "logo_binary",
        "image_variant",
        "design_type",
        "design_gender",
        "design_emotion",
        "design_color",
        "design_attire",
        "design_logo",
        "design_variant",
        "image_width_px",
        "image_height_px",
        "mean_saturation_0_255",
        "mean_brightness_0_255",
        "hue_concentration_0_1",
        "symmetry_proxy_0_1",
        "symmetry_pixel_proxy_0_1",
        "central_face_texture",
        "laplacian_variance",
        "flat_fraction",
        "fine_texture_fraction",
        "entropy_bits",
        "contrast_sd",
        "edge_density",
        "local_texture",
        "local_texture_proxy",
    }
)


def join_participant_features(
    mapping: pd.DataFrame,
    catalog: pd.DataFrame,
    participants: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Preserve experimental conditions and attach explicitly sourced features.

    The data validation report can indicate missing or uncertain session matches.
    This function does not infer missing avatars or approve statistical inference.
    """
    report = audit_mapping(mapping, catalog, participants)
    _key_integrity(mapping, "mapping")
    _key_integrity(participants, "participants")
    validate_catalog(catalog)

    mapping_columns = list(KEYS) + list(AVATAR_FIELDS)
    mapping_columns.append("mapping_status_source")
    merged = participants.merge(
        mapping.loc[:, mapping_columns],
        on=list(KEYS),
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    if (merged["_merge"] != "both").any():
        raise DataContractError("not all participants have a matching mapping row")
    merged = merged.drop(columns="_merge")

    measured_columns = [
        field for field in catalog.columns if field in APPROVED_CATALOG_FEATURES
    ]
    report["excluded_unapproved_catalog_columns"] = sorted(
        set(catalog.columns) - set(measured_columns) - {"avatar_name"}
    )

    catalog_names = set(catalog["avatar_name"].astype(str))
    for field, prefix in zip(
        AVATAR_FIELDS, ("first", "second", "third", "final"), strict=True
    ):
        selected = merged[field].map(_avatar_key)
        merged[f"{prefix}_catalog_match"] = selected.isin(catalog_names)

        renamed = catalog.loc[:, ["avatar_name"] + measured_columns].rename(
            columns={
                "avatar_name": "_join_avatar",
                **{column: f"{prefix}_{column}" for column in measured_columns},
            }
        )
        merged["_join_avatar"] = selected
        merged = merged.merge(
            renamed,
            on="_join_avatar",
            how="left",
            validate="many_to_one",
        ).drop(columns="_join_avatar")

    report["feature_coverage"] = {
        prefix: int(merged[f"{prefix}_catalog_match"].sum())
        for prefix in ("first", "second", "third", "final")
    }
    return merged, report
