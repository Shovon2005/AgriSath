"""
Tests for root backward-compatibility wrappers: recommendation.py and explain.py.
Ensures legacy APIs remain fully operational with existing signatures.
"""

import pandas as pd
from recommendation import (
    soil_assessment,
    irrigation_recommendation,
    fertilizer_recommendation,
    risk_assessment,
)
from explain import clean_feature_name, explain_prediction


def test_legacy_recommendation_wrappers(valid_farm_payload):
    # 1. Soil Assessment
    soil_res = soil_assessment(valid_farm_payload)
    assert isinstance(soil_res, dict)
    assert "status" in soil_res
    assert "issues" in soil_res
    assert isinstance(soil_res["issues"], list)

    # 2. Irrigation Recommendation
    irrig_res = irrigation_recommendation(valid_farm_payload)
    assert isinstance(irrig_res, dict)
    assert "priority" in irrig_res
    assert "message" in irrig_res

    # 3. Fertilizer Recommendation
    fert_res = fertilizer_recommendation(valid_farm_payload)
    assert isinstance(fert_res, list)
    assert len(fert_res) > 0

    # 4. Risk Assessment
    risk_res = risk_assessment(valid_farm_payload)
    assert isinstance(risk_res, list)
    assert len(risk_res) > 0


def test_legacy_explain_wrappers(valid_farm_payload):
    # 1. Feature Name Cleaner
    clean_lbl = clean_feature_name("numeric__N")
    assert "Nitrogen" in clean_lbl

    # 2. Explain Prediction
    res = explain_prediction(valid_farm_payload)
    assert isinstance(res, dict)
    assert "prediction" in res
    assert isinstance(res["prediction"], str)
    assert "probabilities" in res
    assert isinstance(res["probabilities"], pd.DataFrame)
    assert "crop" in res["probabilities"].columns
    assert "probability" in res["probabilities"].columns

    assert "important_features" in res
    assert isinstance(res["important_features"], pd.DataFrame)
    assert "feature" in res["important_features"].columns
    assert "importance" in res["important_features"].columns
