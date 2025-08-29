import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_loader import load_config, get_api_keys
from logger import get_logger

def test_config_loading():
    """Test that configuration loads correctly"""
    config = load_config()

    # Check cities configuration
    assert "cities" in config
    assert len(config["cities"]) == 5

    # Check required city fields
    required_fields = ["name", "state", "noaa_station_id", "eia_region_code"]
    for city in config["cities"]:
        for field in required_fields:
            assert field in city, f"Missing {field} for city {city.get('name', 'unknown')}"

    # Check general config
    assert "general" in config
    assert "fetch_days" in config["general"]
    assert "log_level" in config["general"]

def test_api_keys_structure():
    """Test that API keys are loaded (values may be empty for testing)"""
    api_keys = get_api_keys()

    # Check that required keys exist in structure
    assert "NOAA" in api_keys
    assert "EIA" in api_keys

def test_logger_creation():
    """Test that logger can be created"""
    logger = get_logger("test")
    assert logger is not None

    # Test logging doesn't crash
    logger.info("Test log message")

def test_city_data_integrity():
    """Test that city data matches expected values"""
    config = load_config()
    cities = config["cities"]

    # Expected cities and their codes
    expected_cities = {
        "New York": {"state": "New York", "region": "NYIS"},
        "Chicago": {"state": "Illinois", "region": "PJM"},
        "Houston": {"state": "Texas", "region": "ERCO"},
        "Phoenix": {"state": "Arizona", "region": "AZPS"},
        "Seattle": {"state": "Washington", "region": "SCL"}
    }

    for city in cities:
        name = city["name"]
        if name in expected_cities:
            expected = expected_cities[name]
            assert city["state"] == expected["state"]
            assert city["eia_region_code"] == expected["region"]

if __name__ == "__main__":
    # Run basic setup validation
    config = load_config()
    api_keys = get_api_keys()
    logger = get_logger()

    logger.info("Loaded config for %d cities", len(config["cities"]))
    logger.info("NOAA Key loaded: %s", bool(api_keys["NOAA"]))
    logger.info("EIA Key loaded: %s", bool(api_keys["EIA"]))

    print("✅ All basic setup tests passed!")
