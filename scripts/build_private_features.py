#!/usr/bin/env python3
"""Private-only participant aggregation. NEVER write to the public repository."""
import argparse,json
from pathlib import Path
import pandas as pd
from avatar_vision.aggregate import join_participant_features

p=argparse.ArgumentParser()
for k in ('catalog','mapping','participants','output'):p.add_argument('--'+k,required=True)
a=p.parse_args()
out=Path(a.output).resolve()
if not any(part in ('private','restricted') for part in out.parts):
    p.error('write output into a folder literally named private or restricted, outside the public checkout')
merged,report=join_participant_features(pd.read_csv(a.mapping, dtype={"Version.ID":"string", "User.ID":"string"}),pd.read_csv(a.catalog),pd.read_csv(a.participants, dtype={"Version.ID":"string", "User.ID":"string"}))
out.parent.mkdir(parents=True,exist_ok=True)
merged.to_csv(out,index=False)
print(json.dumps(report,indent=2))
