#!/usr/bin/env bash
# ==============================================================================
# Smart Logistics 4.0 - Decision Intelligence (TFM - UCM)
# Script de Creación y Configuración del Entorno Virtual (.venv) en Linux / macOS
# ==============================================================================

set -e

echo ""
echo "=============================================================================="
echo "[1/4] Verificando instalación de Python 3..."
echo "=============================================================================="
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 no se encuentra instalado en el sistema."
    exit 1
fi
python3 --version

echo ""
echo "=============================================================================="
echo "[2/4] Creando Entorno Virtual (.venv)..."
echo "=============================================================================="
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "[OK] Entorno virtual '.venv' creado con éxito."
else
    echo "[INFO] El directorio '.venv' ya existe. Continuando..."
fi

echo ""
echo "=============================================================================="
echo "[3/4] Activando entorno e instalando requerimientos..."
echo "=============================================================================="
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=============================================================================="
echo "[4/4] Ejecutando pruebas automatizadas de verificación..."
echo "=============================================================================="
pytest tests/ -v

echo ""
echo "=============================================================================="
echo "[ÉXITO] Entorno virtual configurado y verificado al 100%."
echo "Para activar el entorno en futuras sesiones ejecute:"
echo "  source .venv/bin/activate"
echo "Para lanzar el Dashboard:"
echo "  streamlit run src/visualization/dashboard.py"
echo "=============================================================================="
echo ""
