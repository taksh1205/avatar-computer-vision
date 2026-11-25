"""Privacy-aware validation of avatar catalogs and participant/session mappings.

Public diagnostics contain aggregated counts only. Participant identifiers,
raw selections, and session filenames never appear in report values.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

KEYS = ("Version.ID", "User.ID")
AVATAR_FIELDS = ("avatar_1", "avatar_2", "avatar_3", "final_avatar_name_source")
SENTINELS = frozenset({"", "no avatar", "default avatar", "none", "nan", "na"})


class DataContractError(ValueError):
    """Input research data violates a required structural invariant."""


def _require(frame: pd.DataFrame, fields: tuple[str, ...], label: str) -> None:
    missing = sorted(set(fields) - set(frame.columns))
    if missing:
        raise DataContractError(f"{label}: missing columns {missing}")


def _key_integrity(frame: pd.DataFrame, label: str) -> None:
    _require(frame, KEYS, label)
    if frame.loc[:, list(KEYS)].isna().any(axis=None):
        raise DataContractError(f"{label}: null composite participant keys")
    if frame.duplicated(list(KEYS)).any():
        raise DataContractError(f"{label}: duplicated composite participant keys")


def _avatar_key(value: Any) -> str | None:
    """Treat explicitly absent/default avatars as sentinels, not filenames."""
    if pd.isna(value):
        return None
    token = str(value).strip()
    return None if token.casefold() in SENTINELS else token


def validate_catalog(catalog: pd.DataFrame) -> dict[str, Any]:
    """Check unique names without implying the underlying artwork is available."""
    _require(catalog, ("avatar_name",), "catalog")
    names = catalog["avatar_name"].dropna().astype(str).str.strip()
    if len(names) != len(catalog) or (names == "").any():
        raise DataContractError("catalog: empty avatar names")
    if names.duplicated().any():
        raise DataContractError("catalog: duplicate avatar names")

    report: dict[str, Any] = {
        "catalog_rows": int(len(catalog)),
        "unique_names": int(names.nunique()),
    }
    if "avatar_gender" in catalog:
        counts = catalog["avatar_gender"].fillna("missing").value_counts()
        report["gender_counts"] = {
            str(key): int(value) for key, value in sorted(counts.items())
        }
    return report


def _participant_alignment(
    mapping: pd.DataFrame, participants: pd.DataFrame
) -> dict[str, int]:
    """Return only count-level join diagnostics, never actual participant keys."""
    columns = list(KEYS)
    left = mapping[columns].merge(
        participants[columns], on=columns, how="left", indicator=True
    )
    right = participants[columns].merge(
        mapping[columns], on=columns, how="left", indicator=True
    )
    return {
        "mapping_unmatched": int((left["_merge"] == "left_only").sum()),
        "participant_unmatched": int((right["_merge"] == "left_only").sum()),
        "common_keys": int((left["_merge"] == "both").sum()),
    }


def _condition_coverage(
    mapping: pd.DataFrame, participants: pd.DataFrame
) -> dict[str, dict[str, dict[str, int]]]:
    selected = mapping[list(KEYS) + list(AVATAR_FIELDS)].merge(
        participants[list(KEYS) + ["version_enc"]],
        on=list(KEYS),
        how="inner",
        validate="one_to_one",
    )
    result: dict[str, dict[str, dict[str, int]]] = {}
    for condition, group in selected.groupby("version_enc", dropna=False):
        per_field: dict[str, dict[str, int]] = {}
        for field in AVATAR_FIELDS:
            values = group[field]
            is_sentinel = (
                values.notna()
                & values.astype(str).str.strip().str.casefold().isin(SENTINELS)
            )
            is_actual = values.map(_avatar_key).notna()
            per_field[field] = {
                "actual_avatar": int(is_actual.sum()),
                "sentinel": int(is_sentinel.sum()),
                "missing": int(values.isna().sum()),
            }
        result[str(condition)] = per_field
    return result


def audit_mapping(
    mapping: pd.DataFrame,
    catalog: pd.DataFrame,
    participants: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Audit catalog lookups, session statuses, key integrity and study conditions.

    `ready_for_inference` is a *structural* gate only. Even if true, model
    specifications, human annotations and scientific claims need separate review.
    """
    _key_integrity(mapping, "mapping")
    _require(mapping, AVATAR_FIELDS + ("mapping_status_source",), "mapping")
    report = validate_catalog(catalog)
    report["mapping_rows"] = int(len(mapping))
    report["distinct_mapped_people"] = int(len(mapping))

    statuses = mapping["mapping_status_source"].fillna("Unspecified").value_counts()
    report["mapping_status_counts"] = {
        str(key): int(value) for key, value in sorted(statuses.items())
    }
    report["mapping_review_required"] = int(
        sum(
            value
            for status, value in statuses.items()
            if str(status).strip().casefold() != "matched"
        )
    )

    catalog_names = set(catalog["avatar_name"].astype(str).str.strip())
    references: dict[str, dict[str, int]] = {}
    for field in AVATAR_FIELDS:
        actual = [key for value in mapping[field] if (key := _avatar_key(value))]
        unmatched = [key for key in actual if key not in catalog_names]
        references[field] = {
            "referenced": len(actual),
            "not_in_catalog": len(unmatched),
            "distinct_unmatched": len(set(unmatched)),
        }
    report["avatar_references"] = references

    if participants is not None:
        _key_integrity(participants, "participants")
        report["participant_join"] = _participant_alignment(mapping, participants)
        if "version_enc" in participants:
            counts = participants["version_enc"].fillna("missing").value_counts()
            report["condition_counts"] = {
                str(key): int(value) for key, value in sorted(counts.items())
            }
            coverage = _condition_coverage(mapping, participants)
            report["condition_avatar_coverage"] = coverage
            if "no_av" in coverage:
                report["no_avatar_condition_conflicts"] = sum(
                    coverage["no_av"][field]["actual_avatar"]
                    for field in AVATAR_FIELDS
                )

    alignment = report.get("participant_join", {})
    report["ready_for_inference"] = bool(
        participants is not None
        and report["mapping_review_required"] == 0
        and all(item["not_in_catalog"] == 0 for item in references.values())
        and alignment.get("mapping_unmatched", -1) == 0
        and alignment.get("participant_unmatched", -1) == 0
        and report.get("no_avatar_condition_conflicts", 0) == 0
    )
    return report


def require_publication_safe_columns(frame: pd.DataFrame) -> None:
    """Refuse to treat any participant/session-level table as a public fixture."""
    forbidden = {
        "User.ID",
        "Version.ID",
        "robot_session_id_source",
        "session_file_name_source",
        "Fitbit1",
        "Fitbit2",
    }
    found = sorted(set(frame.columns) & forbidden)
    if found:
        raise DataContractError(
            f"participant/session columns must remain private: {found}"
        )
