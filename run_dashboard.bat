@echo off
REM ==============================================================================
REM Smart Logistics 4.0 - Decision Intelligence (TFM - UCM)
REM Lanzador Directo de la Torre de Control y Dashboard (Streamlit)
REM ==============================================================================

if not exist ".venv\Scripts\activate.bat" (
    echo [ADVERTENCIA] No se detecto el entorno virtual .venv.
    echo Ejecutando primero setup_env.bat para configurar el entorno...
    call setup_env.bat
)

echo.
echo ==============================================================================
echo [1/2] Activando entorno virtual (.venv)...
echo ==============================================================================
call .venv\Scripts\activate.bat

echo.
echo ==============================================================================
echo [2/2] Iniciando Torre de Control Streamlit (http://localhost:8501)...
echo ==============================================================================
streamlit run src/visualization/dashboard.py
pause
