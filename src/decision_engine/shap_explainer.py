"""
Módulo de Explicabilidad en Tiempo Real (SHAP Explainer)
Calcula la contribución de cada variable a la probabilidad de retraso predicha.
"""
import shap
import pandas as pd
from typing import Dict, Any

class RealTimeSHAPExplainer:
    def __init__(self, model, feature_cols: list):
        self.model = model
        self.feature_cols = feature_cols
        # Si es un ensamble compuesto, usar el modelo GBDT principal para TreeExplainer
        tree_model = model.models.get("XGBoost", list(model.models.values())[0]) if hasattr(model, "models") else model
        self.explainer = shap.TreeExplainer(tree_model)

    def explain_event(self, enriched_event: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcula valores SHAP para una instancia individual.
        """
        df_single = pd.DataFrame([enriched_event])[self.feature_cols]
        shap_values = self.explainer.shap_values(df_single)
        
        # En XGBoost binario, shap_values es una matriz [1, n_features]
        if isinstance(shap_values, list):
            vals = shap_values[1][0]
        else:
            vals = shap_values[0]
            
        importance_dict = dict(zip(self.feature_cols, [float(v) for v in vals]))
        # Retornar ordenado por impacto positivo (contribución al retraso)
        sorted_importance = dict(sorted(importance_dict.items(), key=lambda item: item[1], reverse=True))
        return sorted_importance
