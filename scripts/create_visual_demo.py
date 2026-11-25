#!/usr/bin/env python3
"""Create an ORIGINAL, synthetic-only illustrated feature demo.

Shapes are drawn in SVG for human viewing, while the corresponding synthetic
raster samples are independently drawn with OpenCV for deterministic statistics.
No real avatar artwork, face images or research participants are loaded.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np

from avatar_vision.features import image_metrics_bgr

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'docs' / 'assets' / 'synthetic_feature_demo.svg'
PALETTES = [
    ('Blue / simple', '#e4f2ff', '#1b64a8', '#ffd0a3', '#3f5c8c'),
    ('Warm / detailed', '#fff0dd', '#d76236', '#ffd1ae', '#8b3d33'),
    ('Green / contrast', '#e4f9ed', '#146d59', '#f7c4a7', '#263c2d'),
]


def render_sample(background: tuple[int, int, int], garment: tuple[int, int, int], *, detail: int) -> np.ndarray:
    import cv2
    img = np.zeros((144, 144, 3), dtype=np.uint8)
    img[:] = background
    cv2.rectangle(img, (15, 103), (129, 143), garment, -1)
    cv2.circle(img, (72, 64), 36, (172, 210, 245), -1)
    cv2.circle(img, (60, 60), 4, (24, 38, 54), -1)
    cv2.circle(img, (84, 60), 4, (24, 38, 54), -1)
    cv2.ellipse(img, (72, 78), (14, 7), 0, 0, 180, (34, 50, 70), 2)
    for i in range(detail):
        x = 28 + i * 22
        cv2.line(img, (x, 118), (x + 10, 137), (250, 245, 240), 2)
    return img


def _xml() -> str:
    metrics = [
        image_metrics_bgr(render_sample((255, 242, 228), (168, 100, 27), detail=0)),
        image_metrics_bgr(render_sample((222, 240, 255), (54, 98, 215), detail=3)),
        image_metrics_bgr(render_sample((237, 249, 228), (89, 109, 20), detail=5)),
    ]
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 490" '
        'role="img" aria-labelledby="demo-title demo-desc">',
        '<title id="demo-title">Synthetic avatar image feature extraction demonstration</title>',
        '<desc id="demo-desc">Three original illustrated avatar designs and numeric OpenCV pixel '
        'statistics calculated from independent synthetic raster samples.</desc>',
        '<rect width="980" height="490" fill="#f8fafc"/>',
        '<text x="36" y="44" font-size="24" font-weight="700" fill="#16233d">Avatar Vision · feature extraction</text>',
        '<text x="36" y="71" font-size="13" fill="#49617d">Original illustrations; no research images, people or participant data</text>',
    ]
    for idx, ((name, bg, garment, skin, line), m) in enumerate(zip(PALETTES, metrics, strict=True)):
        x = 36 + idx * 316
        pieces += [
            f'<rect x="{x}" y="93" width="294" height="352" rx="14" fill="white" stroke="#d4deea"/>',
            f'<rect x="{x+16}" y="110" width="262" height="194" rx="10" fill="{bg}"/>',
            f'<rect x="{x+43}" y="245" width="209" height="59" rx="16" fill="{garment}"/>',
            f'<circle cx="{x+147}" cy="192" r="65" fill="{skin}" stroke="{line}" stroke-width="4"/>',
            f'<circle cx="{x+124}" cy="188" r="6" fill="{line}"/>',
            f'<circle cx="{x+170}" cy="188" r="6" fill="{line}"/>',
            f'<path d="M {x+121} 218 Q {x+147} 235 {x+173} 218" stroke="{line}" fill="none" stroke-width="5" stroke-linecap="round"/>',
            f'<text x="{x+18}" y="330" font-size="16" font-weight="700" fill="#16233d">{name}</text>',
            f'<text x="{x+18}" y="358" font-size="13" fill="#385271">Saturation: {m["mean_saturation_0_255"]:.1f} / 255</text>',
            f'<text x="{x+18}" y="380" font-size="13" fill="#385271">Edge density: {m["edge_density"]:.3f}</text>',
            f'<text x="{x+18}" y="402" font-size="13" fill="#385271">Entropy: {m["entropy_bits"]:.2f} bits</text>',
            f'<text x="{x+18}" y="425" font-size="11" fill="#64748b">CV measures are synthetic-raster proxies</text>',
        ]
    pieces += [
        '<text x="36" y="473" font-size="12" fill="#64748b">Measured values come from '
        'programmatic BGR raster sketches, not from the SVG illustration pixels.</text>',
        '</svg>',
        '',
    ]
    return '\n'.join(pieces)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected = _xml()
    ET.fromstring(expected)
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding='utf-8') != expected:
            raise SystemExit('Synthetic demo is missing or stale; regenerate it')
        print('PASS: synthetic illustration and calculated values are current')
    else:
        TARGET.write_text(expected, encoding='utf-8')
        print(f'Wrote {TARGET.relative_to(ROOT)} (no restricted images)')


if __name__ == '__main__':
    main()
