"""
Shared pytest fixtures for AgriSathi testing.
"""

import pytest
from agrisathi.web.app import create_app


@pytest.fixture
def client():
    """Flask test client fixture."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client



@pytest.fixture
def valid_farm_payload():
    """Standard valid input dictionary matching typical Rice conditions."""
    return {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25.5,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 200.0,
        "soil_moisture": 30.0,
        "soil_type": "Loamy",
        "sunlight_exposure": 8.0,
        "wind_speed": 3.5,
        "co2_concentration": 400.0,
        "organic_matter": 4.0,
        "irrigation_frequency": 3,
        "crop_density": 15.0,
        "pest_pressure": 20.0,
        "fertilizer_usage": 100.0,
        "growth_stage": "Vegetative",
        "urban_area_proximity": 15.0,
        "water_source_type": "Groundwater",
        "frost_risk": 5.0,
        "water_usage_efficiency": 2.5,
    }


@pytest.fixture
def arid_farm_payload():
    """Arid / low-moisture farm conditions for chickpea or mothbeans."""
    return {
        "N": 40,
        "P": 60,
        "K": 80,
        "temperature": 18.0,
        "humidity": 25.0,
        "ph": 7.2,
        "rainfall": 40.0,
        "soil_moisture": 12.0,
        "soil_type": "Sandy",
        "sunlight_exposure": 10.0,
        "wind_speed": 5.0,
        "co2_concentration": 390.0,
        "organic_matter": 2.0,
        "irrigation_frequency": 1,
        "crop_density": 10.0,
        "pest_pressure": 15.0,
        "fertilizer_usage": 60.0,
        "growth_stage": "Seedling",
        "urban_area_proximity": 30.0,
        "water_source_type": "Canal",
        "frost_risk": 2.0,
        "water_usage_efficiency": 3.8,
    }
