@echo off
REM ==============================================================================
REM Smart Logistics 4.0 - Decision Intelligence (TFM - UCM)
REM Script de Creación y Configuración Automática del Entorno Virtual (.venv)
REM ==============================================================================

echo.
echo ==============================================================================
echo [1/4] Comprobando disponibilidad de Python...
echo ==============================================================================
python --version
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el PATH del sistema.
    echo Por favor instale Python 3.10 o superior desde https://www.python.org/
    pause
    exit /b %errorlevel%
)

echo.
echo ==============================================================================
echo [2/4] Creando el Entorno Virtual (.venv)...
echo ==============================================================================
if not exist ".venv" (
    python -m venv .venv
    echo [OK] Entorno virtual '.venv' creado con exito.
) else (
    echo [INFO] El entorno virtual '.venv' ya existe. Continuando...
)

echo.
echo ==============================================================================
echo [3/4] Activando e instalando dependencias (requirements.txt)...
echo ==============================================================================
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Ocurrio un problema al instalar las dependencias.
    pause
    exit /b %errorlevel%
)

echo.
echo ==============================================================================
echo [4/4] Ejecutando suite de pruebas automatizadas de verificacion...
echo ==============================================================================
pytest tests/ -v
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] Algunas pruebas fallaron. Revise el log superior.
) else (
    echo.
    echo [EXITO] Entorno virtual configurado y verificado al 100%%.
)

echo.
echo ==============================================================================
echo INSTRUCCIONES DE USO DEL ENTORNO VIRTUAL:
echo ==============================================================================
echo Para activar el entorno en futuras sesiones ejecute:
echo   .venv\Scripts\activate.bat
echo.
echo Para lanzar la Torre de Control y Dashboard:
echo   run_dashboard.bat
echo ==============================================================================
echo.
pause
