"""
Motor de Análisis Exploratorio Profundo (EDA) del 2021 Amazon Last-Mile Routing Research Challenge Dataset
(Amazon Last Mile Science & MIT Center for Transportation & Logistics - CTL)
Genera estadísticas descriptivas, inferenciales, multivariadas y geoespaciales exhaustivas.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any

# Añadir raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.analytics.statistical_eda import StatisticalEDAEngine

def analyze_raw_amazon_metadata(raw_dir: str = "data/raw/amazon_last_mile_2021/training") -> Dict[str, Any]:
    """Analiza la estructura macro del dataset raw de Amazon."""
    route_file = os.path.join(raw_dir, "route_data.json")
    seq_file = os.path.join(raw_dir, "actual_sequences.json")
    pkg_file = os.path.join(raw_dir, "new_package_data.json")
    tt_file = os.path.join(raw_dir, "new_travel_times.json")
    
    print("[EDA Amazon] Leyendo metadatos de rutas...")
    with open(route_file, "r") as f:
        routes = json.load(f)
        
    with open(seq_file, "r") as f:
        seqs = json.load(f)
        
    total_routes = len(routes)
    stops_per_route = [len(r.get("stops", {})) for r in routes.values()]
    capacities = [r.get("executor_capacity_cm3", 0.0) / 1e6 for r in routes.values() if r.get("executor_capacity_cm3")] # m3
    stations = {}
    dates = []
    
    for r in routes.values():
        st_code = r.get("station_code", "UNKNOWN")
        stations[st_code] = stations.get(st_code, 0) + 1
        dates.append(r.get("date_YYYY_MM_DD", "UNKNOWN"))
        
    dates_unique = sorted(list(set(dates)))
    
    # Análisis de paquetes (muestra representativa de 300 rutas)
    pkg_depths, pkg_heights, pkg_widths, pkg_vols, service_times = [], [], [], [], []
    if os.path.exists(pkg_file):
        print("[EDA Amazon] Leyendo muestra de paquetes...")
        with open(pkg_file, "r") as f:
            pkgs = json.load(f)
        for r_id, stops in list(pkgs.items())[:300]:
            for s_id, p_dict in stops.items():
                for p_id, p_info in p_dict.items():
                    dims = p_info.get("dimensions", {})
                    d = dims.get("depth_cm", 0.0)
                    h = dims.get("height_cm", 0.0)
                    w = dims.get("width_cm", 0.0)
                    srv = p_info.get("planned_service_time_seconds", 0.0)
                    if d > 0 and h > 0 and w > 0:
                        pkg_depths.append(d)
                        pkg_heights.append(h)
                        pkg_widths.append(w)
                        pkg_vols.append((d * h * w) / 1000.0) # Litros
                    if srv > 0:
                        service_times.append(srv)

    return {
        "total_routes": total_routes,
        "total_stops": sum(stops_per_route),
        "stations_count": len(stations),
        "stations_distribution": stations,
        "date_range": f"{dates_unique[0]} a {dates_unique[-1]}" if dates_unique else "N/A",
        "stops_stats": {
            "mean": float(np.mean(stops_per_route)),
            "std": float(np.std(stops_per_route)),
            "median": float(np.median(stops_per_route)),
            "min": int(np.min(stops_per_route)),
            "max": int(np.max(stops_per_route)),
            "p25": float(np.percentile(stops_per_route, 25)),
            "p75": float(np.percentile(stops_per_route, 75)),
            "p95": float(np.percentile(stops_per_route, 95))
        },
        "capacity_m3_stats": {
            "mean": float(np.mean(capacities)) if capacities else 0,
            "median": float(np.median(capacities)) if capacities else 0,
            "std": float(np.std(capacities)) if capacities else 0
        },
        "package_stats": {
            "sample_size": len(pkg_vols),
            "vol_liters_mean": float(np.mean(pkg_vols)) if pkg_vols else 0,
            "vol_liters_median": float(np.median(pkg_vols)) if pkg_vols else 0,
            "vol_liters_std": float(np.std(pkg_vols)) if pkg_vols else 0,
            "service_time_sec_mean": float(np.mean(service_times)) if service_times else 0,
            "service_time_sec_median": float(np.median(service_times)) if service_times else 0,
            "service_time_sec_p90": float(np.percentile(service_times, 90)) if service_times else 0
        }
    }

def run_deep_eda_report(processed_path: str = "data/processed/logistics_historical_dataset.csv"):
    """Ejecuta el análisis EDA estadístico inferencial completo sobre el dataset Gold."""
    raw_meta = analyze_raw_amazon_metadata()
    
    print("=========================================================================")
    print("   MOTOR EDA AVANZADO: 2021 AMAZON LAST-MILE ROUTING CHALLENGE DATASET  ")
    print("   (Amazon Last Mile Science & MIT Center for Transportation & Logistics)")
    print("=========================================================================")
    print("\n-------------------------------------------------------------------------")
    print("   1. ANÁLISIS MACRO-ESTRUCTURAL DEL DATASET AMAZON LAST-MILE 2021      ")
    print("-------------------------------------------------------------------------")
    print(f"Rango Temporal de Operación   : {raw_meta['date_range']}")
    print("\nDistribución de Paradas por Ruta:")
    for k, v in raw_meta["stops_stats"].items():
        print(f"  • {k.upper():<8}: {v:.2f}")
        
    print("\nMuestra de Paquetería y Servicio:")
    for k, v in raw_meta["package_stats"].items():
        print(f"  • {k:<25}: {v:.2f}")

    print("\n=================================================================")
    print("   2. ANÁLISIS INFERENCIAL Y MULTIVARIADO (DATASET GOLD N=8,000) ")
    print("=================================================================")
    df = pd.read_csv(processed_path)
    engine = StatisticalEDAEngine()
    
    # 1. Métricas Descriptivas
    desc = engine.compute_descriptive_metrics(df)
    print("\n--- Tabla de Estadística Descriptiva Univariada ---")
    print(desc[["Variable", "Media (Mean)", "Mediana (Median)", "Desv. Estándar (Std)", "Rango Intercuartil (IQR)", "Asimetría (Skewness)", "Curtosis (Kurtosis)"]])
    
    # 2. Pruebas de Normalidad
    print("\n--- Pruebas de Normalidad (Shapiro-Wilk, D'Agostino, Kolmogorov-Smirnov) ---")
    for col in ["speed_kmh", "distance_remaining_km", "scheduled_eta_minutes", "cargo_temp_celsius", "eta_urgency_ratio"]:
        norm_test = engine.test_normality(df[col])
        sh = norm_test["tests"].get("Shapiro-Wilk", {})
        ks = norm_test["tests"].get("Kolmogorov-Smirnov", {})
        print(f"  • {col:<24}: Shapiro W={sh.get('statistic', 'N/A')}, p={sh.get('p_value', 0.0):.4e} | KS D={ks.get('statistic', 'N/A')}, p={ks.get('p_value', 0.0):.4e} -> {norm_test['conclusion']}")
        
    # 3. Contraste de Hipótesis Bi-Muestrales (Welch's t-test vs Mann-Whitney U)
    print("\n--- Contraste de Hipótesis Bi-Muestral (Sin Retraso vs Con Retraso) ---")
    for var in ["speed_kmh", "distance_remaining_km", "eta_urgency_ratio", "environmental_risk_index"]:
        t_res = engine.test_two_groups_difference(df, "delay_status", var, 0, 1)
        w = t_res["welch_t_test"]
        m = t_res["mann_whitney_u_test"]
        print(f"\n[Variable: {var}]")
        print(f"  Grupo 0 (Puntual) : N={t_res['group_1']['n']}, Media={t_res['group_1']['mean']}, Mediana={t_res['group_1']['median']}")
        print(f"  Grupo 1 (Retraso) : N={t_res['group_2']['n']}, Media={t_res['group_2']['mean']}, Mediana={t_res['group_2']['median']}")
        print(f"  Welch t-test      : t={w['t_statistic']:.4f}, p={w['p_value']:.4e}, Cohen's d={w['cohens_d']:.4f} ({w['effect_magnitude']})")
        print(f"  Mann-Whitney U    : U={m['u_statistic']:.4f}, p={m['p_value']:.4e}, Rank-Biserial r={m['rank_biserial_r']:.4f}")
        print(f"  Decisión Formal   : {t_res['decision']}")

    # 4. ANOVA y Kruskal-Wallis (Por Estación y Clima)
    print("\n--- Análisis de Varianza Multi-Grupo (Por Condición de Tráfico y Clima) ---")
    anova_trf = engine.test_multi_group_difference(df, "traffic_density", "speed_kmh")
    print(f"Tráfico -> Velocidad: F={anova_trf['anova']['f_statistic']:.2f} (p={anova_trf['anova']['p_value']:.4e}, Eta^2={anova_trf['anova']['eta_squared']:.4f}) | Kruskal H={anova_trf['kruskal_wallis']['h_statistic']:.2f} (p={anova_trf['kruskal_wallis']['p_value']:.4e})")
    
    anova_wtr = engine.test_multi_group_difference(df, "weather_condition", "cargo_temp_celsius")
    print(f"Clima -> Temp Carga : F={anova_wtr['anova']['f_statistic']:.2f} (p={anova_wtr['anova']['p_value']:.4e}, Eta^2={anova_wtr['anova']['eta_squared']:.4f}) | Kruskal H={anova_wtr['kruskal_wallis']['h_statistic']:.2f} (p={anova_wtr['kruskal_wallis']['p_value']:.4e})")

    # 5. Chi-Cuadrado de Independencia
    print("\n--- Pruebas de Independencia Chi-Cuadrado (Chi^2) ---")
    chi_trf = engine.test_chi_square_association(df, "traffic_density", "delay_status")
    print(f"Tráfico vs Retraso : Chi^2={chi_trf['chi2_statistic']:.2f}, p={chi_trf['p_value']:.4e}, V={chi_trf['cramers_v']:.3f} ({chi_trf['association_strength']})")
    
    chi_wtr = engine.test_chi_square_association(df, "weather_condition", "delay_status")
    print(f"Clima vs Retraso   : Chi^2={chi_wtr['chi2_statistic']:.2f}, p={chi_wtr['p_value']:.4e}, V={chi_wtr['cramers_v']:.3f} ({chi_wtr['association_strength']})")

    # 6. Detección de Outliers
    print("\n--- Detección de Valores Atípicos (IQR vs Z-Score) ---")
    outliers = engine.detect_outliers(df)
    print(outliers[["Variable", "Outliers (IQR)", "% Outliers (IQR)", "Outliers (|Z| > 3)", "% Outliers (Z-Score)", "Impacto en Media (Δμ)"]])

    return raw_meta, desc, outliers

if __name__ == "__main__":
    run_deep_eda_report()
