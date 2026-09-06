import sys
import os
import json
import sqlite3
import pandas as pd

# Añadir directorio raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from kafka import KafkaConsumer

from src.processing.feature_store import FeatureStore
from src.models.predict import DelayPredictor
from src.decision_engine.prescriptive_rules import DecisionEngine
from src.decision_engine.shap_explainer import RealTimeSHAPExplainer

DB_PATH = "data/live_fleet_state.db"

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

def run_consumer(broker="localhost:9092", topic="telemetria_vehiculos"):
    print(f"[Kafka Consumer] Iniciando motor de Decision Intelligence. Conectando a {broker}...")
    init_db()
    
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[broker],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'
        )
    except Exception as e:
        print(f"[Kafka Consumer] Error conectando a Kafka: {e}. Asegúrese de que el docker-compose esté levantado.")
        return

    # Inicializar componentes
    feature_store = FeatureStore()
    predictor = DelayPredictor(model_path="models/best_delay_model.pkl")
    decision_engine = DecisionEngine(threshold_high=0.75, threshold_medium=0.45)
    explainer = RealTimeSHAPExplainer(predictor.model, predictor.feature_cols)
    
    print("[Kafka Consumer] Escuchando eventos de streaming...")
    
    for message in consumer:
        event = message.value
        print(f"[Kafka Consumer] Recibido evento de {event.get('vehicle_id')}")
        
        # 1. Transformación (Feature Store)
        df_gold = feature_store.process_batch([event])
        
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
        print(f"[Kafka Consumer] Estado actualizado en SQLite para {row['vehicle_id']} -> Riesgo: {decision['risk_level']}")

if __name__ == "__main__":
    run_consumer()
