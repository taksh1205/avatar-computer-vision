"""Domain constraints for image metrics, with no inference about protected traits."""
from __future__ import annotations

import pandas as pd
from .audit import DataContractError, validate_catalog

NUMERIC_RANGES = {
    "mean_saturation_0_255":(0,255),
    "mean_brightness_0_255":(0,255),
    "hue_concentration_0_1":(0,1),
    "symmetry_proxy_0_1":(0,1),
    "skin_tone_fraction_proxy":(0,1),
    "flat_fraction":(0,1),
    "fine_texture_fraction":(0,1),
    "edge_density":(0,1),
    "entropy_bits":(0,8),
    "logo_binary":(0,1),
    "eye_count_detected_0_2":(0,2),
    "face_detected":(0,1),
    "smile_detected":(0,1),
    "contrast_sd":(0,128),
}


def inspect_catalog_metrics(df:pd.DataFrame)->dict:
    """Aggregate summary only; reject out-of-range measured values and nonnumeric entries."""
    base=validate_catalog(df)
    audit={}
    issues=[]
    for col,(lo,hi) in NUMERIC_RANGES.items():
        if col not in df:
            continue
        as_num=pd.to_numeric(df[col],errors="coerce")
        n_bad=int(((as_num<lo)|(as_num>hi)).sum())
        n_missing=int(as_num.isna().sum())
        audit[col]={"checked":int(len(df)),"invalid_range":n_bad,"missing_or_non_numeric":n_missing}
        if n_bad or n_missing:
            issues.append(col)
    base["measurement_checks"]=audit
    base["invalid_measurement_columns"]=issues
    return base


def assert_catalog_quality(df:pd.DataFrame)->dict:
    report=inspect_catalog_metrics(df)
    if report["invalid_measurement_columns"]:
        raise DataContractError("invalid image metric columns: "+", ".join(report["invalid_measurement_columns"]))
    return report
