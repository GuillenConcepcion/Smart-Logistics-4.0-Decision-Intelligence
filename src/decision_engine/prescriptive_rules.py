"""
Motor Prescriptivo y Reglas de Decision Intelligence (DI)
Traduce las probabilidades del modelo ML en acciones operativas y alertas logísticas.
"""
from typing import Dict, Any
import sys
import os

# Añadir directorio raíz al path para permitir ejecuciones directas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
class DecisionEngine:
    def __init__(self, threshold_high: float = 0.75, threshold_medium: float = 0.45):
        self.threshold_high = threshold_high
        self.threshold_medium = threshold_medium

    def evaluate_risk(self, shipment_id: str, delay_probability: float, shap_factors: Dict[str, float]) -> Dict[str, Any]:
        """
        Evalúa el riesgo de retraso y emite recomendaciones prescriptivas.
        """
        if delay_probability >= self.threshold_high:
            risk_level = "ALTO"
            action_code = "NIVEL_1_REENRUTAMIENTO_URGENTE"
            recommendation = (
                "Alerta Crítica: Reenrutamiento dinámico urgente sugerido. "
                "Contactar a torre de control para activar vehículo de respaldo o ajustar ruta."
            )
        elif delay_probability >= self.threshold_medium:
            risk_level = "MEDIO"
            action_code = "NIVEL_2_NOTIFICACION_PREVENTIVA"
            recommendation = (
                "Alerta Moderada: Notificar preventivamente al cliente final sobre ajuste de ETA. "
                "Intensificar frecuencia de monitoreo telemático a 30 segundos."
            )
        else:
            risk_level = "BAJO"
            action_code = "NIVEL_3_ESTADO_NORMAL"
            recommendation = "Operación normal: Mantener monitoreo estándar en ruta."

        # Identificar el factor dominante que incrementa el riesgo
        dominant_factor = max(shap_factors.items(), key=lambda x: x[1]) if shap_factors else ("N/A", 0.0)
        dominant_feature = dominant_factor[0]
        dominant_impact = dominant_factor[1]

        # Sobreescribir recomendación estática con el LLM si hay riesgo
        if risk_level in ["ALTO", "MEDIO"]:
            from src.decision_engine.llm_agent import PrescriptiveLLMAgent
            agent = PrescriptiveLLMAgent()
            recommendation = agent.generate_recommendation(
                shipment_id=shipment_id,
                risk_level=risk_level,
                delay_probability=delay_probability,
                dominant_factor_name=dominant_feature,
                dominant_factor_impact=dominant_impact
            )

        return {
            "shipment_id": shipment_id,
            "delay_probability": round(delay_probability, 4),
            "risk_level": risk_level,
            "action_code": action_code,
            "recommendation": recommendation,
            "dominant_factor": {
                "feature": dominant_feature,
                "impact_score": round(dominant_impact, 4)
            }
        }

if __name__ == "__main__":
    engine = DecisionEngine()
    sample_factors = {"congestión_tráfico": 0.42, "lluvia_intensa": 0.28, "distancia_restante": 0.15}
    decision = engine.evaluate_risk("SH-2026-8942", delay_probability=0.82, shap_factors=sample_factors)
    print(decision)
