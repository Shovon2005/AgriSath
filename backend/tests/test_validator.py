"""
Unit tests for input validator.
"""

import pytest
from agrisathi.core.validator import validate_farm_input, normalize_categorical
from agrisathi.core.schemas import (
    canonical_soil_type,
    canonical_growth_stage,
    canonical_water_source,
)
from agrisathi.core.exceptions import ValidationError


def test_validate_valid_payload(valid_farm_payload):
    result = validate_farm_input(valid_farm_payload)
    assert result["N"] == 90.0
    assert result["soil_type"] == 2  # Loamy -> code 2
    assert result["soil_type_label"] == "Loamy"
    assert result["growth_stage"] == 2  # Vegetative -> code 2
    assert result["growth_stage_label"] == "Vegetative"
    assert result["water_source_type"] == 1  # Groundwater -> code 1
    assert result["water_source_type_label"] == "Groundwater"


def test_validate_missing_field(valid_farm_payload):
    del valid_farm_payload["temperature"]
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "temperature" in exc_info.value.details


def test_validate_out_of_bounds_value(valid_farm_payload):
    valid_farm_payload["ph"] = 15.5  # Max pH is 14.0
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "ph" in exc_info.value.details


def test_validate_invalid_categorical(valid_farm_payload):
    valid_farm_payload["soil_type"] = "UnknownSoil"
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "soil_type" in exc_info.value.details


def test_normalize_categorical_variants():
    # Codes, floats, and text
    assert normalize_categorical("soil_type", "Clay") == (1, "Clay")
    assert normalize_categorical("soil_type", 1) == (1, "Clay")
    assert normalize_categorical("soil_type", 1.0) == (1, "Clay")
    assert normalize_categorical("soil_type", "1.0") == (1, "Clay")
    assert normalize_categorical("soil_type", "sandy") == (3, "Sandy")
    assert normalize_categorical("growth_stage", "Maturity") == (4, "Maturity")
    assert normalize_categorical("growth_stage", 4) == (4, "Maturity")
    assert normalize_categorical("growth_stage", 4.0) == (4, "Maturity")
    assert normalize_categorical("water_source_type", "River") == (4, "River")
    assert normalize_categorical("water_source_type", 4) == (4, "River")
    assert normalize_categorical("water_source_type", "4.0") == (4, "River")


def test_canonical_resolvers():
    assert canonical_soil_type("1.0") == "Clay"
    assert canonical_soil_type(1) == "Clay"
    assert canonical_soil_type("clay") == "Clay"
    assert canonical_soil_type(3) == "Sandy"
    assert canonical_growth_stage(4) == "Maturity"
    assert canonical_growth_stage("maturity") == "Maturity"
    assert canonical_water_source(4) == "River"
    assert canonical_water_source("river") == "River"


def test_validate_allow_defaults(valid_farm_payload):
    del valid_farm_payload["temperature"]
    del valid_farm_payload["co2_concentration"]
    res = validate_farm_input(valid_farm_payload, allow_defaults=True)
    assert res["temperature"] == 25.0
    assert res["co2_concentration"] == 400.0


def test_non_dict_payload():
    with pytest.raises(ValidationError):
        validate_farm_input("not a dict")


def test_validate_rejects_nan_and_inf(valid_farm_payload):
    # Reject float NaN
    valid_farm_payload["ph"] = float("nan")
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "ph" in exc_info.value.details
    assert "finite real number" in exc_info.value.details["ph"]

    # Reject string 'nan'
    valid_farm_payload["ph"] = "nan"
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "ph" in exc_info.value.details

    # Reject float inf
    valid_farm_payload["ph"] = float("inf")
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "ph" in exc_info.value.details


def test_validate_rejects_boolean_values(valid_farm_payload):
    # Reject boolean for numeric feature
    valid_farm_payload["ph"] = True
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "ph" in exc_info.value.details
    assert "not boolean" in exc_info.value.details["ph"]

    # Reject boolean for categorical feature
    valid_farm_payload["ph"] = 6.5
    valid_farm_payload["soil_type"] = False
    with pytest.raises(ValidationError) as exc_info:
        validate_farm_input(valid_farm_payload)
    assert "soil_type" in exc_info.value.details

