#!/usr/bin/env python3
"""Generate/check a dictionary directly from the public extractor's feature registry."""
from __future__ import annotations

import argparse
from pathlib import Path

from avatar_vision.feature_registry import DESIGN_FACTORS, LEGACY_CATALOG_NOTE, PIXEL_FEATURES

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs' / 'FEATURE_DICTIONARY.md'


def generate() -> str:
    parts = [
        '# Avatar Vision — feature dictionary',
        '',
        'Generated from `src/avatar_vision/feature_registry.py` using '
        '`python scripts/build_feature_dictionary.py`.',
        '',
        '## Image-derived measurements',
        '',
        'All below are deterministic OpenCV statistics on decoded **BGR** images. '
        'They are not learned AI predictions or judgments about a person.',
        '',
        '| Output field | Meaning | Unit / domain | Computation | Interpretation limit |',
        '|---|---|---|---|---|',
    ]
    for name, spec in PIXEL_FEATURES.items():
        parts.append(f'| `{name}` | {spec.meaning} | {spec.unit_or_domain} | {spec.provenance} | {spec.caution} |')
    parts += [
        '', '## Filename-encoded experimental design factors', '',
        'These represent **the avatar design file naming scheme**, not information inferred about participants.',
        '', '| Output field | Meaning | Values / domain | Provenance | Interpretation limit |',
        '|---|---|---|---|---|',
    ]
    for name, spec in DESIGN_FACTORS.items():
        parts.append(f'| `{name}` | {spec.meaning} | {spec.unit_or_domain} | {spec.provenance} | {spec.caution} |')
    parts += [
        '', '## Provenance and measurement controls', '',
        '- Pixel metrics are measured from decoded images; their values depend on resolution, '
        'compression, color handling and crop. Compare groups only after a consistent preprocessing policy.',
        '- Name-derived design labels are provided by the generator and require independent '
        'verification against the original design documentation if used inferentially.',
        '- The 54-column historical exports must not be identified with the ten new pixel measurements.',
        '- Keep missing avatar references as missing. Never convert absence into a zero-valued image.',
        '- Participant joins need reviewed session mappings before inferential analysis.',
        '', '## Historical catalog scope', '', LEGACY_CATALOG_NOTE, '',
    ]
    return '\n'.join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Fail if dictionary is stale')
    args = parser.parse_args()
    expected = generate()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding='utf-8') != expected:
            raise SystemExit('Feature dictionary missing or out of date; rerun generator')
        print('PASS: feature dictionary matches registry')
    else:
        OUTPUT.write_text(expected, encoding='utf-8')
        print(f'Wrote {OUTPUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
