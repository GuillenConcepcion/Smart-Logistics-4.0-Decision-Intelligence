"""
Módulo de Inferencia en Tiempo Real (Predict Engine)
Carga el modelo XGBoost y calcula probabilidades de retraso para eventos telemáticos.
"""
import os
import sys
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import joblib
import pandas as pd
from typing import Dict, Any
from src.models.ensemble import LogisticsSuperLearner

class DelayPredictor:
    def __init__(self, model_path: str = "models/best_delay_model.pkl"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No se encontró el artefacto del modelo en {model_path}. Ejecute src/models/train.py primero.")
            
        artifact = joblib.load(model_path)
        self.model = artifact["model"]
        self.feature_cols = artifact["feature_cols"]
        self.metrics = artifact.get("metrics", {})

    def predict_event(self, enriched_event: Dict[str, Any]) -> float:
        """
        Calcula la probabilidad P(Retraso) para un evento individual enriquecido.
        """
        df_single = pd.DataFrame([enriched_event])
        X = df_single[self.feature_cols]
        proba = self.model.predict_proba(X)[0, 1]
        return float(proba)

    def predict_batch(self, df_gold: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula probabilidades para un DataFrame batch/streaming.
        """
        df_out = df_gold.copy()
        X = df_out[self.feature_cols]
        df_out["delay_probability"] = self.model.predict_proba(X)[:, 1]
        return df_out

if __name__ == "__main__":
    predictor = DelayPredictor()
    sample_enriched = {
        "speed_kmh": 22.5,
        "distance_remaining_km": 110.0,
        "scheduled_eta_minutes": 80,
        "weather_severity_num": 0.85,
        "traffic_density_num": 1.0,
        "estimated_real_min": 293.3,
        "eta_urgency_ratio": 3.66,
        "expected_delay_min": 213.3,
        "environmental_risk_index": 0.94,
        "cargo_temp_celsius": 4.1
    }
    p = predictor.predict_event(sample_enriched)
    print(f"Probabilidad de Retraso Calculada P(Retraso): {p:.4f}")
