import pandas as pd
import pytest
from avatar_vision.quality import assert_catalog_quality, inspect_catalog_metrics
from avatar_vision.audit import DataContractError


def test_valid_catalog_measurement_ranges():
    df=pd.DataFrame({'avatar_name':['a','b'],'mean_saturation_0_255':[0,255],
                     'edge_density':[0,.25],'entropy_bits':[2,8]})
    report=assert_catalog_quality(df)
    assert report['invalid_measurement_columns']==[]


def test_out_of_range_measurements_rejected():
    df=pd.DataFrame({'avatar_name':['a'],'mean_brightness_0_255':[300]})
    assert inspect_catalog_metrics(df)['measurement_checks']['mean_brightness_0_255']['invalid_range']==1
    with pytest.raises(DataContractError,match='mean_brightness'):
        assert_catalog_quality(df)


def test_missing_numeric_measurement_rejected():
    df=pd.DataFrame({'avatar_name':['a'],'hue_concentration_0_1':['unknown']})
    with pytest.raises(DataContractError):
        assert_catalog_quality(df)
