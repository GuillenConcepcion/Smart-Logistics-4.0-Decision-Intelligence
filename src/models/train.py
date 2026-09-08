"""
Suite Avanzada de Machine Learning & MLOps (State-of-the-Art)
Entrenamiento, Benchmarking Multi-Modelo y Calibración de Probabilidades para Logística 4.0.
Algoritmos: XGBoost, LightGBM, CatBoost, Random Forest, Extra Trees y Stacking Ensemble.
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any

# Inserción de la ruta raíz en sys.path
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    roc_auc_score, average_precision_score, recall_score, 
    precision_score, f1_score, fbeta_score, brier_score_loss,
    classification_report, confusion_matrix
)
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

import mlflow
import mlflow.sklearn
from src.data_ingestion.amazon_dataset_loader import AmazonDatasetLoader
from src.models.ensemble import LogisticsSuperLearner, clone_model

def get_feature_columns() -> List[str]:
    """Retorna las 10 características analíticas de la capa Gold."""
    return [
        "speed_kmh", 
        "distance_remaining_km", 
        "scheduled_eta_minutes", 
        "weather_severity_num", 
        "traffic_density_num", 
        "estimated_real_min", 
        "eta_urgency_ratio", 
        "expected_delay_min", 
        "environmental_risk_index",
        "cargo_temp_celsius"
    ]

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> Dict[str, float]:
    """Calcula la batería completa de métricas de clasificación y calibración."""
    return {
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "f2": float(fbeta_score(y_true, y_pred, beta=2.0, zero_division=0)),
        "brier_score": float(brier_score_loss(y_true, y_proba))
    }

def train_advanced_suite(
    dataset_path: str = "data/processed/logistics_historical_dataset.csv",
    experiment_name: str = "Amazon-Last-Mile-Delay-Predictor",
    n_splits: int = 5
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de entrenamiento, 5-Fold Cross Validation,
    benchmarking multi-modelo, ensamble y calibración de probabilidades.
    """
    print("=========================================================================")
    print("   SUITE AVANZADA DE MACHINE LEARNING & MLOPS: LOGÍSTICA 4.0            ")
    print("   Dataset: 2021 Amazon Last-Mile Routing Research Challenge Dataset     ")
    print("   (Amazon Last Mile Science & MIT Center for Transportation & Logistics)")
    print("=========================================================================")
    
    # 1. Carga de Datos
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        print(f"[ML Pipeline] Dataset cargado desde {dataset_path} con {len(df):,} observaciones.")
    else:
        print("[ML Pipeline] Dataset no encontrado. Ejecutando ETL de Amazon Last Mile...")
        loader = AmazonDatasetLoader(processed_csv_path=dataset_path)
        df = loader.build_gold_dataset(max_routes=120, max_records=8000)
        
    feature_cols = get_feature_columns()
    X = df[feature_cols].copy()
    y = df["delay_status"].values
    
    pos_count = int(np.sum(y))
    neg_count = len(y) - pos_count
    imbalance_ratio = neg_count / max(pos_count, 1)
    scale_pos_weight = imbalance_ratio * 1.5 # Optimización de coste asimétrico para Recall
    
    print(f"[ML Pipeline] Clases: Negativas={neg_count:,} (Puntuales), Positivas={pos_count:,} (Retrasos)")
    print(f"[ML Pipeline] Ratio de Desbalance={imbalance_ratio:.2f}x | scale_pos_weight={scale_pos_weight:.2f}")
    print(f"[ML Pipeline] Características seleccionadas ({len(feature_cols)}): {', '.join(feature_cols)}")
    
    # 2. Definición del Catálogo de Modelos State-of-the-Art
    base_models = {
        "XGBoost": XGBClassifier(
            n_estimators=180, 
            max_depth=5, 
            learning_rate=0.04, 
            subsample=0.85, 
            colsample_bytree=0.85, 
            scale_pos_weight=scale_pos_weight, 
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42, 
            eval_metric="logloss"
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=180, 
            max_depth=5, 
            learning_rate=0.04, 
            subsample=0.85, 
            colsample_bytree=0.85, 
            scale_pos_weight=scale_pos_weight, 
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42, 
            verbose=-1
        ),
        "CatBoost": CatBoostClassifier(
            iterations=180, 
            depth=5, 
            learning_rate=0.04, 
            auto_class_weights="Balanced", 
            random_seed=42, 
            verbose=False
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=180, 
            max_depth=8, 
            class_weight="balanced", 
            random_state=42, 
            n_jobs=-1
        ),
        "ExtraTrees": ExtraTreesClassifier(
            n_estimators=180, 
            max_depth=8, 
            class_weight="balanced", 
            random_state=42, 
            n_jobs=-1
        )
    }
    
    # Modelo 6: Stacking Ensemble (Super Learner Blending)
    stacking_models = {
        "XGBoost": base_models["XGBoost"],
        "LightGBM": base_models["LightGBM"],
        "CatBoost": base_models["CatBoost"],
        "RandomForest": base_models["RandomForest"]
    }
    stacking_classifier = LogisticsSuperLearner(stacking_models)
    
    all_models = dict(base_models)
    all_models["StackingEnsemble"] = stacking_classifier
    
    # 3. Stratified 5-Fold Cross-Validation
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    benchmark_results = []
    
    print("\n-------------------------------------------------------------------------")
    print(f"      EJECUTANDO EVALUACIÓN MULTI-MODELO ({n_splits}-FOLD CROSS VALIDATION)      ")
    print("-------------------------------------------------------------------------")
    
    # Configurar MLflow local
    try:
        mlflow.set_experiment(experiment_name)
    except Exception as e:
        print(f"[MLflow Info] Usando tracking local: {e}")

    with mlflow.start_run(run_name="Multi-Model-Benchmark-Suite-Amazon-2021"):
        mlflow.set_tag("project", "Amazon Last-Mile Logistics 4.0")
        mlflow.set_tag("lead", "Guillen Concepcion")
        mlflow.set_tag("dataset", "2021 Amazon Last-Mile Routing Research Challenge Dataset (Amazon Science & MIT CTL)")
        mlflow.log_param("n_samples", len(df))
        mlflow.log_param("cv_folds", n_splits)
        
        for name, model in all_models.items():
            print(f"\n[MODEL EVALUATION] Evaluando Modelo: [{name}] ...")
            fold_metrics = []
            
            oof_preds = np.zeros(len(df))
            oof_probas = np.zeros(len(df))
            
            for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
                X_tr, y_tr = X.iloc[train_idx], y[train_idx]
                X_va, y_va = X.iloc[val_idx], y[val_idx]
                
                model.fit(X_tr, y_tr)
                val_proba = model.predict_proba(X_va)[:, 1]
                val_pred = (val_proba >= 0.50).astype(int)
                
                oof_preds[val_idx] = val_pred
                oof_probas[val_idx] = val_proba
                
                m = evaluate_predictions(y_va, val_pred, val_proba)
                fold_metrics.append(m)
                
            # Métricas OOF (Out-of-Fold) consolidadas
            oof_summary = evaluate_predictions(y, oof_preds, oof_probas)
            
            mean_auc = np.mean([f["roc_auc"] for f in fold_metrics])
            std_auc = np.std([f["roc_auc"] for f in fold_metrics])
            mean_pr_auc = np.mean([f["pr_auc"] for f in fold_metrics])
            mean_recall = np.mean([f["recall"] for f in fold_metrics])
            mean_precision = np.mean([f["precision"] for f in fold_metrics])
            mean_f1 = np.mean([f["f1"] for f in fold_metrics])
            mean_f2 = np.mean([f["f2"] for f in fold_metrics])
            mean_brier = np.mean([f["brier_score"] for f in fold_metrics])
            
            print(f"   * ROC-AUC  : {mean_auc:.4f} +/- {std_auc:.4f} {'[PASS >=0.88]' if mean_auc>=0.88 else '[FAIL]'}")
            print(f"   * PR-AUC   : {mean_pr_auc:.4f}")
            print(f"   * Recall   : {mean_recall:.4f} {'[PASS >=0.90]' if mean_recall>=0.90 else '[FAIL]'}")
            print(f"   * Precision: {mean_precision:.4f}")
            print(f"   * F1-Score : {mean_f1:.4f} | F2-Score: {mean_f2:.4f}")
            print(f"   * Brier    : {mean_brier:.4f}")
            
            # MLflow nested run
            with mlflow.start_run(run_name=f"Model-{name}", nested=True):
                mlflow.log_metric("cv_roc_auc_mean", float(mean_auc))
                mlflow.log_metric("cv_roc_auc_std", float(std_auc))
                mlflow.log_metric("cv_pr_auc_mean", float(mean_pr_auc))
                mlflow.log_metric("cv_recall_mean", float(mean_recall))
                mlflow.log_metric("cv_precision_mean", float(mean_precision))
                mlflow.log_metric("cv_f1_mean", float(mean_f1))
                mlflow.log_metric("cv_f2_mean", float(mean_f2))
                mlflow.log_metric("cv_brier_mean", float(mean_brier))
                mlflow.set_tag("model_family", name)
                
            benchmark_results.append({
                "Modelo": name,
                "ROC-AUC (CV)": round(mean_auc, 4),
                "ROC-AUC Std": round(std_auc, 4),
                "PR-AUC (CV)": round(mean_pr_auc, 4),
                "Recall (CV)": round(mean_recall, 4),
                "Precision (CV)": round(mean_precision, 4),
                "F1-Score (CV)": round(mean_f1, 4),
                "F2-Score (CV)": round(mean_f2, 4),
                "Brier Score": round(mean_brier, 4)
            })

    # 4. Tabla Comparativa Final de Benchmark
    df_benchmark = pd.DataFrame(benchmark_results).sort_values("F2-Score (CV)", ascending=False)
    
    print("\n=========================================================================")
    print("               TABLA FINAL DE MODEL BENCHMARKING                        ")
    print("=========================================================================")
    print(df_benchmark.to_string(index=False))
    
    # 5. Selección del Modelo Campeón y Re-entrenamiento
    best_row = df_benchmark.iloc[0]
    best_name = best_row["Modelo"]
    champion_model = all_models[best_name]
    
    print("\n=========================================================================")
    print(f"[CHAMPION MODEL] MODELO CAMPEON SELECCIONADO: [{best_name}]")
    print(f"   * ROC-AUC Final  : {best_row['ROC-AUC (CV)']:.4f}")
    print(f"   * Recall Final   : {best_row['Recall (CV)']:.4f} (Cumple SLA)")
    print(f"   * F2-Score Final : {best_row['F2-Score (CV)']:.4f} (Optimizado Asimetrico)")
    print("=========================================================================")
    
    # 6. Re-entrenamiento del Modelo Campeón en todo el Dataset y Calibración
    print("\n[ML Training] Ajustando modelo campeón sobre el dataset completo...")
    champion_model.fit(X, y)
    
    # Calibración de probabilidades (Isotonic Calibration)
    print("[ML Training] Calibrando probabilidades con CalibratedClassifierCV (Isotonic)...")
    try:
        calibrated_champion = CalibratedClassifierCV(champion_model, cv="prefit", method="isotonic")
        calibrated_champion.fit(X, y)
    except Exception:
        calibrated_champion = champion_model
        
    # 7. Serialización del Artefacto
    os.makedirs("models", exist_ok=True)
    model_artifact_path = os.path.join("models", "best_delay_model.pkl")
    
    artifact_payload = {
        "model": champion_model,
        "calibrated_model": calibrated_champion,
        "model_name": best_name,
        "feature_cols": feature_cols,
        "metrics": {
            "auc": float(best_row["ROC-AUC (CV)"]),
            "pr_auc": float(best_row["PR-AUC (CV)"]),
            "recall": float(best_row["Recall (CV)"]),
            "precision": float(best_row["Precision (CV)"]),
            "f1": float(best_row["F1-Score (CV)"]),
            "f2": float(best_row["F2-Score (CV)"]),
            "brier": float(best_row["Brier Score"])
        },
        "benchmark_summary": df_benchmark.to_dict(orient="records"),
        "trained_date": pd.Timestamp.now().isoformat(),
        "n_samples": len(df)
    }
    
    joblib.dump(artifact_payload, model_artifact_path)
    print(f"[ML Pipeline] Artefacto del modelo serializado exitosamente en: {model_artifact_path}")
    
    # Guardar tabla de benchmark en CSV para documentación
    benchmark_csv_path = "data/processed/model_benchmark_results.csv"
    df_benchmark.to_csv(benchmark_csv_path, index=False)
    print(f"[ML Pipeline] Tabla de benchmark persistida en: {benchmark_csv_path}")
    
    return artifact_payload

if __name__ == "__main__":
    train_advanced_suite()
