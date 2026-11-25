"""Image pixel statistics and explicitly declared avatar design metadata.

No subjective human attributes are inferred. Design labels come from filenames;
image metrics come from decoded BGR pixels, not from generator templates.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

NAME_PATTERN = re.compile(
    r"^avatar_(?P<type>[^_]+)_(?P<gender>male|female)_"
    r"(?P<emotion>happy|neutral)_(?P<color>[a-z]+)_"
    r"(?P<attire>formal|informal)_(?P<logo>nologo|[a-z0-9]+logo)_"
    r"v(?P<variant>\d+)$"
)


def parse_filename(filename: str) -> dict:
    """Return known experimental design factors, never CV predictions."""
    path = Path(filename)
    match = NAME_PATTERN.fullmatch(path.stem)
    if match is None:
        raise ValueError(
            f"filename outside documented design schema: {path.name}"
        )

    result = {
        "avatar_name": path.stem.removeprefix("avatar_"),
        "image_file_name": path.name,
    }
    result.update(
        {f"design_{key}": value for key, value in match.groupdict().items()}
    )
    result["design_variant"] = int(result["design_variant"])
    return result


def image_metrics_bgr(image: np.ndarray) -> dict:
    """Measure a BGR 3-channel image using deterministic OpenCV operations."""
    import cv2

    if (
        image is None
        or not isinstance(image, np.ndarray)
        or image.ndim != 3
        or image.shape[2] != 3
        or min(image.shape[:2]) < 2
    ):
        raise ValueError(
            "expected BGR image with height/width >=2 and three channels"
        )

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    smoothed = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gray, 60, 140)
    histogram = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    histogram = histogram[histogram > 0] / histogram.sum()

    pixel_diff = np.abs(
        gray.astype(np.float32) - np.fliplr(gray).astype(np.float32)
    )
    symmetry = float(np.clip(1.0 - pixel_diff.mean() / 255, 0, 1))

    return {
        "image_width_px": int(image.shape[1]),
        "image_height_px": int(image.shape[0]),
        "mean_saturation_0_255": float(hsv[:, :, 1].mean()),
        "mean_brightness_0_255": float(hsv[:, :, 2].mean()),
        "contrast_sd": float(gray.std()),
        "entropy_bits": float(-(histogram * np.log2(histogram)).sum()),
        "edge_density": float((edges > 0).mean()),
        "laplacian_variance": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        "symmetry_pixel_proxy_0_1": symmetry,
        "local_texture_proxy": float(
            np.abs(gray.astype(float) - smoothed.astype(float)).mean()
        ),
    }


def measure_file(path: str | Path) -> dict:
    """Decode a licensed image and combine design labels with pixel statistics."""
    import cv2

    image_path = Path(path)
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"could not read image: {image_path.name}")
    return {**parse_filename(image_path.name), **image_metrics_bgr(image)}
