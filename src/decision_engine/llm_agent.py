"""
Módulo de Simulación de Agente GenAI (LLM Mock) para el TFM.
Simula la respuesta en lenguaje natural de un LLM (como GPT-4) basado en los factores SHAP y nivel de riesgo.
"""
import time
import random

class PrescriptiveLLMAgent:
    def __init__(self):
        # Usado para simular latencia de red si se desea, aquí lo mantenemos bajo para UI fluida.
        pass

    def generate_recommendation(self, shipment_id: str, risk_level: str, delay_probability: float, dominant_factor_name: str, dominant_factor_impact: float) -> str:
        """
        Genera una recomendación de acción en lenguaje natural.
        """
        # Mapeo amistoso de las variables
        factor_mapping = {
            "traffic_density_num": "congestión de tráfico",
            "weather_severity_num": "condiciones climáticas adversas",
            "eta_urgency_ratio": "ajuste en la ventana de entrega",
            "speed_kmh": "velocidad promedio reducida",
            "cargo_temp_celsius": "desviación en temperatura de carga"
        }
        
        factor_str = factor_mapping.get(dominant_factor_name, dominant_factor_name)
        prob_percent = int(delay_probability * 100)
        
        # Simular latencia de LLM
        time.sleep(0.3)
        
        if risk_level == "ALTO":
            templates_alto = [
                f"El envío {shipment_id} enfrenta un riesgo crítico de retraso ({prob_percent}%). El modelo indica que el factor principal es {factor_str}. Sugiero activar protocolo de emergencia y reenrutar por vía alternativa inmediatamente.",
                f"Alerta Crítica: Se pronostica demora inminente ({prob_percent}%) para {shipment_id} provocada mayormente por {factor_str}. Contactar al operador en ruta para sugerir desvío a autopista secundaria.",
                f"Prioridad Máxima en {shipment_id}: La probabilidad de incumplimiento de SLA ha subido al {prob_percent}% debido a {factor_str}. Recomiendo redirigir este vehículo o preparar una unidad de contingencia."
            ]
            return random.choice(templates_alto)
            
        elif risk_level == "MEDIO":
            templates_medio = [
                f"Atención preventiva en el vehículo {shipment_id}. La probabilidad de retraso se estima en {prob_percent}%, impulsada por {factor_str}. Sugiero notificar proactivamente al cliente final sobre un posible ajuste de ETA.",
                f"Riesgo moderado detectado en {shipment_id} ({prob_percent}%). La variable que más impacta es {factor_str}. Recomiendo incrementar la frecuencia telemática a 30s y monitorear evolución.",
                f"El envío {shipment_id} comienza a mostrar signos de desviación ({prob_percent}%) causados por {factor_str}. Considerar enviar mensaje preventivo al cliente informando un ligero retraso operacional."
            ]
            return random.choice(templates_medio)
            
        else:
            return "El vehículo opera bajo parámetros óptimos. Ninguna acción correctiva es necesaria."
