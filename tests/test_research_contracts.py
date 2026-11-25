import pandas as pd
import pytest
from avatar_vision.audit import audit_mapping, validate_catalog, DataContractError, require_publication_safe_columns
from avatar_vision.aggregate import join_participant_features
from avatar_vision.features import parse_filename, image_metrics_bgr


def fixture_data():
    catalog=pd.DataFrame({
      'avatar_name':['humanoid_female_happy_blue_formal_nologo_v1','humanoid_male_neutral_red_informal_okstatelogo_v2'],
      'avatar_gender':['female','male'], 'mean_saturation_0_255':[32.,72.],
    })
    mapping=pd.DataFrame({
      'Version.ID':['v1r','v2r','v4r'],'User.ID':[1,2,3],
      'avatar_1':[catalog.avatar_name[0],catalog.avatar_name[1],'No avatar'],
      'avatar_2':[catalog.avatar_name[1],None,None],
      'avatar_3':[None,None,None],
      'final_avatar_name_source':[catalog.avatar_name[1],catalog.avatar_name[1],None],
      'mapping_status_source':['Matched','Matched','Matched'],
    })
    participants=pd.DataFrame({'Version.ID':['v1r','v2r','v4r'],'User.ID':[1,2,3],
                               'version_enc':['create_av','human_av','no_av'],'serv_qual':[4.,3.,2.]})
    return catalog,mapping,participants


def test_mapping_and_participant_coverage():
    catalog,mapping,participants=fixture_data()
    result=audit_mapping(mapping,catalog,participants)
    assert result['ready_for_inference'] is True
    assert result['participant_join']['common_keys']==3
    assert result['avatar_references']['avatar_1']['referenced']==2
    assert result['condition_counts']=={'create_av':1,'human_av':1,'no_av':1}


def test_outstanding_review_blocks_ready_flag():
    catalog,mapping,participants=fixture_data()
    mapping.loc[1,'mapping_status_source']='Matched - Review'
    result=audit_mapping(mapping,catalog,participants)
    assert result['mapping_review_required']==1
    assert not result['ready_for_inference']


def test_unresolved_catalog_reference_is_reported_not_fabricated():
    catalog,mapping,participants=fixture_data()
    mapping.loc[0,'avatar_1']='unrecognized_avatar'
    out=audit_mapping(mapping,catalog,participants)
    assert out['avatar_references']['avatar_1']['not_in_catalog']==1
    assert not out['ready_for_inference']


def test_duplicate_keys_rejected():
    catalog,mapping,participants=fixture_data()
    mapping.loc[1,'User.ID']=1
    mapping.loc[1,'Version.ID']='v1r'
    with pytest.raises(DataContractError,match='duplicated'):
        audit_mapping(mapping,catalog,participants)


def test_duplicate_catalog_name_rejected():
    catalog,_,_=fixture_data()
    catalog.loc[1,'avatar_name']=catalog.loc[0,'avatar_name']
    with pytest.raises(DataContractError,match='duplicate'):
        validate_catalog(catalog)


def test_join_keeps_all_conditions_and_absent_avatar_nulls():
    catalog,mapping,participants=fixture_data()
    df,report=join_participant_features(mapping,catalog,participants)
    assert len(df)==3
    assert report['feature_coverage']=={'first':2,'second':1,'third':0,'final':2}
    row=df.loc[df['version_enc']=='no_av'].iloc[0]
    assert not bool(row['first_catalog_match'])
    assert pd.isna(row['first_mean_saturation_0_255'])
    assert df.loc[df['version_enc']=='human_av','first_avatar_gender'].iloc[0]=='male'


def test_research_identifiers_cannot_be_public_fixtures():
    _,mapping,_=fixture_data()
    with pytest.raises(DataContractError,match='participant/session'):
        require_publication_safe_columns(mapping)


def test_design_labels_are_not_claimed_to_be_visual_measurements():
    features=parse_filename('avatar_humanoid_female_happy_blue_formal_nologo_v1.jpeg')
    assert features['design_gender']=='female'
    assert features['avatar_name']=='humanoid_female_happy_blue_formal_nologo_v1'
    assert 'eye_count_detected_0_2' not in features
    with pytest.raises(ValueError):
        parse_filename('female_blue.jpeg')


def test_image_metrics_pixel_level():
    np=pytest.importorskip('numpy')
    pytest.importorskip('cv2')
    img=np.zeros((12,16,3),dtype=np.uint8)
    img[:,:,0]=255
    data=image_metrics_bgr(img)
    assert data['image_width_px']==16
    assert data['image_height_px']==12
    assert data['mean_saturation_0_255']>200
    assert 0<=data['symmetry_pixel_proxy_0_1']<=1


def test_invalid_image_rejected():
    np=pytest.importorskip('numpy')
    pytest.importorskip('cv2')
    with pytest.raises(ValueError,match='expected BGR'):
        image_metrics_bgr(np.zeros((2,2),dtype=np.uint8))


def test_cannot_mark_ready_without_participant_join():
    catalog,mapping,_=fixture_data()
    assert not audit_mapping(mapping,catalog)['ready_for_inference']


def test_participant_key_mismatch_detected():
    catalog,mapping,participants=fixture_data()
    participants.loc[2,'User.ID']=99
    result=audit_mapping(mapping,catalog,participants)
    assert result['participant_join']['mapping_unmatched']==1
    assert result['participant_join']['participant_unmatched']==1
    assert not result['ready_for_inference']


def test_mapping_status_is_preserved_for_private_qc():
    catalog,mapping,participants=fixture_data()
    mapping.loc[1,'mapping_status_source']='Matched - Review'
    joined,_=join_participant_features(mapping,catalog,participants)
    assert joined.loc[joined['User.ID']==2,'mapping_status_source'].iloc[0]=='Matched - Review'


def test_no_avatar_condition_cannot_carry_measured_avatar_reference():
    catalog,mapping,participants=fixture_data()
    mapping.loc[2,'avatar_1']=catalog.loc[0,'avatar_name']
    result=audit_mapping(mapping,catalog,participants)
    assert result['no_avatar_condition_conflicts']==1
    assert not result['ready_for_inference']


def test_condition_coverage_is_explicit_without_ids():
    catalog,mapping,participants=fixture_data()
    report=audit_mapping(mapping,catalog,participants)
    assert report['condition_avatar_coverage']['no_av']['avatar_1']=={'actual_avatar':0,'sentinel':1,'missing':0}
    assert report['condition_avatar_coverage']['create_av']['avatar_2']['actual_avatar']==1
    assert 'User.ID' not in str(report)


def test_unvalidated_appearance_proxies_are_excluded_from_new_joins():
    catalog,mapping,participants=fixture_data()
    catalog['eyelashes_present_visual_proxy']=[1,0]
    catalog['skin_tone_fraction_proxy']=[.2,.7]
    joined,report=join_participant_features(mapping,catalog,participants)
    assert 'first_eyelashes_present_visual_proxy' not in joined
    assert 'first_skin_tone_fraction_proxy' not in joined
    assert 'eyelashes_present_visual_proxy' in report['excluded_unapproved_catalog_columns']
