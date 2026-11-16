"""
Unit tests for input validator.
"""

import pytest
from agrisathi.core.validator import validate_farm_input, normalize_categorical
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
    # Codes and text
    assert normalize_categorical("soil_type", "Clay") == (1, "Clay")
    assert normalize_categorical("soil_type", 1) == (1, "Clay")
    assert normalize_categorical("soil_type", "sandy") == (3, "Sandy")
    assert normalize_categorical("growth_stage", "Maturity") == (3, "Flowering")
    assert normalize_categorical("water_source_type", "River") == (3, "Canal")


def test_non_dict_payload():
    with pytest.raises(ValidationError):
        validate_farm_input("not a dict")
