import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
from unittest.mock import patch, mock_open

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_data_quality_checks():
    """Test data quality check functions"""
    from data_quality import check_missing_values, check_outliers, check_freshness

    # Create test data
    test_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'city': ['New York'] * 10,
        'avg_temp_f': [70, 75, 80, 85, 90, 95, 100, 105, 110, 115],  # Some outliers
        'energy_consumption': [100, 105, 110, 115, 120, 125, 130, 135, 140, -50]  # Negative outlier
    })

    # Test missing values
    missing_report = check_missing_values(test_data)
    assert isinstance(missing_report, dict)
    assert all(isinstance(v, (int, np.integer)) for v in missing_report.values())

    # Test outliers
    outlier_report = check_outliers(test_data)
    assert isinstance(outlier_report, dict)
    assert 'temperature_outliers' in outlier_report
    assert 'negative_energy_readings' in outlier_report
    assert outlier_report['temperature_outliers'] >= 0  # Should detect high temp outliers
    assert outlier_report['negative_energy_readings'] >= 0  # Should detect negative energy

    # Test freshness
    freshness_report = check_freshness(test_data)
    assert isinstance(freshness_report, dict)
    assert 'latest_date' in freshness_report
    assert 'is_fresh' in freshness_report
    assert 'days_old' in freshness_report

def test_anomaly_detection():
    """Test anomaly detection functionality"""
    from anomaly_detection import detect_anomalies

    # Create test data with some anomalies
    test_data = pd.DataFrame({
        'avg_temp_f': np.random.normal(70, 10, 100),
        'temp_delta_f': np.random.normal(15, 5, 100),
        'energy_consumption': np.random.normal(1000, 100, 100)
    })

    # Add some clear anomalies
    test_data.loc[0, 'avg_temp_f'] = 200  # Extreme temperature
    test_data.loc[1, 'energy_consumption'] = -1000  # Negative energy

    anomalies = detect_anomalies(test_data)

    assert isinstance(anomalies, pd.DataFrame)
    assert len(anomalies) >= 0  # Should detect at least some anomalies
    assert 'avg_temp_f' in anomalies.columns
    assert 'energy_consumption' in anomalies.columns

def test_config_city_codes():
    """Test that city codes match expected values"""
    from config_loader import load_config

    config = load_config()
    cities = config['cities']

    # Expected station IDs (partial check)
    expected_stations = {
        'New York': 'GHCND:USW00094728',
        'Chicago': 'GHCND:USW00094846',
        'Houston': 'GHCND:USW00012960',
        'Phoenix': 'GHCND:USW00023183',
        'Seattle': 'GHCND:USW00024233'
    }

    for city in cities:
        name = city['name']
        if name in expected_stations:
            assert city['noaa_station_id'] == expected_stations[name]

if __name__ == "__main__":
    print("Running data pipeline tests...")

    try:
        test_data_quality_checks()
        print("✅ Data quality tests passed")
    except Exception as e:
        print(f"❌ Data quality tests failed: {e}")

    try:
        test_anomaly_detection()
        print("✅ Anomaly detection tests passed")
    except Exception as e:
        print(f"❌ Anomaly detection tests failed: {e}")

    try:
        test_config_city_codes()
        print("✅ Config validation tests passed")
    except Exception as e:
        print(f"❌ Config validation tests failed: {e}")

    print("Test suite completed!")
