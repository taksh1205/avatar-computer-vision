"""Regression tests for research provenance, publication and inference safety."""
from pathlib import Path
import importlib.util

import pandas as pd
import pytest

from avatar_vision.audit import DataContractError, audit_mapping
from avatar_vision.aggregate import join_participant_features
from avatar_vision.features import image_metrics_bgr, parse_filename
from avatar_vision.feature_registry import PIXEL_FEATURES, DESIGN_FACTORS
from avatar_vision.release_gate import require_inference_ready

from test_research_contracts import fixture_data


def test_dictionary_covers_every_computed_measurement_and_design_factor():
    pytest.importorskip('cv2')
    import numpy as np
    metrics = image_metrics_bgr(np.zeros((12, 16, 3), dtype=np.uint8))
    parsed = parse_filename('avatar_humanoid_female_happy_blue_formal_nologo_v1.png')
    assert set(metrics) == set(PIXEL_FEATURES)
    assert set(DESIGN_FACTORS) == {key for key in parsed if key.startswith('design_')}
    assert all(spec.provenance and spec.caution for spec in PIXEL_FEATURES.values())


def test_unresolved_session_never_enters_inference_even_if_joined():
    catalog, mapping, participants = fixture_data()
    mapping.loc[1, 'mapping_status_source'] = 'Matched - Review'
    joined, report = join_participant_features(mapping, catalog, participants)
    assert len(joined) == 3  # preserved for private QA
    with pytest.raises(DataContractError, match='unresolved'):
        require_inference_ready(joined, report, approved_by_lab=True)


def test_lab_approval_is_separate_from_clean_structural_audit():
    catalog, mapping, participants = fixture_data()
    joined, report = join_participant_features(mapping, catalog, participants)
    assert report['ready_for_inference']
    with pytest.raises(DataContractError, match='lab adjudication'):
        require_inference_ready(joined, report)
    released = require_inference_ready(joined, report, approved_by_lab=True)
    released.loc[:, 'version_enc'] = 'modified'
    assert 'modified' not in set(joined['version_enc'])


def test_revalidated_table_cannot_hide_an_unreviewed_status():
    catalog, mapping, participants = fixture_data()
    joined, report = join_participant_features(mapping, catalog, participants)
    joined.loc[0, 'mapping_status_source'] = 'Unresolved'
    with pytest.raises(DataContractError, match='unreviewed'):
        require_inference_ready(joined, report, approved_by_lab=True)


def test_revalidated_no_avatar_rows_cannot_acquire_image_features():
    catalog, mapping, participants = fixture_data()
    joined, report = join_participant_features(mapping, catalog, participants)
    joined.loc[joined.version_enc == 'no_av', 'first_catalog_match'] = True
    with pytest.raises(DataContractError, match='no-avatar'):
        require_inference_ready(joined, report, approved_by_lab=True)


def test_generated_docs_match_code_registry():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('build_feature_dictionary', root/'scripts'/'build_feature_dictionary.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert (root/'docs'/'FEATURE_DICTIONARY.md').read_text() == module.generate()


def test_synthetic_svg_has_no_embedded_real_image():
    root = Path(__file__).resolve().parents[1]
    contents = (root/'docs'/'assets'/'synthetic_feature_demo.svg').read_text()
    assert '<image' not in contents.casefold()
    assert 'data:image' not in contents.casefold()
    assert 'http://' not in contents.replace('http://www.w3.org/2000/svg','')
    assert 'Synthetic avatar' in contents
