# ==============================================================================
# Smart Logistics 4.0 - Decision Intelligence (TFM - UCM)
# Script de Creación y Configuración del Entorno Virtual (.venv) en PowerShell
# ==============================================================================

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "[1/4] Verificando Python..." -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan

try {
    $pythonVersion = python --version
    Write-Host "[OK] $pythonVersion detectado." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no está instalado o no se encuentra en el PATH." -ForegroundColor Red
    Write-Host "Descargue e instale Python 3.10+ desde https://www.python.org/" -ForegroundColor Yellow
    Exit 1
}

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "[2/4] Creando Entorno Virtual (.venv)..." -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "[OK] Entorno virtual '.venv' creado con éxito." -ForegroundColor Green
} else {
    Write-Host "[INFO] El directorio '.venv' ya existe. Omitiendo creación." -ForegroundColor Yellow
}

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "[3/4] Activando entorno e instalando dependencias (requirements.txt)..." -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan

& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Falló la instalación de requerimientos." -ForegroundColor Red
    Exit $LASTEXITCODE
}

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "[4/4] Verificando suite de pruebas automatizadas (PyTest)..." -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan

pytest tests/ -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[ÉXITO] Entorno virtual preparado y verificado al 100%." -ForegroundColor Green
} else {
    Write-Host "`n[ADVERTENCIA] Algunas pruebas presentaron errores." -ForegroundColor Yellow
}

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "CÓMO EJECUTAR EL PROYECTO EN POWERSHELL:" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "1. Activar el entorno virtual:    .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Lanzar Torre de Control:       streamlit run src/visualization/dashboard.py" -ForegroundColor White
Write-Host "==============================================================================`n" -ForegroundColor Cyan
