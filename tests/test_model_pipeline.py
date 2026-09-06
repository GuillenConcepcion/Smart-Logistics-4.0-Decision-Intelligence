import pytest
import os
import pandas as pd
from src.models.predict import DelayPredictor

@pytest.fixture
def predictor():
    model_path = "models/best_delay_model.pkl"
    if not os.path.exists(model_path):
        pytest.skip(f"Modelo {model_path} no encontrado. Ejecute train.py primero.")
    return DelayPredictor(model_path=model_path)

@pytest.fixture
def sample_feature_vector():
    return {
        "speed_kmh": 40.0,
        "distance_remaining_km": 50.0,
        "scheduled_eta_minutes": 60,
        "weather_severity_num": 0.35,
        "traffic_density_num": 0.4,
        "estimated_real_min": 75.0,
        "eta_urgency_ratio": 1.25,
        "expected_delay_min": 15.0,
        "environmental_risk_index": 0.38,
        "cargo_temp_celsius": 4.5
    }

def test_single_prediction_range(predictor, sample_feature_vector):
    p = predictor.predict_event(sample_feature_vector)
    assert isinstance(p, float)
    assert 0.0 <= p <= 1.0

def test_batch_prediction_shape(predictor, sample_feature_vector):
    df_in = pd.DataFrame([sample_feature_vector, sample_feature_vector])
    df_out = predictor.predict_batch(df_in)
    assert "delay_probability" in df_out.columns
    assert len(df_out) == 2
    assert (df_out["delay_probability"] >= 0.0).all()
    assert (df_out["delay_probability"] <= 1.0).all()
