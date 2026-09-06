import pytest
from src.processing.feature_store import FeatureStore

@pytest.fixture
def feature_store():
    return FeatureStore()

def test_enrich_event_calculated_features(feature_store):
    event = {
        "shipment_id": "SH-2026-1001",
        "speed_kmh": 60.0,
        "distance_remaining_km": 60.0,
        "scheduled_eta_minutes": 60,
        "traffic_density": "LOW",
        "weather_condition": "CLEAR"
    }
    enriched = feature_store.enrich_event(event)
    
    # 60 km a 60 km/h = 60 minutos
    assert enriched["estimated_real_min"] == 60.0
    assert enriched["eta_urgency_ratio"] == 1.0
    assert enriched["expected_delay_min"] == 0.0
    assert enriched["weather_severity_num"] == 0.0
    assert enriched["traffic_density_num"] == 0.1
    assert "environmental_risk_index" in enriched

def test_enrich_event_delay_urgency(feature_store):
    event = {
        "shipment_id": "SH-2026-1002",
        "speed_kmh": 30.0,
        "distance_remaining_km": 60.0,
        "scheduled_eta_minutes": 60,
        "traffic_density": "SEVERE_CONGESTION",
        "weather_condition": "SNOW"
    }
    enriched = feature_store.enrich_event(event)
    
    # 60 km a 30 km/h = 120 min (2x más del tiempo programado)
    assert enriched["estimated_real_min"] == 120.0
    assert enriched["eta_urgency_ratio"] == 2.0
    assert enriched["expected_delay_min"] == 60.0
    assert enriched["weather_severity_num"] == 1.0
    assert enriched["traffic_density_num"] == 1.0
    assert enriched["environmental_risk_index"] == 1.0

def test_enrich_event_zero_speed_protection(feature_store):
    event = {
        "shipment_id": "SH-2026-1003",
        "speed_kmh": 0.0,
        "distance_remaining_km": 10.0,
        "scheduled_eta_minutes": 0
    }
    # No debe lanzar ZeroDivisionError
    enriched = feature_store.enrich_event(event)
    assert enriched["estimated_real_min"] > 0
    assert enriched["eta_urgency_ratio"] > 0
