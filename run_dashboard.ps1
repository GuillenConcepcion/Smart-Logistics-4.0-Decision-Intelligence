# ==============================================================================
# Smart Logistics 4.0 - Decision Intelligence (TFM - UCM)
# Lanzador de la Torre de Control y Dashboard en PowerShell
# ==============================================================================

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "[INFO] Entorno virtual no detectado. Ejecutando setup_env.ps1..." -ForegroundColor Yellow
    .\setup_env.ps1
}

Write-Host "`nActivando entorno virtual (.venv)..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Iniciando Torre de Control Streamlit (http://localhost:8501)...`n" -ForegroundColor Green
streamlit run src/visualization/dashboard.py
