"""
Simulador de Ingesta Telemática e IoT
Genera eventos telemáticos en tiempo real simular envíos logísticos.
"""
import time
import json
import random
import os
import numpy as np
import pandas as pd
from datetime import datetime, timezone

class IoTSimulator:
    def __init__(self, sample_interval: int = 5, landing_zone_dir: str = "data/streaming_landing_zone", dataset_path: str = "data/processed/logistics_historical_dataset.csv"):
        self.sample_interval = sample_interval
        self.landing_zone_dir = landing_zone_dir
        
        # Crear la carpeta si no existe
        os.makedirs(self.landing_zone_dir, exist_ok=True)
        print(f"[IoT Simulator] Landing Zone configurada en: {self.landing_zone_dir}")
                
        self.vehicles = [f"VH-{i:03d}" for i in range(101, 115)]
        self.weather_conditions = ["CLEAR", "RAIN", "HEAVY_RAIN", "FOG", "SNOW"]
        self.traffic_levels = ["LOW", "MODERATE", "HIGH", "SEVERE_CONGESTION"]
        
        # Cargar paradas reales de Amazon si están disponibles
        self.real_waypoints = []
        if os.path.exists(dataset_path):
            try:
                df = pd.read_csv(dataset_path)
                if "lat" in df.columns and "lng" in df.columns:
                    self.real_waypoints = df[["lat", "lng", "station_code", "speed_kmh", "cargo_temp_celsius"]].to_dict(orient="records")
                    print(f"[IoT Simulator] {len(self.real_waypoints)} waypoints reales de Amazon cargados para telemetría.")
            except Exception as e:
                print(f"[IoT Simulator Warning] {e}")

    def generate_telemetry_event(self) -> dict:
        vehicle_id = random.choice(self.vehicles)
        
        if self.real_waypoints:
            wp = random.choice(self.real_waypoints)
            lat = float(wp["lat"]) + random.uniform(-0.005, 0.005)
            lng = float(wp["lng"]) + random.uniform(-0.005, 0.005)
            station = wp.get("station_code", "DLA3")
            shipment_id = f"AMZ-{station}-{random.randint(1000, 9999)}"
            speed = round(float(np.clip(float(wp.get("speed_kmh", 45.0)) + random.normalvariate(0, 3.0), 10.0, 90.0)), 2)
            cargo_temp = round(float(np.clip(float(wp.get("cargo_temp_celsius", 4.0)) + random.normalvariate(0, 0.4), 1.5, 9.5)), 2)
        else:
            lat = round(43.6150 + random.uniform(-0.15, 0.15), 6)
            lng = round(-116.2023 + random.uniform(-0.2, 0.2), 6)
            shipment_id = f"SH-2026-{random.randint(1000, 9999)}"
            speed = round(random.uniform(20.0, 90.0), 2)
            cargo_temp = round(random.uniform(2.0, 8.0), 1)

        event = {
            "shipment_id": shipment_id,
            "vehicle_id": vehicle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "speed_kmh": speed,
            "traffic_density": random.choice(self.traffic_levels),
            "weather_condition": random.choice(self.weather_conditions),
            "cargo_temp_celsius": cargo_temp,
            "distance_remaining_km": round(random.uniform(3.0, 45.0), 1),
            "scheduled_eta_minutes": random.randint(15, 120)
        }
        return event

    def run_simulation(self, duration_seconds: int = 30):
        print(f"[IoT Simulator] Iniciando simulación por {duration_seconds} segundos...")
        start_time = time.time()
        count = 0
        while time.time() - start_time < duration_seconds:
            event = self.generate_telemetry_event()
            
            # Guardar evento como fichero micro-batch en Landing Zone
            filename = f"event_{int(time.time()*1000)}_{event['vehicle_id']}.json"
            filepath = os.path.join(self.landing_zone_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(event, f)
                
            print(f"[File-Based Streaming Event #{count+1}] Depositado: {filename}")
            
            count += 1
            time.sleep(self.sample_interval)

if __name__ == "__main__":
    simulator = IoTSimulator(sample_interval=2)
    simulator.run_simulation(duration_seconds=60)
