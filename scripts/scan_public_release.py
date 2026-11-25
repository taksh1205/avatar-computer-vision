#!/usr/bin/env python3
"""Fail closed when a public checkout accidentally includes research data or images."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IGNORE={'.git','.venv','__pycache__','.pytest_cache','build','dist','.ipynb_checkpoints'}
DANGEROUS={'.csv','.xlsx','.xls','.parquet','.sav','.pkl','.rds','.RData','.jpeg','.jpg','.png','.mp4','.mov','.gif','.webp','.tiff','.tif','.db','.sqlite','.tsv','.jsonl','.ndjson','.zip','.7z','.tar','.gz'}
COLLECTED=[]
for file in ROOT.rglob('*'):
    if any(parent.name in IGNORE for parent in file.parents) or not file.is_file():
        continue
    if file.suffix.lower() in {x.lower() for x in DANGEROUS}:
        COLLECTED.append(str(file.relative_to(ROOT)))
# SVG is source text, permitted only for our newly drawn synthetic illustration.
SVG_ALLOWED = 'docs/assets/synthetic_feature_demo.svg'
for file in ROOT.rglob('*.svg'):
    if any(parent.name in IGNORE for parent in file.parents) or not file.is_file():
        continue
    relative = file.relative_to(ROOT).as_posix()
    if relative != SVG_ALLOWED:
        COLLECTED.append(relative + ' (unreviewed SVG)')
        continue
    content = file.read_text(encoding='utf-8').casefold()
    if any(token in content for token in ('<image', '<script', '<foreignobject',
                                           'data:', 'href=', 'xlink:href=', '<iframe')):
        COLLECTED.append(relative + ' (external/embedded SVG content)')
if COLLECTED:
    print('BLOCKED: nonpublic research assets detected:')
    for f in sorted(COLLECTED):print(' - '+f)
    raise SystemExit(1)
print('PASS: no dataset or original image/video assets in public tree')
