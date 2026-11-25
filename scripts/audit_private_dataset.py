#!/usr/bin/env python3
"""Validate rights-cleared original files; print identifier-free aggregate JSON."""
import argparse,json
import pandas as pd
from avatar_vision.audit import audit_mapping

p=argparse.ArgumentParser()
p.add_argument('--catalog',required=True)
p.add_argument('--mapping',required=True)
p.add_argument('--participants')
a=p.parse_args()
report=audit_mapping(pd.read_csv(a.mapping, dtype={"Version.ID":"string", "User.ID":"string"}),pd.read_csv(a.catalog),pd.read_csv(a.participants, dtype={"Version.ID":"string", "User.ID":"string"}) if a.participants else None)
print(json.dumps(report,indent=2,sort_keys=True))
if not report['ready_for_inference']:
    raise SystemExit('AUDIT FLAGGED: review unresolved session/selection evidence before inference')
