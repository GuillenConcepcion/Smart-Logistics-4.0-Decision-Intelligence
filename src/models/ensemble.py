"""
Módulo de Ensamble y Super Learner para Predicción de Retrasos en Logística 4.0
Combina XGBoost, LightGBM, CatBoost y Random Forest en un clasificador apilado.
"""
from typing import Dict, Any
import numpy as np
from sklearn.base import clone

def clone_model(model):
    """Clona un estimador de scikit-learn / GBDT preservando sus hiperparámetros."""
    try:
        return clone(model)
    except Exception:
        return model.__class__(**model.get_params())

class LogisticsSuperLearner:
    """
    Ensamble Super Learner / Blended Stacking de modelos GBDT y Random Forest.
    Calcula el promedio probabilístico ponderado de los estimadores base.
    """
    def __init__(self, models: Dict[str, Any]):
        self.models = {k: clone_model(v) for k, v in models.items()}
        
    def fit(self, X_fit, y_fit):
        for name, m in self.models.items():
            m.fit(X_fit, y_fit)
        return self
        
    def predict_proba(self, X_val):
        probas = [m.predict_proba(X_val) for m in self.models.values()]
        return np.mean(probas, axis=0)
        
    def predict(self, X_val):
        p = self.predict_proba(X_val)[:, 1]
        return (p >= 0.50).astype(int)
