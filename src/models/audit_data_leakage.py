"""
Auditoría Empírica de Data Leakage (Fuga de Información) & Validación Cruzada por Grupos
Logística 4.0 - Metro Meals on Wheels Treasure Valley
Benchmark comparativo: Modelo Naïve (con Fuga) vs. Modelos Saneados (Production-Ready)
Incluye generación de gráficos comparativos y persistencia de métricas.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.metrics import (
    roc_auc_score, average_precision_score, recall_score,
    precision_score, f1_score, fbeta_score, brier_score_loss
)
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# Inserción de la ruta raíz en sys.path
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.models.ensemble import LogisticsSuperLearner

NAIVE_FEATURES = [
    "speed_kmh", 
    "distance_remaining_km", 
    "scheduled_eta_minutes", 
    "weather_severity_num", 
    "traffic_density_num", 
    "estimated_real_min", 
    "eta_urgency_ratio",        # <--- Fuga de datos (componente directo del target)
    "expected_delay_min",       # <--- Fuga de datos (componente directo del target)
    "environmental_risk_index", 
    "cargo_temp_celsius"
]

SANITIZED_FEATURES = [
    "speed_kmh", 
    "distance_remaining_km", 
    "scheduled_eta_minutes", 
    "weather_severity_num", 
    "traffic_density_num", 
    "cargo_temp_celsius",
    "environmental_risk_index"
]

def evaluate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> Dict[str, float]:
    """Calcula la batería canónica de métricas de clasificación probabilística."""
    return {
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "f2": float(fbeta_score(y_true, y_pred, beta=2.0, zero_division=0)),
        "brier_score": float(brier_score_loss(y_true, y_proba))
    }

def get_base_models(scale_pos_weight: float) -> Dict[str, Any]:
    """Retorna el catálogo base de modelos de clasificación calibrados para recall."""
    xgb = XGBClassifier(
        n_estimators=160, max_depth=5, learning_rate=0.04, subsample=0.85,
        colsample_bytree=0.85, scale_pos_weight=scale_pos_weight,
        random_state=42, eval_metric="logloss"
    )
    lgb = LGBMClassifier(
        n_estimators=160, max_depth=5, learning_rate=0.04, subsample=0.85,
        colsample_bytree=0.85, scale_pos_weight=scale_pos_weight,
        random_state=42, verbose=-1
    )
    cat = CatBoostClassifier(
        iterations=160, depth=5, learning_rate=0.04, auto_class_weights="Balanced",
        random_seed=42, verbose=False
    )
    rf = RandomForestClassifier(
        n_estimators=160, max_depth=8, class_weight="balanced",
        random_state=42, n_jobs=-1
    )
    stacking = LogisticsSuperLearner({
        "XGBoost": xgb, "LightGBM": lgb, "CatBoost": cat, "RandomForest": rf
    })
    return {
        "XGBoost": xgb,
        "LightGBM": lgb,
        "CatBoost": cat,
        "RandomForest": rf,
        "StackingEnsemble": stacking
    }

def plot_benchmark_contrast(df_comp: pd.DataFrame, output_image_path: str = "images/benchmark_leakage_contrast.png") -> None:
    """Genera una figura comparativa de alta resolución (300 DPI) para la memoria del TFM."""
    sns.set_theme(style="whitegrid", palette="muted")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    
    # Palette personalizada
    palette = {
        "Naïve (Con Fuga)": "#e74c3c",                # Rojo alerta
        "Saneado Dinámico (En Tránsito)": "#2ecc71",   # Verde producción
        "Saneado Pre-Despacho (Estático)": "#3498db"   # Azul estratégico
    }
    
    # 1. ROC-AUC
    ax1 = axes[0, 0]
    sns.barplot(data=df_comp, x="Modelo", y="ROC_AUC", hue="Configuracion", palette=palette, ax=ax1)
    ax1.set_title("1. Comparativa de ROC-AUC: Degradación Controlada de Métricas", fontsize=13, fontweight="bold", pad=10)
    ax1.set_ylim(0.70, 1.05)
    ax1.axhline(0.88, color="#7f8c8d", linestyle="--", linewidth=1.2, label="Umbral Mínimo TFM (AUC ≥ 0.88)")
    ax1.set_ylabel("ROC-AUC Score")
    ax1.legend(loc="lower left", fontsize=9)
    for p in ax1.patches:
        height = p.get_height()
        if height > 0.1:
            ax1.annotate(f"{height:.3f}", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8, xytext=(0, 3), textcoords='offset points')

    # 2. Recall (Sensibilidad de Detección de Retrasos)
    ax2 = axes[0, 1]
    sns.barplot(data=df_comp, x="Modelo", y="Recall", hue="Configuracion", palette=palette, ax=ax2)
    ax2.set_title("2. Sensibilidad / Recall (Detección Oportuna de Retrasos)", fontsize=13, fontweight="bold", pad=10)
    ax2.set_ylim(0.70, 1.05)
    ax2.axhline(0.90, color="#e67e22", linestyle="--", linewidth=1.2, label="Meta SLA TFM (Recall ≥ 0.90)")
    ax2.set_ylabel("Recall (Clase Positiva)")
    ax2.legend(loc="lower left", fontsize=9)
    for p in ax2.patches:
        height = p.get_height()
        if height > 0.1:
            ax2.annotate(f"{height:.3f}", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8, xytext=(0, 3), textcoords='offset points')

    # 3. Precision vs. Recall Trade-Off (F2-Score)
    ax3 = axes[1, 0]
    sns.barplot(data=df_comp, x="Modelo", y="Precision", hue="Configuracion", palette=palette, ax=ax3)
    ax3.set_title("3. Precisión Operacional (Tasa de Falsas Alarmas)", fontsize=13, fontweight="bold", pad=10)
    ax3.set_ylim(0.25, 1.05)
    ax3.set_ylabel("Precision Score")
    ax3.legend(loc="upper right", fontsize=9)
    for p in ax3.patches:
        height = p.get_height()
        if height > 0.1:
            ax3.annotate(f"{height:.3f}", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8, xytext=(0, 3), textcoords='offset points')

    # 4. Calibración Probabilística (Brier Score - Menor es Mejor)
    ax4 = axes[1, 1]
    sns.barplot(data=df_comp, x="Modelo", y="Brier_Score", hue="Configuracion", palette=palette, ax=ax4)
    ax4.set_title("4. Incertidumbre y Calibración Probabilística (Brier Score ↓)", fontsize=13, fontweight="bold", pad=10)
    ax4.set_ylabel("Brier Score Loss (0 = Calibración Perfecta)")
    ax4.legend(loc="upper left", fontsize=9)
    for p in ax4.patches:
        height = p.get_height()
        if height > 0.0001:
            ax4.annotate(f"{height:.4f}", (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=8, xytext=(0, 3), textcoords='offset points')

    plt.suptitle("Auditoría de Data Leakage: Contraste Empírico 'Antes y Después'\nLogística 4.0 - Dataset Amazon Last-Mile Science & MIT CTL (N=8.000)", fontsize=16, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    plt.savefig(output_image_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[Auditoría Gráfica] Figura comparativa exportada exitosamente en: {output_image_path}")

def run_leakage_audit(
    dataset_path: str = "data/processed/logistics_historical_dataset.csv",
    output_csv_path: str = "data/processed/leakage_audit_comparison.csv",
    output_image_path: str = "images/benchmark_leakage_contrast.png",
    n_splits: int = 5
) -> pd.DataFrame:
    """
    Ejecuta el benchmark comparativo formal entre los 3 regímenes:
    1. Pipeline Naïve (con Data Leakage y StratifiedKFold a nivel de fila)
    2. Pipeline Saneado Dinámico (sin Target Leakage y con GroupKFold a nivel de ruta)
    3. Pipeline Saneado Pre-Despacho (con metadatos estáticos ex-ante y GroupKFold)
    """
    print("=========================================================================")
    print("      AUDITORÍA DE DATA LEAKAGE: MODELO NAÏVE VS. MODELO SANEADO         ")
    print("=========================================================================")
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset no encontrado en {dataset_path}")
        
    df = pd.read_csv(dataset_path)
    y = df["delay_status"].values
    groups = df["route_id"].values
    
    pos_count = int(np.sum(y))
    neg_count = len(y) - pos_count
    imbalance_ratio = neg_count / max(pos_count, 1)
    scale_pos_weight = imbalance_ratio * 1.5
    
    print(f"[Auditoría] Observaciones: {len(df):,} | Rutas únicas: {df['route_id'].nunique()}")
    print(f"[Auditoría] Distribución Clases: Retraso={pos_count} ({y.mean()*100:.2f}%) | Puntual={neg_count}")
    
    comparison_rows = []
    
    # -------------------------------------------------------------
    # 1. EVALUACIÓN NAÏVE (CON DATA LEAKAGE & STRATIFIED KFOLD)
    # -------------------------------------------------------------
    print("\n>>> FASE 1: Evaluando Modelos NAÏVE (con Data Leakage y StratifiedKFold)...")
    X_naive = df[NAIVE_FEATURES].copy()
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    models_naive = get_base_models(scale_pos_weight)
    
    for model_name, model in models_naive.items():
        oof_preds = np.zeros(len(df))
        oof_probas = np.zeros(len(df))
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X_naive, y)):
            X_tr, y_tr = X_naive.iloc[train_idx], y[train_idx]
            X_va, y_va = X_naive.iloc[val_idx], y[val_idx]
            
            model.fit(X_tr, y_tr)
            proba = model.predict_proba(X_va)[:, 1]
            oof_probas[val_idx] = proba
            oof_preds[val_idx] = (proba >= 0.50).astype(int)
            
        m = evaluate_metrics(y, oof_preds, oof_probas)
        print(f"   [Naïve] {model_name:16s} | ROC-AUC: {m['roc_auc']:.4f} | Recall: {m['recall']:.4f} | Precision: {m['precision']:.4f} | Brier: {m['brier_score']:.4f}")
        
        comparison_rows.append({
            "Configuracion": "Naïve (Con Fuga)",
            "Modelo": model_name,
            "Num_Features": len(NAIVE_FEATURES),
            "Estrategia_CV": "StratifiedKFold (Filas)",
            "ROC_AUC": round(m["roc_auc"], 4),
            "PR_AUC": round(m["pr_auc"], 4),
            "Recall": round(m["recall"], 4),
            "Precision": round(m["precision"], 4),
            "F1_Score": round(m["f1"], 4),
            "F2_Score": round(m["f2"], 4),
            "Brier_Score": round(m["brier_score"], 4),
            "Diagnostico": "Artificial / Fuga Circular"
        })
        
    # -------------------------------------------------------------
    # 2. EVALUACIÓN SANEADA DINÁMICA (EN TRÁNSITO + GROUP KFOLD POR RUTA)
    # -------------------------------------------------------------
    print("\n>>> FASE 2: Evaluando Modelos SANEADOS EN TRÁNSITO (GroupKFold por route_id)...")
    X_sanitized = df[SANITIZED_FEATURES].copy()
    gkf = GroupKFold(n_splits=n_splits)
    models_sanitized = get_base_models(scale_pos_weight)
    
    for model_name, model in models_sanitized.items():
        oof_preds = np.zeros(len(df))
        oof_probas = np.zeros(len(df))
        
        for fold, (train_idx, val_idx) in enumerate(gkf.split(X_sanitized, y, groups=groups)):
            X_tr, y_tr = X_sanitized.iloc[train_idx], y[train_idx]
            X_va, y_va = X_sanitized.iloc[val_idx], y[val_idx]
            
            model.fit(X_tr, y_tr)
            proba = model.predict_proba(X_va)[:, 1]
            oof_probas[val_idx] = proba
            oof_preds[val_idx] = (proba >= 0.50).astype(int)
            
        m = evaluate_metrics(y, oof_preds, oof_probas)
        print(f"   [Saneado Tránsito] {model_name:16s} | ROC-AUC: {m['roc_auc']:.4f} | Recall: {m['recall']:.4f} | Precision: {m['precision']:.4f} | Brier: {m['brier_score']:.4f}")
        
        comparison_rows.append({
            "Configuracion": "Saneado Dinámico (En Tránsito)",
            "Modelo": model_name,
            "Num_Features": len(SANITIZED_FEATURES),
            "Estrategia_CV": "GroupKFold (route_id)",
            "ROC_AUC": round(m["roc_auc"], 4),
            "PR_AUC": round(m["pr_auc"], 4),
            "Recall": round(m["recall"], 4),
            "Precision": round(m["precision"], 4),
            "F1_Score": round(m["f1"], 4),
            "F2_Score": round(m["f2"], 4),
            "Brier_Score": round(m["brier_score"], 4),
            "Diagnostico": "Producción Streaming / Telemetría"
        })

    # -------------------------------------------------------------
    # 3. EVALUACIÓN SANEADA PRE-DESPACHO (ESTRATÉGICA + GROUP KFOLD)
    # -------------------------------------------------------------
    print("\n>>> FASE 3: Evaluando Modelos SANEADOS PRE-DESPACHO (Sin Telemetría Dinámica + GroupKFold)...")
    df_predispatch = df.copy()
    df_predispatch["station_num"] = df_predispatch["station_code"].astype("category").cat.codes
    predispatch_features = ["station_num", "scheduled_eta_minutes", "weather_severity_num"]
    X_predispatch = df_predispatch[predispatch_features].copy()
    
    xgb_pre = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.04, scale_pos_weight=scale_pos_weight, random_state=42, eval_metric="logloss")
    lgb_pre = LGBMClassifier(n_estimators=100, max_depth=4, learning_rate=0.04, scale_pos_weight=scale_pos_weight, random_state=42, verbose=-1)
    cat_pre = CatBoostClassifier(iterations=100, depth=4, learning_rate=0.04, auto_class_weights="Balanced", random_seed=42, verbose=False)
    rf_pre = RandomForestClassifier(n_estimators=100, max_depth=6, class_weight="balanced", random_state=42, n_jobs=-1)
    stack_pre = LogisticsSuperLearner({"XGBoost": xgb_pre, "LightGBM": lgb_pre, "CatBoost": cat_pre, "RandomForest": rf_pre})
    
    predispatch_models = {
        "XGBoost": xgb_pre,
        "LightGBM": lgb_pre,
        "CatBoost": cat_pre,
        "RandomForest": rf_pre,
        "StackingEnsemble": stack_pre
    }
    
    for model_name, model in predispatch_models.items():
        oof_preds = np.zeros(len(df))
        oof_probas = np.zeros(len(df))
        
        for fold, (train_idx, val_idx) in enumerate(gkf.split(X_predispatch, y, groups=groups)):
            X_tr, y_tr = X_predispatch.iloc[train_idx], y[train_idx]
            X_va, y_va = X_predispatch.iloc[val_idx], y[val_idx]
            
            model.fit(X_tr, y_tr)
            proba = model.predict_proba(X_va)[:, 1]
            oof_probas[val_idx] = proba
            oof_preds[val_idx] = (proba >= 0.50).astype(int)
            
        m = evaluate_metrics(y, oof_preds, oof_probas)
        print(f"   [Saneado Pre-Despacho] {model_name:16s} | ROC-AUC: {m['roc_auc']:.4f} | Recall: {m['recall']:.4f} | Precision: {m['precision']:.4f} | Brier: {m['brier_score']:.4f}")
        
        comparison_rows.append({
            "Configuracion": "Saneado Pre-Despacho (Estático)",
            "Modelo": model_name,
            "Num_Features": len(predispatch_features),
            "Estrategia_CV": "GroupKFold (route_id)",
            "ROC_AUC": round(m["roc_auc"], 4),
            "PR_AUC": round(m["pr_auc"], 4),
            "Recall": round(m["recall"], 4),
            "Precision": round(m["precision"], 4),
            "F1_Score": round(m["f1"], 4),
            "F2_Score": round(m["f2"], 4),
            "Brier_Score": round(m["brier_score"], 4),
            "Diagnostico": "Producción Pre-Salida (SLA Ex-Ante)"
        })
        
    df_comp = pd.DataFrame(comparison_rows)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_comp.to_csv(output_csv_path, index=False)
    
    # Generar visualización gráfica comparativa
    plot_benchmark_contrast(df_comp, output_image_path=output_image_path)
    
    print("\n=========================================================================")
    print("               RESUMEN DE AUDITORÍA: NAÏVE VS. SANEADO                  ")
    print("=========================================================================")
    print(df_comp[["Configuracion", "Modelo", "ROC_AUC", "Recall", "Precision", "F2_Score", "Brier_Score", "Diagnostico"]].to_string(index=False))
    print(f"\n[Auditoría] Resultados guardados en: {output_csv_path}")
    
    return df_comp

if __name__ == "__main__":
    run_leakage_audit()
