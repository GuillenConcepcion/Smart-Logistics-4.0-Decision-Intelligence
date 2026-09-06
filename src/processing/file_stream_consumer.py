import sys
import os
import json
import time
import sqlite3
import pandas as pd
import glob

# Añadir directorio raíz al path
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.processing.feature_store import FeatureStore
from src.processing.data_validator import DataValidator
from src.models.predict import DelayPredictor
from src.decision_engine.prescriptive_rules import DecisionEngine
from src.decision_engine.shap_explainer import RealTimeSHAPExplainer

DB_PATH = "data/live_fleet_state.db"
LANDING_ZONE = "data/streaming_landing_zone"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fleet_telemetry (
            vehicle_id TEXT PRIMARY KEY,
            shipment_id TEXT,
            timestamp TEXT,
            latitude REAL,
            longitude REAL,
            speed_kmh REAL,
            traffic_density TEXT,
            weather_condition TEXT,
            delay_probability REAL,
            risk_level TEXT,
            action_code TEXT,
            recommendation TEXT,
            dominant_factor TEXT,
            shap_values TEXT
        )
    """)
    # Migración: asegurar columna shap_values si la tabla ya existía
    cursor.execute("PRAGMA table_info(fleet_telemetry)")
    columns = [row[1] for row in cursor.fetchall()]
    if "shap_values" not in columns:
        cursor.execute("ALTER TABLE fleet_telemetry ADD COLUMN shap_values TEXT")
    conn.commit()
    conn.close()

def run_file_consumer():
    print(f"[File Consumer] Iniciando motor de Decision Intelligence.")
    print(f"[File Consumer] Escuchando micro-batches en: {LANDING_ZONE}")
    init_db()
    os.makedirs(LANDING_ZONE, exist_ok=True)

    # Inicializar componentes
    validator = DataValidator()
    feature_store = FeatureStore()
    predictor = DelayPredictor(model_path="models/best_delay_model.pkl")
    decision_engine = DecisionEngine(threshold_high=0.75, threshold_medium=0.45)
    explainer = RealTimeSHAPExplainer(predictor.model, predictor.feature_cols)
    
    while True:
        # Buscar ficheros JSON
        files = glob.glob(os.path.join(LANDING_ZONE, "*.json"))
        
        if not files:
            time.sleep(1) # Esperar a que el simulador envíe datos
            continue
            
        # Procesar archivos encontrados
        for filepath in files:
            try:
                with open(filepath, 'r') as f:
                    event = json.load(f)
            except Exception as e:
                print(f"[File Consumer] Error leyendo {filepath}: {e}")
                continue

            # 0. Validación de Calidad de Datos (Data Quality Gate)
            is_valid, clean_event, err_msg = validator.validate_event(event)
            if not is_valid:
                print(f"[File Consumer] Evento corrupto descartado de {event.get('vehicle_id')}: {err_msg}")
                os.remove(filepath)
                continue
                
            print(f"[File Consumer] Procesando evento validado de {clean_event.get('vehicle_id')}")
            
            # 1. Transformación (Feature Store)
            df_gold = feature_store.process_batch([clean_event])
            
            # 2. Predicción
            df_pred = predictor.predict_batch(df_gold)
            row = df_pred.iloc[0]
            
            # 3. Explicabilidad SHAP
            row_dict = row.to_dict()
            shap_factors = explainer.explain_event(row_dict)
            
            # 4. Motor Prescriptivo (GenAI / Reglas)
            decision = decision_engine.evaluate_risk(row["shipment_id"], row["delay_probability"], shap_factors)
            
            # 5. Escribir a Base de Datos (Sink)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO fleet_telemetry 
                (vehicle_id, shipment_id, timestamp, latitude, longitude, speed_kmh, traffic_density, weather_condition, 
                 delay_probability, risk_level, action_code, recommendation, dominant_factor, shap_values)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(vehicle_id) DO UPDATE SET
                timestamp=excluded.timestamp,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                speed_kmh=excluded.speed_kmh,
                traffic_density=excluded.traffic_density,
                weather_condition=excluded.weather_condition,
                delay_probability=excluded.delay_probability,
                risk_level=excluded.risk_level,
                action_code=excluded.action_code,
                recommendation=excluded.recommendation,
                dominant_factor=excluded.dominant_factor,
                shap_values=excluded.shap_values
            """, (
                row["vehicle_id"], row["shipment_id"], event["timestamp"], row["latitude"], row["longitude"],
                row["speed_kmh"], row["traffic_density"], row["weather_condition"],
                float(row["delay_probability"]), decision["risk_level"], decision["action_code"], 
                decision["recommendation"], decision["dominant_factor"]["feature"],
                json.dumps(shap_factors)
            ))
            
            conn.commit()
            conn.close()
            
            # Borrar el archivo procesado (Streaming completado)
            os.remove(filepath)

if __name__ == "__main__":
    run_file_consumer()
