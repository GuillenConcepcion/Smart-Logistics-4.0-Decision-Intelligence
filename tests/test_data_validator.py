import pytest
from src.processing.data_validator import DataValidator

@pytest.fixture
def validator():
    return DataValidator()

@pytest.fixture
def valid_telemetry_event():
    return {
        "shipment_id": "SH-2026-9001",
        "vehicle_id": "VH-105",
        "timestamp": "2026-09-05T18:30:00Z",
        "latitude": 43.6150,
        "longitude": -116.2023,
        "speed_kmh": 50.0,
        "traffic_density": "MODERATE",
        "weather_condition": "CLEAR",
        "cargo_temp_celsius": 4.0,
        "distance_remaining_km": 40.0,
        "scheduled_eta_minutes": 60
    }

def test_valid_telemetry_event(validator, valid_telemetry_event):
    is_valid, data, err = validator.validate_event(valid_telemetry_event)
    assert is_valid is True
    assert err is None
    assert data["shipment_id"] == "SH-2026-9001"
    assert data["speed_kmh"] == 50.0

def test_reject_outlier_speed(validator, valid_telemetry_event):
    bad_event = valid_telemetry_event.copy()
    bad_event["speed_kmh"] = 250.0  # Supera límite físico
    is_valid, data, err = validator.validate_event(bad_event)
    assert is_valid is False
    assert err is not None

def test_reject_invalid_coordinates(validator, valid_telemetry_event):
    bad_event = valid_telemetry_event.copy()
    bad_event["latitude"] = 10.0  # Fuera de Treasure Valley
    is_valid, data, err = validator.validate_event(bad_event)
    assert is_valid is False
    assert "latitude" in err

def test_reject_invalid_weather(validator, valid_telemetry_event):
    bad_event = valid_telemetry_event.copy()
    bad_event["weather_condition"] = "HURRICANE_CATEGORY_5"
    is_valid, data, err = validator.validate_event(bad_event)
    assert is_valid is False

def test_validate_batch(validator, valid_telemetry_event):
    bad_event = valid_telemetry_event.copy()
    bad_event["speed_kmh"] = -10.0
    
    events = [valid_telemetry_event, bad_event]
    valid_list, rejected_list = validator.validate_batch(events)
    assert len(valid_list) == 1
    assert len(rejected_list) == 1
