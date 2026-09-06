#!/usr/bin/env bash
# ==============================================================================
# Smart Logistics 4.0 - Decision Intelligence (TFM - UCM)
# Lanzador de la Torre de Control en Linux / macOS
# ==============================================================================

if [ ! -d ".venv" ]; then
    echo "[INFO] Creando entorno virtual..."
    bash setup_env.sh
fi

source .venv/bin/activate
echo "Iniciando Torre de Control Streamlit (http://localhost:8501)..."
streamlit run src/visualization/dashboard.py
