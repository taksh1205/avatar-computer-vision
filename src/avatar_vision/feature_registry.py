"""Source-of-truth descriptions for measured pixels and encoded design factors.

Only measured metrics returned by ``image_metrics_bgr`` are described as CV features.
Design metadata is never interpreted as model-detected demographic or facial traits.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureSpec:
    meaning: str
    unit_or_domain: str
    provenance: str
    caution: str


PIXEL_FEATURES: dict[str, FeatureSpec] = {
    "image_width_px": FeatureSpec("Raster width", "pixels, integer >= 2", "Decoded image width", "Depends on image export size"),
    "image_height_px": FeatureSpec("Raster height", "pixels, integer >= 2", "Decoded image height", "Depends on image export size"),
    "mean_saturation_0_255": FeatureSpec("Mean HSV saturation", "OpenCV HSV saturation [0, 255]", "Mean S channel of BGR->HSV", "Not a calibrated measure of perceived colorfulness"),
    "mean_brightness_0_255": FeatureSpec("Mean HSV value", "OpenCV HSV V [0, 255]", "Mean V channel of BGR->HSV", "Sensitive to lighting and export processing"),
    "contrast_sd": FeatureSpec("Gray intensity standard deviation", "gray-level standard deviation", "Population SD of grayscale pixels", "Global contrast proxy; no semantic content"),
    "entropy_bits": FeatureSpec("Shannon entropy of grayscale histogram", "bits per pixel intensity (0–8)", "Entropy over 256 intensity bins", "Not a measure of model uncertainty"),
    "edge_density": FeatureSpec("Fraction of nonzero Canny edge pixels", "fraction [0, 1]", "Canny thresholds 60 and 140 on grayscale", "Threshold-dependent, not object-boundary accuracy"),
    "laplacian_variance": FeatureSpec("Variance of grayscale Laplacian response", "squared response units", "OpenCV CV_64F Laplacian variance", "Sharpness proxy; sensitive to noise and scaling"),
    "symmetry_pixel_proxy_0_1": FeatureSpec("Normalized left-right grayscale similarity", "score [0, 1]", "1 - mean(abs(gray-flipped gray))/255", "Pixel proxy, not facial or aesthetic symmetry"),
    "local_texture_proxy": FeatureSpec("Mean absolute grayscale residual after 3x3 blur", "gray-level absolute deviation", "Mean abs(gray - GaussianBlur(3x3))", "Texture proxy; not a trained texture classifier"),
}

DESIGN_FACTORS: dict[str, FeatureSpec] = {
    "design_type": FeatureSpec("Avatar kind encoded in filename", "string", "Name convention", "Not visually detected"),
    "design_gender": FeatureSpec("Creator-design category encoded in filename", "male/female code", "Name convention", "Not a demographic prediction, identity or sex inference"),
    "design_emotion": FeatureSpec("Generator-design emotion label", "happy/neutral code", "Name convention", "Not an expression-recognition model"),
    "design_color": FeatureSpec("Encoded palette label", "string", "Name convention", "May differ from actual measured pixels"),
    "design_attire": FeatureSpec("Encoded clothing-design label", "formal/informal code", "Name convention", "Not a clothing classifier"),
    "design_logo": FeatureSpec("Encoded logo-design label", "string", "Name convention", "Not logo detection"),
    "design_variant": FeatureSpec("Design variant index", "positive integer", "Name convention", "Not a numerical rank of visual quality"),
}

# Earlier private catalog features are inherited historical columns, not necessarily
# produced by this module. Their definitions must be checked against the source study.
LEGACY_CATALOG_NOTE = (
    "Historical catalog fields and 54-column exploratory exports are source-specific. "
    "The new pixel extractor does not claim to reproduce those columns, train a "
    "classifier, identify facial anatomy, or validate prior human annotations."
)
