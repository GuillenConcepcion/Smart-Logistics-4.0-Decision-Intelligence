import pytest
from src.decision_engine.prescriptive_rules import DecisionEngine

@pytest.fixture
def decision_engine():
    return DecisionEngine(threshold_high=0.75, threshold_medium=0.45)

def test_high_risk_decision(decision_engine):
    shap_factors = {"congestión_tráfico": 0.45, "clima_adverso": 0.20}
    decision = decision_engine.evaluate_risk(
        shipment_id="SH-2026-TEST-1",
        delay_probability=0.88,
        shap_factors=shap_factors
    )
    assert decision["risk_level"] == "ALTO"
    assert decision["action_code"] == "NIVEL_1_REENRUTAMIENTO_URGENTE"
    assert decision["dominant_factor"]["feature"] == "congestión_tráfico"
    assert "recommendation" in decision

def test_medium_risk_decision(decision_engine):
    shap_factors = {"ajuste_eta": 0.30, "velocidad_reducida": 0.15}
    decision = decision_engine.evaluate_risk(
        shipment_id="SH-2026-TEST-2",
        delay_probability=0.55,
        shap_factors=shap_factors
    )
    assert decision["risk_level"] == "MEDIO"
    assert decision["action_code"] == "NIVEL_2_NOTIFICACION_PREVENTIVA"
    assert decision["dominant_factor"]["feature"] == "ajuste_eta"

def test_low_risk_decision(decision_engine):
    shap_factors = {"distancia": 0.05}
    decision = decision_engine.evaluate_risk(
        shipment_id="SH-2026-TEST-3",
        delay_probability=0.15,
        shap_factors=shap_factors
    )
    assert decision["risk_level"] == "BAJO"
    assert decision["action_code"] == "NIVEL_3_ESTADO_NORMAL"
