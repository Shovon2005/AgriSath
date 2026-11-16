"""
Unit tests for extended domain schemas, season mappings, and farm area conversions.
"""

import pytest
from agrisathi.core.schemas import (
    Season,
    canonical_season,
    area_to_hectares,
    EXTENDED_FEATURE_DEFINITIONS,
    ALL_FEATURE_MAP,
)
from agrisathi.core.validator import validate_farm_input


def test_season_normalization():
    assert canonical_season("kharif") == "Kharif"
    assert canonical_season("Monsoon season") == "Kharif"
    assert canonical_season("rabi") == "Rabi"
    assert canonical_season("Winter") == "Rabi"
    assert canonical_season("zaid") == "Zaid"
    assert canonical_season("Summer") == "Zaid"
    assert canonical_season("annual") == "Whole Year"
    assert canonical_season(None) == "Whole Year"


def test_area_to_hectares():
    assert area_to_hectares(1.0, "hectare") == 1.0
    # 1 acre = 0.404686 ha -> approx 0.4047 ha
    assert pytest.approx(area_to_hectares(2.47105, "acre"), 0.01) == 1.0
    assert area_to_hectares(10.0, "acres") > 0.0
    assert area_to_hectares("invalid", "hectare") == 1.0
    assert area_to_hectares(-5.0, "hectare") == 0.01


def test_validator_with_extended_parameters(valid_farm_payload):
    payload = valid_farm_payload.copy()
    payload["farm_area"] = 5.0
    payload["farm_area_unit"] = "acre"
    payload["electrical_conductivity"] = 1.2
    payload["organic_carbon"] = 0.8
    payload["location"] = "Punjab, India"
    payload["season"] = "Rabi"
    payload["expected_rainfall_24h"] = 15.0

    sanitized = validate_farm_input(payload)

    assert sanitized["farm_area"] == 5.0
    assert sanitized["farm_area_unit"] == "acre"
    assert pytest.approx(sanitized["farm_area_ha"], 0.01) == 5.0 * 0.404686
    assert sanitized["electrical_conductivity"] == 1.2
    assert sanitized["organic_carbon"] == 0.8
    assert sanitized["location"] == "Punjab, India"
    assert sanitized["season"] == "Rabi"
    assert sanitized["expected_rainfall_24h"] == 15.0


def test_validator_extended_fallbacks(valid_farm_payload):
    # Payload without any extended fields should fallback gracefully
    sanitized = validate_farm_input(valid_farm_payload)
    assert sanitized["farm_area"] == 1.0
    assert sanitized["farm_area_ha"] == 1.0
    assert sanitized["electrical_conductivity"] == 0.6
    # Organic carbon derived from organic_matter
    expected_oc = round(sanitized["organic_matter"] / 1.724, 2)
    assert sanitized["organic_carbon"] == expected_oc
    assert sanitized["location"] == "Local Farm"
    assert sanitized["season"] == "Whole Year"
    assert sanitized["expected_rainfall_24h"] == 0.0


def test_validator_optional_soil_moisture(valid_farm_payload):
    # Soil moisture is optional; omitting or passing empty string should default to 30.0%
    payload_no_sm = valid_farm_payload.copy()
    del payload_no_sm["soil_moisture"]
    sanitized1 = validate_farm_input(payload_no_sm)
    assert sanitized1["soil_moisture"] == 30.0

    payload_empty_sm = valid_farm_payload.copy()
    payload_empty_sm["soil_moisture"] = ""
    sanitized2 = validate_farm_input(payload_empty_sm)
    assert sanitized2["soil_moisture"] == 30.0


def test_validator_oc_derives_om(valid_farm_payload):
    # Providing organic_carbon but omitting organic_matter should derive OM = OC * 1.724
    payload = valid_farm_payload.copy()
    del payload["organic_matter"]
    payload["organic_carbon"] = 0.85
    sanitized = validate_farm_input(payload)
    assert sanitized["organic_carbon"] == 0.85
    assert sanitized["organic_matter"] == round(0.85 * 1.724, 2)
