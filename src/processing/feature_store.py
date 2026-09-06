"""
Módulo de Feature Store (Gold Layer)
Transforma datos telemáticos crudos en vectores de características enriquecidos para Machine Learning y Decision Intelligence.
"""
import pandas as pd
import numpy as np
from datetime import datetime

class FeatureStore:
    def __init__(self):
        self.weather_severity_map = {
            "CLEAR": 0.0,
            "FOG": 0.35,
            "RAIN": 0.60,
            "HEAVY_RAIN": 0.85,
            "SNOW": 1.00
        }
        
        self.traffic_density_map = {
            "LOW": 0.1,
            "MODERATE": 0.4,
            "HIGH": 0.7,
            "SEVERE_CONGESTION": 1.0
        }

    def enrich_event(self, raw_event: dict) -> dict:
        """
        Calcula variables derivadas sobre un evento telemático individual.
        """
        enriched = raw_event.copy()
        
        # Mapeos numéricos de severidad
        weather_sev = self.weather_severity_map.get(raw_event.get("weather_condition", "CLEAR"), 0.0)
        traffic_sev = self.traffic_density_map.get(raw_event.get("traffic_density", "LOW"), 0.1)
        
        # Variables compuestas de ingeniería de características
        speed_kmh = raw_event.get("speed_kmh", 50.0)
        dist_remaining = raw_event.get("distance_remaining_km", 50.0)
        scheduled_eta_min = raw_event.get("scheduled_eta_minutes", 60)
        
        # Tiempo estimado real a velocidad actual (horas a minutos)
        estimated_real_min = (dist_remaining / max(speed_kmh, 5.0)) * 60.0
        
        # Ratio de urgencia (si > 1.0, la velocidad actual no alcanza para llegar a tiempo)
        eta_urgency_ratio = estimated_real_min / max(scheduled_eta_min, 1.0)
        
        # Defase esperado en minutos
        expected_delay_min = max(0.0, estimated_real_min - scheduled_eta_min)
        
        # Índice sintético de riesgo ambiental y vial
        environmental_risk_index = round((weather_sev * 0.4) + (traffic_sev * 0.6), 4)

        enriched.update({
            "weather_severity_num": weather_sev,
            "traffic_density_num": traffic_sev,
            "estimated_real_min": round(estimated_real_min, 2),
            "eta_urgency_ratio": round(eta_urgency_ratio, 4),
            "expected_delay_min": round(expected_delay_min, 2),
            "environmental_risk_index": environmental_risk_index
        })
        
        return enriched

    def process_batch(self, events_list: list) -> pd.DataFrame:
        """
        Procesa una lista de eventos y los convierte en DataFrame estructurado.
        """
        enriched_list = [self.enrich_event(ev) for ev in events_list]
        return pd.DataFrame(enriched_list)

if __name__ == "__main__":
    fs = FeatureStore()
    sample = {
        "shipment_id": "SH-2026-1001",
        "speed_kmh": 25.0,
        "distance_remaining_km": 80.0,
        "scheduled_eta_minutes": 90,
        "traffic_density": "SEVERE_CONGESTION",
        "weather_condition": "HEAVY_RAIN"
    }
    res = fs.enrich_event(sample)
    print(res)
