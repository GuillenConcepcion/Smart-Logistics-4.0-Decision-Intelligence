"""
Torre de Control & Dashboard de Decision Intelligence (Streamlit)
Interfaz visual interactiva en tiempo real para gestión logística y monitoreo prescriptivo.
"""
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import networkx as nx
import sqlite3
import json

def generate_alternative_route(lat, lon):
    """
    Simula un cálculo de reenrutamiento matemático usando NetworkX (Dijkstra).
    """
    G = nx.Graph()
    # Coordenadas relativas simuladas
    A = (lat, lon) # Origen (Posición actual)
    B = (lat + 0.05, lon + 0.04) # Nodo congestionado
    C = (lat + 0.12, lon + 0.08) # Destino
    D = (lat + 0.04, lon - 0.05) # Desvío alternativo 1
    E = (lat + 0.10, lon - 0.02) # Desvío alternativo 2
    
    G.add_node("A", pos=A)
    G.add_node("B", pos=B)
    G.add_node("C", pos=C)
    G.add_node("D", pos=D)
    G.add_node("E", pos=E)
    
    # Aristas y pesos (tiempo)
    G.add_edge("A", "B", weight=80) # Ruta original congestionada
    G.add_edge("B", "C", weight=20)
    
    G.add_edge("A", "D", weight=15) # Ruta alternativa óptima
    G.add_edge("D", "E", weight=15)
    G.add_edge("E", "C", weight=20)
    
    optimal_path = nx.shortest_path(G, source="A", target="C", weight="weight")
    original_path = ["A", "B", "C"]
    
    coords_original = [G.nodes[n]["pos"] for n in original_path]
    coords_optimal = [G.nodes[n]["pos"] for n in optimal_path]
    
    return coords_original, coords_optimal

from src.data_ingestion.iot_simulator import IoTSimulator
from src.processing.feature_store import FeatureStore
from src.models.predict import DelayPredictor
from src.decision_engine.prescriptive_rules import DecisionEngine
from src.decision_engine.shap_explainer import RealTimeSHAPExplainer
from src.decision_engine.route_optimizer import RouteOptimizer
from src.analytics.statistical_eda import StatisticalEDAEngine
from scipy import stats

# Configuración de página
st.set_page_config(
    page_title="Smart Logistics 4.0 | Decision Intelligence Control Tower",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Premium Dark Theme & Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Metrics Box - Glassmorphism */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid #3b82f6;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(59, 130, 246, 0.2);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Title Animations */
    h1 {
        background: -webkit-linear-gradient(45deg, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Plotly containers */
    .stPlotlyChart {
        background: rgba(30, 41, 59, 0.3);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        padding: 10px;
    }

    /* Cards Prescriptivas */
    .high-risk-card {
        background: linear-gradient(145deg, rgba(153, 27, 27, 0.8), rgba(69, 10, 10, 0.9));
        border: 1px solid rgba(239, 68, 68, 0.6);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.2);
    }
    .medium-risk-card {
        background: linear-gradient(145deg, rgba(154, 52, 18, 0.8), rgba(69, 26, 3, 0.9));
        border: 1px solid rgba(249, 115, 22, 0.6);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(249, 115, 22, 0.2);
    }
    .low-risk-card {
        background: linear-gradient(145deg, rgba(6, 95, 70, 0.8), rgba(6, 78, 59, 0.9));
        border: 1px solid rgba(16, 185, 129, 0.6);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_components():
    simulator = IoTSimulator(sample_interval=1)
    feature_store = FeatureStore()
    predictor = DelayPredictor(model_path="models/best_delay_model.pkl")
    decision_engine = DecisionEngine(threshold_high=0.75, threshold_medium=0.45)
    explainer = RealTimeSHAPExplainer(predictor.model, predictor.feature_cols)
    return simulator, feature_store, predictor, decision_engine, explainer

def render_control_tower():
    st.title("🚚 Smart Logistics 4.0: Decision Intelligence Control Tower")
    st.caption("Sistema Prescriptivo de Decision Intelligence (TFM UCM) | Base: 2021 Amazon Last-Mile Routing Research Challenge Dataset (Amazon Science & MIT CTL)")
    
    try:
        simulator, feature_store, predictor, decision_engine, explainer = load_components()
    except Exception as e:
        st.error(f"Error al cargar componentes: {e}. Asegúrese de haber ejecutado `python src/models/train.py`.")
        return

    # Sidebar: Controles de Simulación
    st.sidebar.header("⚙️ Panel de Control & Simulación")
    ingestion_mode = st.sidebar.radio("Modo de Ingesta:", ["Simulación Local (Síncrono)", "File-Based Streaming (Asíncrono)"])
    n_events = st.sidebar.slider("Cantidad de Envíos en Monitoreo", 5, 25, 12)
    refresh_button = st.sidebar.button("🔄 Actualizar Telemetría")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Objetivos & Umbrales SLA")
    st.sidebar.write("• **OTIF Objetivo:** ≥ 95.0%")
    st.sidebar.write("• **ROC-AUC Modelo:** ≥ 0.88")
    st.sidebar.write("• **Recall Target:** ≥ 0.90")
    st.sidebar.write("• **Umbral Crítico (Nivel 1):** P ≥ 0.75")
    st.sidebar.write("• **Umbral Moderado (Nivel 2):** 0.45 ≤ P < 0.75")

    if ingestion_mode == "Simulación Local (Síncrono)":
        events = [simulator.generate_telemetry_event() for _ in range(n_events)]
        df_gold = feature_store.process_batch(events)
        df_predicted = predictor.predict_batch(df_gold)
        
        decisions = []
        shap_summaries = []
        for idx, row in df_predicted.iterrows():
            row_dict = row.to_dict()
            shap_factors = explainer.explain_event(row_dict)
            decision = decision_engine.evaluate_risk(row["shipment_id"], row["delay_probability"], shap_factors)
            decisions.append(decision)
            shap_summaries.append(shap_factors)
            
        df_predicted["risk_level"] = [d["risk_level"] for d in decisions]
        df_predicted["action_code"] = [d["action_code"] for d in decisions]
        df_predicted["recommendation"] = [d["recommendation"] for d in decisions]
        df_predicted["dominant_factor"] = [d["dominant_factor"]["feature"] for d in decisions]
    else:
        # FILE-BASED STREAMING MODE
        db_path = "data/live_fleet_state.db"
        if not os.path.exists(db_path):
            st.warning("⚠️ La base de datos SQLite no existe. Asegúrate de ejecutar `python src/processing/file_stream_consumer.py` en una terminal.")
            return
            
        conn = sqlite3.connect(db_path)
        df_predicted = pd.read_sql_query("SELECT * FROM fleet_telemetry LIMIT ?", conn, params=(n_events,))
        conn.close()
        
        if df_predicted.empty:
            st.warning("⚠️ No hay eventos procesados. Inicia el simulador: `python src/data_ingestion/iot_simulator.py`.")
            return
            
        # Deserializar shap_values guardados en SQLite con fallback seguro
        shap_summaries = []
        for _, row in df_predicted.iterrows():
            shap_raw = row.get("shap_values") if "shap_values" in row else None
            if shap_raw and isinstance(shap_raw, str):
                try:
                    shap_summaries.append(json.loads(shap_raw))
                except Exception:
                    shap_summaries.append({row.get("dominant_factor", "N/A"): 0.1})
            else:
                shap_summaries.append({row.get("dominant_factor", "N/A"): 0.1})

    # Asegurar columnas esperadas para compatibilidad con streaming y SQLite
    expected_defaults = {
        "distance_remaining_km": 28.5,
        "scheduled_eta_minutes": 45,
        "cargo_temp_celsius": 4.2,
        "speed_kmh": 42.0,
        "weather_severity_num": 0.0,
        "traffic_density_num": 0.1,
        "estimated_real_min": 40.0,
        "eta_urgency_ratio": 0.88,
        "environmental_risk_index": 0.20,
        "weather_condition": "CLEAR",
        "traffic_density": "LOW",
        "action_code": "NORMAL",
        "recommendation": "Continuar ruta programada.",
        "risk_level": "BAJO"
    }
    for col, val in expected_defaults.items():
        if col not in df_predicted.columns:
            df_predicted[col] = val

    # --- SECCIÓN 1: METRICAS CLAVE DE NEGOCIO (KPIs) ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    high_risk_count = sum(df_predicted["risk_level"] == "ALTO")
    med_risk_count = sum(df_predicted["risk_level"] == "MEDIO")
    low_risk_count = sum(df_predicted["risk_level"] == "BAJO")
    
    simulated_otif = round((low_risk_count / n_events) * 100, 1)
    
    col1.metric("Envíos Monitoreados", f"{n_events} vehículos")
    col2.metric("OTIF Estimado (En Ruta)", f"{simulated_otif}%", delta=f"{simulated_otif - 95.0:.1f}% vs Goal")
    col3.metric("🔴 Alertas Nivel 1 (Reenrutamiento)", f"{high_risk_count}", delta="Acción Urgente", delta_color="inverse")
    col4.metric("🟡 Alertas Nivel 2 (Preventivo)", f"{med_risk_count}", delta="Notificar Cliente", delta_color="off")
    col5.metric("🟢 Operación Normal", f"{low_risk_count}")

    st.markdown("---")

    # --- SECCIÓN 2: MAPA TELEMÁTICO Y MONITOREO DE FLOTA ---
    st.subheader("📍 Ubicación Telemática y Nivel de Riesgo por Vehículo")
    
    color_map = {"ALTO": "red", "MEDIO": "orange", "BAJO": "green"}
    df_predicted["color"] = df_predicted["risk_level"].map(color_map)
    
    center_lat = float(df_predicted["latitude"].mean()) if not df_predicted.empty else 43.6150
    center_lon = float(df_predicted["longitude"].mean()) if not df_predicted.empty else -116.2023
    
    fig_map = px.scatter_mapbox(
        df_predicted,
        lat="latitude",
        lon="longitude",
        color="risk_level",
        size="delay_probability",
        color_discrete_map=color_map,
        hover_name="shipment_id",
        hover_data=["vehicle_id", "speed_kmh", "traffic_density", "weather_condition", "delay_probability"],
        zoom=8.5,
        center=dict(lat=center_lat, lon=center_lon),
        height=750,
        title="Posición de Envíos en Tiempo Real (GPS IoT)"
    )
    fig_map.update_layout(
        mapbox_style="open-street-map",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    # Añadir rutas simuladas de reenrutamiento (Grafos NetworkX)
    for idx, row in df_predicted.iterrows():
        if row["risk_level"] == "ALTO":
            coords_orig, coords_opt = generate_alternative_route(row["latitude"], row["longitude"])
            
            lats_orig, lons_orig = zip(*coords_orig)
            fig_map.add_trace(go.Scattermapbox(
                mode="lines",
                lon=lons_orig,
                lat=lats_orig,
                line=dict(width=3, color="red"),
                name=f"Ruta Congestionada ({row['vehicle_id']})",
                opacity=0.6,
                hoverinfo="none"
            ))
            
            lats_opt, lons_opt = zip(*coords_opt)
            fig_map.add_trace(go.Scattermapbox(
                mode="lines",
                lon=lons_opt,
                lat=lats_opt,
                line=dict(width=4, color="#a855f7"),
                name=f"Desvío Óptimo ({row['vehicle_id']})",
                hoverinfo="none"
            ))
            
    st.plotly_chart(fig_map, use_container_width=True)

    # --- SECCIÓN 3: RECOMENDACIONES PRESCRIPTIVAS & SHAP EXPLAINABILITY ---
    st.markdown("---")
    st.subheader("🧠 Motor Prescriptivo & Explicabilidad SHAP (Decision Intelligence)")
    
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.write("#### Envíos en Riesgo y Acciones Prescriptivas Sugeridas")
        high_risk_df = df_predicted[df_predicted["risk_level"].isin(["ALTO", "MEDIO"])].sort_values("delay_probability", ascending=False)
        
        if len(high_risk_df) == 0:
            st.success("✅ Toda la flota operando bajo parámetros estándar. No se requieren acciones correctivas.")
        else:
            for idx, row in high_risk_df.iterrows():
                card_class = "high-risk-card" if row["risk_level"] == "ALTO" else "medium-risk-card"
                badge = "🔴 ALERTA NIVEL 1" if row["risk_level"] == "ALTO" else "🟡 ALERTA NIVEL 2"
                
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>{badge} | Envío {row['shipment_id']} (Vehículo {row['vehicle_id']})</h4>
                    <p><b>Probabilidad de Retraso P(Retraso):</b> {row['delay_probability']:.1%} | <b>Velocidad:</b> {row['speed_kmh']} km/h</p>
                    <p><b>Condición:</b> Clima {row['weather_condition']} | Tráfico {row['traffic_density']}</p>
                    <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 8px; margin-top: 10px; border-left: 4px solid #a855f7;">
                        <p style="margin: 0; font-size: 0.9em; color: #d8b4fe;"><b>🤖✨ Recomendación Generada por GenAI:</b></p>
                        <p style="margin: 5px 0 0 0; font-style: italic;">"{row['recommendation']}"</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.write("#### Factores Dominantes de Demora (SHAP Values)")
        selected_shipment = st.selectbox("Seleccione envío para analizar causa raíz:", df_predicted["shipment_id"].tolist())
        
        selected_idx = df_predicted[df_predicted["shipment_id"] == selected_shipment].index[0]
        shap_vals = shap_summaries[selected_idx]
        
        # Tomar los 5 principales factores
        top_shap = dict(list(shap_vals.items())[:5])
        
        df_shap_chart = pd.DataFrame({
            "Variable": list(top_shap.keys()),
            "Impacto SHAP": list(top_shap.values())
        }).sort_values("Impacto SHAP", ascending=True)
        
        fig_shap = px.bar(
            df_shap_chart,
            x="Impacto SHAP",
            y="Variable",
            orientation="h",
            title=f"Contribución al Riesgo de Retraso ({selected_shipment})",
            color="Impacto SHAP",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_shap, use_container_width=True)

    # --- SECCIÓN 4: TABLA DE PLANIFICACIÓN DE DESPACHO ACTIVO ---
    st.markdown("---")
    st.subheader("📋 Planificación de Despacho Activo (Flota en Ruta)")
    
    df_dispatch = df_predicted[[
        "vehicle_id", "shipment_id", "distance_remaining_km", "scheduled_eta_minutes", "delay_probability", "risk_level"
    ]].copy()
    
    df_dispatch.columns = [
        "Vehículo", "Envío / Ruta Asignada", "Distancia Restante (km)", "ETA Programado (min)", 
        "Prob. Retraso (ML Engine)", "Estado (SLA / Riesgo)"
    ]
    
    df_dispatch["Prob. Retraso (ML Engine)"] = df_dispatch["Prob. Retraso (ML Engine)"].apply(lambda x: f"{x:.1%}")
    
    st.dataframe(df_dispatch, use_container_width=True, hide_index=True)

    # --- SECCIÓN 5: TABLA DETALLADA DE LA CAPA GOLD (FEATURE STORE) ---
    with st.expander("🔍 Ver Matriz de Características Completa (Gold Layer Feature Store)"):
        st.dataframe(
            df_predicted[[
                "shipment_id", "vehicle_id", "speed_kmh", "distance_remaining_km",
                "scheduled_eta_minutes", "weather_condition", "traffic_density",
                "environmental_risk_index", "delay_probability", "risk_level", "recommendation"
            ]],
            use_container_width=True
        )

@st.cache_data
def load_historical_data():
    path = "data/processed/logistics_historical_dataset.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def render_historical_analysis():
    st.title("📊 Inteligencia Histórica (Batch Analytics)")
    st.caption("Análisis de tendencias, SLAs e impacto ambiental sobre el **2021 Amazon Last-Mile Routing Research Challenge Dataset** (Amazon Last Mile Science & MIT CTL).")
    
    df = load_historical_data()
    if df is None:
        st.warning("No se encontró el dataset histórico. Asegúrate de ejecutar `python src/models/train.py` primero.")
        return
        
    # KPIs Históricos
    total_envios = len(df)
    envios_retrasados = df["delay_status"].sum()
    otif_historico = round(((total_envios - envios_retrasados) / total_envios) * 100, 1)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Envíos Históricos", f"{total_envios:,}")
    col2.metric("OTIF Histórico Global", f"{otif_historico}%", delta=f"{otif_historico - 95.0:.1f}% vs SLA")
    col3.metric("Tasa de Retrasos", f"{(envios_retrasados/total_envios)*100:.1f}%", delta_color="inverse")
    
    st.markdown("---")
    
    # Gráficos Nivel 1 (Originales mejorados)
    col_chart1, col_chart2 = st.columns(2)
    
    df["Estado"] = df["delay_status"].map({0: "A Tiempo", 1: "Retrasado"})
    
    with col_chart1:
        st.subheader("Impacto Climático en Retrasos")
        weather_impact = df.groupby(["weather_condition", "Estado"]).size().reset_index(name="count")
        fig_weather = px.bar(
            weather_impact, 
            x="weather_condition", 
            y="count", 
            color="Estado",
            barmode="group",
            color_discrete_map={"A Tiempo": "#10b981", "Retrasado": "#ef4444"}
        )
        fig_weather.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_weather, use_container_width=True)
        
    with col_chart2:
        st.subheader("Riesgo Ambiental vs Demora")
        fig_risk = px.box(
            df,
            x="Estado",
            y="environmental_risk_index",
            color="Estado",
            color_discrete_map={"A Tiempo": "#10b981", "Retrasado": "#ef4444"}
        )
        fig_risk.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_risk, use_container_width=True)

    # NUEVO EDA (Exploratory Data Analysis)
    st.markdown("---")
    st.markdown("### Análisis Exploratorio de Datos (EDA Avanzado)")
    
    col_eda1, col_eda2 = st.columns(2)
    
    with col_eda1:
        st.subheader("Dispersión: Velocidad vs Distancia")
        fig_scatter = px.scatter(
            df.sample(min(2000, len(df))), # Muestra para rendimiento
            x="distance_remaining_km",
            y="speed_kmh",
            color="Estado",
            size="expected_delay_min",
            opacity=0.6,
            color_discrete_map={"A Tiempo": "#3b82f6", "Retrasado": "#ef4444"},
            labels={"distance_remaining_km": "Distancia Restante (km)", "speed_kmh": "Velocidad (km/h)"}
        )
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_eda2:
        st.subheader("Distribución de Tiempos de Retraso")
        fig_hist = px.histogram(
            df[df["expected_delay_min"] > 0], 
            x="expected_delay_min",
            nbins=30,
            color_discrete_sequence=["#a855f7"],
            labels={"expected_delay_min": "Minutos de Retraso Esperado"}
        )
        fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Matriz de Correlación de Variables")
    numeric_cols = [
        'speed_kmh', 'distance_remaining_km', 'cargo_temp_celsius', 
        'eta_urgency_ratio', 'environmental_risk_index', 'delay_status'
    ]
    corr_matrix = df[numeric_cols].corr()
    fig_corr = px.imshow(
        corr_matrix, 
        text_auto=True, 
        aspect="auto",
        color_continuous_scale="RdBu_r"
    )
    fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_corr, use_container_width=True)

@st.cache_data
def get_mow_clients(n_clients):
    opt = RouteOptimizer()
    return opt.generate_clients(n_clients)

def render_last_mile_optimizer():
    st.title("🚚 Optimizador de Rutas Last-Mile (VRP)")
    st.caption("Planificación automatizada y secuenciación óptima de rutas de última milla (K-Means + 2-Opt TSP)")
    
    # Explicación del caso de estudio
    with st.expander("ℹ️ Información del modelo operativo (Distribución de Última Milla)", expanded=False):
        st.markdown("""
        **Contexto del problema:**
        Operaciones de distribución urbana y suburbana de última milla con flota heterogénea a lo largo de rutas de entrega de alta densidad.
        
        **Desafíos:**
        - **Ventana operativa de servicio:** Cada entrega debe realizarse dentro de un SLA estricto de **90 minutos** desde la salida de la estación logística / hub.
        - **Planificación automatizada:** Sustitución de la planificación manual por optimización combinatoria basada en K-Means y 2-Opt TSP.
        - **Tipos de rutas:**
          - *Rutas directas (Solo ida):* El conductor finaliza la jornada tras completar la última entrega programada.
          - *Rutas de ciclo cerrado (Ida y vuelta):* El vehículo retorna a la estación central al completar el itinerario.
        """)
        
    # Sidebar: Controles específicos del optimizador
    st.sidebar.header("⚙️ Configuración del ruteo")
    n_clients = st.sidebar.slider("Clientes a simular", 50, 800, 200, step=50)
    n_routes = st.sidebar.slider("Número de rutas (conductores)", 5, 30, 21)
    pct_regular = st.sidebar.slider("Conductores regulares (% Solo ida)", 0, 100, 70) / 100.0
    speed_kmh = st.sidebar.slider("Velocidad promedio (km/h)", 20, 60, 40)
    service_time_min = st.sidebar.slider("Tiempo por parada (min)", 1, 10, 3)
    max_time_min = st.sidebar.slider("Límite SLA (minutos)", 60, 120, 90)
    
    # Inicializar y optimizar
    optimizer = RouteOptimizer()
    df_clients = get_mow_clients(n_clients)
    
    with st.spinner("Optimizando rutas mediante K-Means y 2-opt TSP..."):
        df_stops, df_routes, summary = optimizer.solve_vrp(
            df_clients,
            n_routes=n_routes,
            pct_regular=pct_regular,
            speed_kmh=speed_kmh,
            service_time_min=service_time_min,
            max_time_min=max_time_min
        )
        
    # --- KPIs DE RENDIMIENTO ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Conversión a millas para consistencia con el caso de estudio (1 km = 0.621371 millas)
    miles_saved = summary["saved_distance_km"] * 0.621371
    annual_miles_saved = miles_saved * 260 # 260 días laborales al año
    annual_cost_saved = annual_miles_saved * 0.58 # 0.58 USD por milla
    annual_hours_saved = summary["saved_time_hours"] * 260
    
    # Determinar si cumple SLA
    sla_pct = summary["sla_compliance_global_pct"]
    sla_color = "normal" if sla_pct >= 95 else "inverse" # delta_color
    
    col1.metric(
        "Ahorro de distancia anual",
        f"{annual_miles_saved:,.0f} millas",
        f"{miles_saved:.1f} millas/día",
        help="Comparado con una ruta manual simulada sin optimizar"
    )
    col2.metric(
        "Ahorro de tiempo anual",
        f"{annual_hours_saved:,.0f} horas",
        f"{summary['saved_time_hours']:.1f} horas/día",
        help="Tiempo de conducción guardado para los voluntarios"
    )
    col3.metric(
        "Ahorro económico anual",
        f"${annual_cost_saved:,.2f}",
        f"Tasa de $0.58/milla",
        help="Estimación basada en el costo operativo de un sedán mediano"
    )
    col4.metric(
        "Cumplimiento global SLA",
        f"{sla_pct:.1f}%",
        f"{'Goal Met (>=95%)' if sla_pct >= 95 else 'Bajo SLA Target'}",
        delta_color=sla_color,
        help="Porcentaje de clientes que reciben la comida caliente antes del límite establecido (90 min)"
    )
    
    # --- MAPA INTERACTIVO ---
    st.subheader("📍 Visualización de rutas en Treasure Valley, Idaho")
    
    # Definir paleta de colores para las rutas (hasta 30 rutas)
    colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
        "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#aec7e8", "#ffbb78",
        "#98df8a", "#ff9896", "#c5b0d5", "#c49c94", "#f7b6d2", "#c7c7c7",
        "#dbdb8d", "#9edae5", "#393b79", "#5254a3", "#6b6ecf", "#9c9ede",
        "#637939", "#8ca252", "#b5cf6b", "#cedb9c", "#8c6d31", "#bd9e39"
    ]
    
    # Dibujar mapa de clientes y depot
    fig_map = go.Figure()
    
    # Agregar rutas como líneas
    for r_id in range(n_routes):
        r_stops = df_stops[df_stops["route_id"] == f"Ruta {r_id + 1:02d}"].sort_values("stop_number")
        if len(r_stops) < 2:
            continue
            
        color = colors[r_id % len(colors)]
        r_name = f"Ruta {r_id + 1:02d}"
        r_type = r_stops.iloc[0]["route_type"]
        
        # Trazar línea
        fig_map.add_trace(go.Scattermapbox(
            mode="lines+markers",
            lon=r_stops["longitude"],
            lat=r_stops["latitude"],
            line=dict(width=2.5, color=color),
            marker=dict(size=6, color=color),
            name=f"{r_name} ({r_type})",
            hoverinfo="text",
            hovertext=r_stops.apply(
                lambda row: f"Parada {row['stop_number']}: {row['location_name']}<br>"
                            f"Llegada: {row['cum_time_min']:.1f} min<br>"
                            f"Distancia Acum: {row['cum_dist_km']*0.621371:.2f} mi<br>"
                            f"SLA: {'Cumplido' if row['sla_met'] else '⚠️ VIOLADO'}",
                axis=1
            )
        ))
        
    # Agregar Depot como marcador especial
    fig_map.add_trace(go.Scattermapbox(
        mode="markers",
        lon=[optimizer.kitchen_lon],
        lat=[optimizer.kitchen_lat],
        marker=dict(
            size=14,
            color="#ef4444",
            symbol="star"
        ),
        name="Estación Logística Central (Hub)",
        hoverinfo="text",
        hovertext="Estación Logística Central (Hub)"
    ))
    
    # Agregar marcadores para paradas con SLA violado (halo rojo)
    violated_stops = df_stops[(df_stops["stop_number"] > 0) & (~df_stops["sla_met"]) & (df_stops["location_name"].str.startswith("MOW-"))]
    if len(violated_stops) > 0:
        fig_map.add_trace(go.Scattermapbox(
            mode="markers",
            lon=violated_stops["longitude"],
            lat=violated_stops["latitude"],
            marker=dict(
                size=12,
                color="#dc2626",
                symbol="circle"
            ),
            name="Alerta: SLA violado (>90 min)",
            hoverinfo="text",
            hovertext=violated_stops.apply(
                lambda row: f"¡SLA Violado!<br>Cliente: {row['location_name']}<br>Llegada: {row['cum_time_min']:.1f} min",
                axis=1
            )
        ))
        
    fig_map.update_layout(
        mapbox=dict(
            center=dict(lat=43.60, lon=-116.35),
            zoom=9.5,
            style="open-street-map"
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=750,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(15, 23, 42, 0.8)",
            font=dict(color="#f8fafc", size=10)
        )
    )
    
    st.plotly_chart(fig_map)
    
    # --- DETALLE DE RUTAS Y EXPLORADOR ---
    st.markdown("---")
    st.subheader("🔍 Detalle de secuencias de entrega y hojas de ruta")
    
    col_sel_left, col_sel_right = st.columns([1.2, 2])
    
    with col_sel_left:
        selected_route_name = st.selectbox(
            "Seleccione una ruta para inspeccionar:",
            df_routes["route_id"].tolist()
        )
        
        # Resumen de la ruta seleccionada
        route_meta = df_routes[df_routes["route_id"] == selected_route_name].iloc[0]
        
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); padding: 18px; border-radius: 12px; border-left: 5px solid #a855f7;">
            <h4 style="margin-top:0;">{route_meta['route_id']}</h4>
            <p style="margin: 5px 0;"><b>Tipo de ruta:</b> {route_meta['route_type']}</p>
            <p style="margin: 5px 0;"><b>Clientes en ruta:</b> {route_meta['num_clients']} hogares</p>
            <p style="margin: 5px 0;"><b>Distancia total:</b> {route_meta['total_distance_km'] * 0.621371:.2f} millas ({route_meta['total_distance_km']:.2f} km)</p>
            <p style="margin: 5px 0;"><b>Tiempo estimado:</b> {route_meta['total_time_min']:.1f} min</p>
            <p style="margin: 5px 0;"><b>Tiempo máximo de entrega:</b> {route_meta['max_delivery_time_min']:.1f} min</p>
            <p style="margin: 5px 0;"><b>Cumplimiento SLA:</b> {route_meta['sla_compliance_pct']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para descargar todas las rutas en CSV
        st.write("")
        csv_data = df_stops.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar hojas de ruta completas (CSV)",
            data=csv_data,
            file_name="hojas_de_ruta_last_mile.csv",
            mime="text/csv",
            icon=":material/download:"
        )
        
    with col_sel_right:
        st.write(f"#### Paradas en secuencia - {selected_route_name}")
        
        r_stops_detail = df_stops[df_stops["route_id"] == selected_route_name].copy()
        
        # Modificar las distancias a millas para la visualización
        r_stops_detail["Distancia Acum (mi)"] = r_stops_detail["cum_dist_km"] * 0.621371
        r_stops_detail["Distancia Parcial (mi)"] = r_stops_detail["segment_dist_km"] * 0.621371
        
        # Renombrar columnas para visualización amigable
        r_display = r_stops_detail[[
            "stop_number", "location_name", "Distancia Parcial (mi)", "Distancia Acum (mi)",
            "segment_time_min", "cum_time_min", "sla_met"
        ]].copy()
        
        r_display.columns = [
            "Parada", "Destino / Cliente", "Distancia Segmento (mi)", "Distancia Acumulada (mi)",
            "Tiempo Conducción (min)", "Tiempo Llegada (min desde salida)", "SLA Cumplido (<=90 min)"
        ]
        
        # Redondear valores
        r_display["Distancia Segmento (mi)"] = r_display["Distancia Segmento (mi)"].round(2)
        r_display["Distancia Acumulada (mi)"] = r_display["Distancia Acumulada (mi)"].round(2)
        r_display["Tiempo Conducción (min)"] = r_display["Tiempo Conducción (min)"].round(1)
        r_display["Tiempo Llegada (min desde salida)"] = r_display["Tiempo Llegada (min desde salida)"].round(1)
        
        st.dataframe(
            r_display,
            hide_index=True
        )

def render_statistical_eda():
    st.title("🔬 Módulo EDA, Estadística Descriptiva e Inferencial")
    st.caption("Contraste de hipótesis, análisis de distribuciones y pruebas no paramétricas sobre el **2021 Amazon Last-Mile Routing Research Challenge Dataset** (Amazon Last Mile Science & MIT CTL).")
    
    df = load_historical_data()
    if df is None:
        st.warning("⚠️ No se encontró el dataset histórico. Asegúrate de ejecutar `python src/models/train.py` primero.")
        return
        
    engine = StatisticalEDAEngine(alpha=0.05)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Descriptiva & Distribuciones",
        "🧪 Inferencia & Contraste de Hipótesis",
        "🔗 Correlaciones & Chi-Cuadrado (χ²)",
        "⚠️ Diagnóstico de Outliers & Robustez"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: DESCRIPTIVA & DISTRIBUCIONES
    # -------------------------------------------------------------
    with tab1:
        st.subheader("📋 Métricas Descriptivas Paramétricas y No Paramétricas")
        num_cols = [
            "speed_kmh", "distance_remaining_km", "scheduled_eta_minutes",
            "cargo_temp_celsius", "estimated_real_min", "eta_urgency_ratio",
            "expected_delay_min", "environmental_risk_index"
        ]
        desc_df = engine.compute_descriptive_metrics(df, num_cols)
        st.dataframe(desc_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("📈 Análisis de Distribución y Evaluación de Normalidad")
        
        col_var, col_cat = st.columns(2)
        with col_var:
            selected_var = st.selectbox(
                "Seleccione variable a analizar:", 
                num_cols, 
                format_func=lambda x: {
                    "speed_kmh": "Velocidad (km/h)",
                    "distance_remaining_km": "Distancia Restante (km)",
                    "scheduled_eta_minutes": "ETA Programado (min)",
                    "cargo_temp_celsius": "Temperatura de Carga (°C)",
                    "estimated_real_min": "Tiempo Estimado Real (min)",
                    "eta_urgency_ratio": "Ratio de Urgencia ETA",
                    "expected_delay_min": "Minutos de Retraso Esperado",
                    "environmental_risk_index": "Índice de Riesgo Ambiental"
                }.get(x, x)
            )
        with col_cat:
            group_by_col = st.selectbox("Segmentar por:", ["Ninguno", "delay_status", "weather_condition", "traffic_density"])
            
        series_data = df[selected_var].dropna()
        pt_est, boot_low, boot_high = engine.bootstrap_mean_ci(series_data, n_iterations=1500, ci=0.95)
        norm_res = engine.test_normality(series_data)
        
        # Tarjetas de resumen rápido de distribución
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Media Empírica", f"{series_data.mean():.2f}")
        c2.metric("Mediana (P50)", f"{series_data.median():.2f}")
        c3.metric("IC 95% Bootstrap", f"[{boot_low:.2f}, {boot_high:.2f}]")
        c4.metric(
            "Prueba Normalidad (Shapiro)", 
            "Normal" if norm_res["is_normal"] else "No Normal", 
            delta=f"p = {norm_res['tests']['Shapiro-Wilk']['p_value']:.4e}" if "Shapiro-Wilk" in norm_res["tests"] else "N/A",
            delta_color="normal" if norm_res["is_normal"] else "inverse"
        )
        
        col_plot1, col_plot2 = st.columns(2)
        with col_plot1:
            st.write("##### Histograma de Densidad y Límites de Confianza")
            if group_by_col == "Ninguno":
                fig_dist = px.histogram(
                    df, 
                    x=selected_var, 
                    nbins=40, 
                    marginal="box",
                    opacity=0.75,
                    color_discrete_sequence=["#3b82f6"]
                )
            else:
                fig_dist = px.histogram(
                    df, 
                    x=selected_var, 
                    color=group_by_col,
                    nbins=40, 
                    marginal="box",
                    barmode="overlay",
                    opacity=0.65
                )
            fig_dist.add_vline(x=series_data.mean(), line_dash="dash", line_color="#ef4444", annotation_text=f"Media: {series_data.mean():.2f}")
            fig_dist.add_vline(x=series_data.median(), line_dash="dot", line_color="#10b981", annotation_text=f"Mediana: {series_data.median():.2f}")
            fig_dist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_dist, use_container_width=True)
            
        with col_plot2:
            st.write("##### Gráfico Q-Q (Quantile-Quantile vs Normal)")
            res_prob = stats.probplot(series_data, dist="norm")
            theoretical_q = res_prob[0][0]
            sample_q = res_prob[0][1]
            slope, intercept, r = res_prob[1]
            
            fig_qq = go.Figure()
            fig_qq.add_trace(go.Scatter(
                x=theoretical_q,
                y=sample_q,
                mode='markers',
                marker=dict(color='#a855f7', size=5, opacity=0.7),
                name='Cuantiles Muestrales'
            ))
            fig_qq.add_trace(go.Scatter(
                x=theoretical_q,
                y=slope * theoretical_q + intercept,
                mode='lines',
                line=dict(color='#ef4444', width=2),
                name=f'Ajuste Teórico (R²={r**2:.3f})'
            ))
            fig_qq.update_layout(
                xaxis_title="Cuantiles Teóricos Normales",
                yaxis_title="Cuantiles Muestrales",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True
            )
            st.plotly_chart(fig_qq, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 2: INFERENCIA & CONTRASTE DE HIPÓTESIS
    # -------------------------------------------------------------
    with tab2:
        st.subheader("🧪 Contraste de Hipótesis Operacionales y Tamaño del Efecto")
        
        hypo_option = st.selectbox("Seleccione Hipótesis a Contrastar:", [
            "H1: ¿La velocidad media difiere significativamente entre envíos A Tiempo y Retrasados?",
            "H2: ¿La distancia restante es mayor en envíos con retraso?",
            "H3: ¿El tipo de clima impacta en los minutos de retraso esperado (expected_delay_min)?",
            "H4: ¿El nivel de tráfico genera diferencias significativas en el índice de riesgo ambiental?",
            "H5: [Personalizado] Comparación de 2 Grupos (Prueba de Welch & Mann-Whitney U)",
            "H6: [Personalizado] Comparación Multi-Grupo (ANOVA & Kruskal-Wallis)"
        ])
        
        if hypo_option.startswith("H1"):
            res = engine.test_two_groups_difference(df, "delay_status", "speed_kmh", 0, 1)
            h0_desc = "H0: No existe diferencia en la velocidad media entre envíos a tiempo y retrasados (μ_ontime = μ_delayed)."
            h1_desc = "H1: La velocidad media es significativamente distinta entre ambos grupos (μ_ontime ≠ μ_delayed)."
            num_v, grp_v = "speed_kmh", "delay_status"
        elif hypo_option.startswith("H2"):
            res = engine.test_two_groups_difference(df, "delay_status", "distance_remaining_km", 0, 1)
            h0_desc = "H0: La distancia restante media es igual para envíos a tiempo y retrasados."
            h1_desc = "H1: La distancia restante media difiere significativamente entre estados de entrega."
            num_v, grp_v = "distance_remaining_km", "delay_status"
        elif hypo_option.startswith("H3"):
            res = engine.test_multi_group_difference(df, "weather_condition", "expected_delay_min")
            h0_desc = "H0: El retraso esperado medio es idéntico bajo todas las condiciones climáticas."
            h1_desc = "H1: Al menos una condición climática presenta una distribución de retrasos significativamente diferente."
            num_v, grp_v = "expected_delay_min", "weather_condition"
        elif hypo_option.startswith("H4"):
            res = engine.test_multi_group_difference(df, "traffic_density", "environmental_risk_index")
            h0_desc = "H0: El riesgo ambiental medio es equivalente en todos los niveles de congestión."
            h1_desc = "H1: El nivel de tráfico genera variaciones estadísticamente significativas en el riesgo ambiental."
            num_v, grp_v = "environmental_risk_index", "traffic_density"
        elif hypo_option.startswith("H5"):
            col_h5_1, col_h5_2 = st.columns(2)
            with col_h5_1:
                num_v = st.selectbox("Variable numérica dependiente:", num_cols, key="h5_num")
            with col_h5_2:
                grp_v = st.selectbox("Variable categórica binaria:", ["delay_status"], key="h5_grp")
            res = engine.test_two_groups_difference(df, grp_v, num_v, 0, 1)
            h0_desc = f"H0: No existe diferencia en {num_v} entre los grupos de {grp_v}."
            h1_desc = f"H1: Existen diferencias significativas en {num_v} según {grp_v}."
        else:
            col_h6_1, col_h6_2 = st.columns(2)
            with col_h6_1:
                num_v = st.selectbox("Variable numérica dependiente:", num_cols, key="h6_num")
            with col_h6_2:
                grp_v = st.selectbox("Variable categórica multi-nivel:", ["weather_condition", "traffic_density"], key="h6_grp")
            res = engine.test_multi_group_difference(df, grp_v, num_v)
            h0_desc = f"H0: No existen diferencias en {num_v} entre las categorías de {grp_v}."
            h1_desc = f"H1: Existen diferencias significativas en {num_v} entre los niveles de {grp_v}."

        # Tarjeta de Decisión Estadística
        card_border = "#10b981" if res.get("reject_null_hypothesis") else "#f59e0b"
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid {card_border}; border-left: 6px solid {card_border}; padding: 20px; border-radius: 12px; margin-top: 15px; margin-bottom: 20px;">
            <h4 style="margin-top:0; color: #f8fafc;">📋 Formulación de Hipótesis:</h4>
            <p style="margin:4px 0; color: #cbd5e1;"><b>Hipótesis Nula:</b> {h0_desc}</p>
            <p style="margin:4px 0; color: #cbd5e1;"><b>Hipótesis Alternativa:</b> {h1_desc}</p>
            <hr style="border-color: rgba(255,255,255,0.1);"/>
            <h4 style="margin: 8px 0; color: #60a5fa;">💡 Conclusión Estadística e Inferencia:</h4>
            <p style="font-size: 1.05em; font-weight: 600; color: {'#34d399' if res.get('reject_null_hypothesis') else '#fbbf24'};">
                {res.get('decision') or res.get('conclusion')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Desglose de Pruebas
        col_res_left, col_res_right = st.columns([1.2, 1])
        with col_res_left:
            st.write("##### Estadísticos Formales de Contraste")
            if "welch_t_test" in res:
                tt = res["welch_t_test"]
                mw = res["mann_whitney_u_test"]
                df_test_summary = pd.DataFrame([
                    {
                        "Prueba": "Welch's t-test (Paramétrico)",
                        "Estadístico": f"t = {tt['t_statistic']:.4f}",
                        "p-valor": f"{tt['p_value']:.4e}",
                        "Significancia (α=0.05)": "Rechazar H0" if tt['p_value'] < 0.05 else "No Rechazar",
                        "Tamaño del Efecto": f"Cohen's d = {tt['cohens_d']:.3f} ({tt['effect_magnitude']})"
                    },
                    {
                        "Prueba": "Mann-Whitney U (No Paramétrico)",
                        "Estadístico": f"U = {mw['u_statistic']:.1f}",
                        "p-valor": f"{mw['p_value']:.4e}",
                        "Significancia (α=0.05)": "Rechazar H0" if mw['p_value'] < 0.05 else "No Rechazar",
                        "Tamaño del Efecto": f"Rank-Biserial r = {mw['rank_biserial_r']:.3f}"
                    }
                ])
                st.dataframe(df_test_summary, use_container_width=True, hide_index=True)
            elif "anova" in res:
                an = res["anova"]
                kw = res["kruskal_wallis"]
                df_test_summary = pd.DataFrame([
                    {
                        "Prueba": "One-Way ANOVA (Paramétrico)",
                        "Estadístico": f"F = {an['f_statistic']:.4f}",
                        "p-valor": f"{an['p_value']:.4e}",
                        "Significancia (α=0.05)": "Rechazar H0" if an['p_value'] < 0.05 else "No Rechazar",
                        "Tamaño del Efecto": f"Eta² (η²) = {an['eta_squared']:.4f}"
                    },
                    {
                        "Prueba": "Kruskal-Wallis H (No Paramétrico)",
                        "Estadístico": f"H = {kw['h_statistic']:.4f}",
                        "p-valor": f"{kw['p_value']:.4e}",
                        "Significancia (α=0.05)": "Rechazar H0" if kw['p_value'] < 0.05 else "No Rechazar",
                        "Tamaño del Efecto": f"Epsilon² (ε²) = {kw['epsilon_squared']:.4f}"
                    }
                ])
                st.dataframe(df_test_summary, use_container_width=True, hide_index=True)
                if "group_breakdown" in res:
                    st.write("###### Resumen por Categoría:")
                    st.dataframe(res["group_breakdown"], use_container_width=True, hide_index=True)

        with col_res_right:
            st.write("##### Visualización Comparativa de Grupos")
            fig_comp = px.violin(
                df, 
                x=grp_v, 
                y=num_v, 
                color=grp_v, 
                box=True, 
                points="all",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_comp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_comp, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 3: CORRELACIONES & CHI-CUADRADO (χ²)
    # -------------------------------------------------------------
    with tab3:
        st.subheader("🔗 Matrices de Correlación y Asociación Categórica")
        
        col_c1, col_c2 = st.columns([1.3, 1])
        with col_c1:
            corr_method = st.radio(
                "Coeficiente de Correlación:", 
                ["pearson", "spearman", "kendall"], 
                horizontal=True,
                format_func=lambda x: {
                    "pearson": "Pearson (Lineal)",
                    "spearman": "Spearman (Rangos / No Lineal)",
                    "kendall": "Kendall Tau (Concordancia)"
                }.get(x, x)
            )
            df_corr, df_pval = engine.compute_correlation_with_pvalues(df, num_cols, method=corr_method)
            
            # Anotaciones con estrellas de significancia
            annot_text = []
            for i in range(len(num_cols)):
                row_text = []
                for j in range(len(num_cols)):
                    r_val = df_corr.iloc[i, j]
                    p_val = df_pval.iloc[i, j]
                    stars = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else ""))
                    row_text.append(f"{r_val:.2f}{stars}")
                annot_text.append(row_text)
                
            fig_corr_mat = px.imshow(
                df_corr,
                text_auto=False,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                title=f"Matriz de Correlación {corr_method.capitalize()} (* p<0.05, ** p<0.01, *** p<0.001)"
            )
            fig_corr_mat.update_traces(text=annot_text, texttemplate="%{text}")
            fig_corr_mat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_corr_mat, use_container_width=True)

        with col_c2:
            st.write("##### Prueba Chi-Cuadrado (χ²) de Independencia")
            chi_cat1 = st.selectbox("Variable Categórica 1:", ["weather_condition", "traffic_density"], key="chi_c1")
            chi_cat2 = st.selectbox("Variable Categórica 2:", ["delay_status"], key="chi_c2")
            
            chi_res = engine.test_chi_square_association(df, chi_cat1, chi_cat2)
            
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); padding: 15px; border-radius: 10px; border-left: 4px solid #a855f7; margin-bottom: 15px;">
                <p style="margin:2px 0;"><b>Estadístico χ²:</b> {chi_res['chi2_statistic']:.2f} (gl = {chi_res['degrees_of_freedom']})</p>
                <p style="margin:2px 0;"><b>p-valor:</b> {chi_res['p_value']:.4e}</p>
                <p style="margin:2px 0;"><b>V de Cramér:</b> {chi_res['cramers_v']:.3f} (<b>{chi_res['association_strength']}</b>)</p>
                <p style="margin:2px 0; color: #a78bfa;"><b>Decisión:</b> {'Asociación Significativa' if chi_res['reject_null_hypothesis'] else 'Variables Independientes'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("###### Residuos Tipificados:")
            st.caption("Valores > +2.0 indican sobre-representación observada respecto a lo esperado.")
            st.dataframe(chi_res["standardized_residuals"], use_container_width=True)

    # -------------------------------------------------------------
    # TAB 4: DIAGNÓSTICO DE OUTLIERS & ROBUSTEZ
    # -------------------------------------------------------------
    with tab4:
        st.subheader("⚠️ Detección de Valores Atípicos y Análisis de Robustez")
        outlier_df = engine.detect_outliers(df, num_cols)
        st.dataframe(outlier_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.write("##### Diagrama de Dispersión con Bandas de Corte IQR")
        var_outlier = st.selectbox("Variable para visualización de Outliers:", num_cols, key="outlier_var_select")
        
        q25 = df[var_outlier].quantile(0.25)
        q75 = df[var_outlier].quantile(0.75)
        iqr = q75 - q25
        low_f = q25 - 1.5 * iqr
        upp_f = q75 + 1.5 * iqr
        
        df_plot_out = df[[var_outlier, "delay_status"]].copy().reset_index()
        df_plot_out["Tipo"] = np.where(
            (df_plot_out[var_outlier] < low_f) | (df_plot_out[var_outlier] > upp_f), 
            "Outlier (IQR)", 
            "Observación Estándar"
        )
        
        fig_out = px.scatter(
            df_plot_out,
            x="index",
            y=var_outlier,
            color="Tipo",
            color_discrete_map={"Observación Estándar": "#3b82f6", "Outlier (IQR)": "#ef4444"},
            opacity=0.7,
            title=f"Observaciones vs Límites de Tukey para {var_outlier}"
        )
        fig_out.add_hline(y=upp_f, line_dash="dash", line_color="#ef4444", annotation_text=f"Límite Sup: {upp_f:.2f}")
        fig_out.add_hline(y=low_f, line_dash="dash", line_color="#ef4444", annotation_text=f"Límite Inf: {low_f:.2f}")
        fig_out.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_out, use_container_width=True)

def main():
    st.sidebar.title("Navegación")
    st.sidebar.markdown("**📦 Dataset Base:**")
    st.sidebar.caption("2021 Amazon Last-Mile Routing Research Challenge Dataset (Amazon Science & MIT CTL)")
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Seleccione Módulo:", [
        "📡 Torre de Control (En Vivo)", 
        "📊 Inteligencia Histórica (Batch)",
        "🔬 EDA Estadístico e Inferencial",
        "🚚 Optimizador de Rutas Last-Mile"
    ])
    
    if page == "📡 Torre de Control (En Vivo)":
        render_control_tower()
    elif page == "📊 Inteligencia Histórica (Batch)":
        render_historical_analysis()
    elif page == "🔬 EDA Estadístico e Inferencial":
        render_statistical_eda()
    else:
        render_last_mile_optimizer()

if __name__ == "__main__":
    main()
