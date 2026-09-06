"""
Procesamiento de Streaming y ETL de Telemetría (Spark Streaming Simulado)
Simula el procesamiento distribuido de eventos en streaming y actualización de la capa Gold.
"""
import time
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import pandas as pd
from typing import List, Dict, Any
from src.data_ingestion.iot_simulator import IoTSimulator
from src.processing.feature_store import FeatureStore

class SparkStreamingETL:
    def __init__(self):
        self.simulator = IoTSimulator(sample_interval=1)
        self.feature_store = FeatureStore()
        self.gold_buffer: List[Dict[str, Any]] = []

    def process_micro_batch(self, batch_size: int = 10) -> pd.DataFrame:
        """
        Simula el procesamiento de un micro-batch de Spark Streaming.
        """
        raw_events = [self.simulator.generate_telemetry_event() for _ in range(batch_size)]
        
        # Enriquecimiento mediante el Feature Store
        df_gold = self.feature_store.process_batch(raw_events)
        
        # Generación de la variable target hipotética para simulación de entrenamiento
        # delay_status = 1 si eta_urgency_ratio > 1.15 o expected_delay_min > 15
        df_gold["delay_status"] = (
            (df_gold["eta_urgency_ratio"] > 1.12) | 
            (df_gold["expected_delay_min"] > 15.0) | 
            (df_gold["environmental_risk_index"] > 0.70)
        ).astype(int)
        
        return df_gold

if __name__ == "__main__":
    etl = SparkStreamingETL()
    batch_df = etl.process_micro_batch(5)
    print("--- Spark Streaming Micro-Batch Procesado ---")
    print(batch_df[["shipment_id", "speed_kmh", "expected_delay_min", "environmental_risk_index", "delay_status"]])
