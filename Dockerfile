# ==============================================================================
# Dockerfile Multi-Service: Decision Intelligence & Smart Logistics (Meals on Wheels)
# Compatible con Docker y Podman
# ==============================================================================
FROM python:3.10-slim AS base

# Variables de entorno de producción
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del repositorio
COPY . .

# Crear usuario no privilegiado para seguridad
RUN useradd -m -u 1001 appuser && \
    mkdir -p data/streaming_landing_zone data/processed models mlruns && \
    chown -R appuser:appuser /app

USER appuser

# Puerto por defecto de Streamlit
EXPOSE 8501 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando por defecto (Dashboard)
CMD ["streamlit", "run", "src/visualization/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
