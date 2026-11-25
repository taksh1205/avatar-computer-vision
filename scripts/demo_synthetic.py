#!/usr/bin/env python3
"""Public, deterministic demonstration with invented participants, no real research data."""
import json
import pandas as pd
from avatar_vision.audit import audit_mapping
from avatar_vision.aggregate import join_participant_features
from avatar_vision.quality import assert_catalog_quality
from avatar_vision.features import parse_filename,image_metrics_bgr
import numpy as np

names=['humanoid_female_happy_blue_formal_nologo_v1','humanoid_male_neutral_red_informal_okstatelogo_v2']
cat=pd.DataFrame({'avatar_name':names,'avatar_gender':['female','male'],
                  'mean_saturation_0_255':[32.,72.], 'edge_density':[.05,.12]})
mapdf=pd.DataFrame({'Version.ID':['v1r','v2r','v4r'],'User.ID':[111,222,333],
    'avatar_1':[names[0],names[1],'No avatar'],'avatar_2':[names[1],None,None],
    'avatar_3':[None,None,None],
    'final_avatar_name_source':[names[1],names[1],None],
    'mapping_status_source':['Matched']*3})
people=pd.DataFrame({'Version.ID':['v1r','v2r','v4r'],'User.ID':[111,222,333],
                      'version_enc':['create_av','human_av','no_av']})
report=assert_catalog_quality(cat)
joined,coverage=join_participant_features(mapdf,cat,people)
img=np.zeros((16,16,3),dtype=np.uint8);img[:,:,0]=255
result={'synthetic_only':True,'catalog_quality_columns':len(report['measurement_checks']),
        'design_label_example':parse_filename('avatar_'+names[0]+'.jpeg'),
        'image_metrics_example':image_metrics_bgr(img),
        'mapping_summary':audit_mapping(mapdf,cat,people),
        'feature_coverage':coverage['feature_coverage'],
        'joined_rows':int(len(joined))}
print(json.dumps(result,indent=2,sort_keys=True))
