"""
Módulo de Calidad y Validación de Datos (Data Quality & Validation)
Implementa esquemas estrictos con Pydantic para asegurar la integridad física
y dimensional de la telemetría antes de la ingesta en el Feature Store.
"""
import logging
from typing import Dict, Any, Tuple, List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataValidator")

VALID_WEATHER_CONDITIONS = {"CLEAR", "RAIN", "HEAVY_RAIN", "FOG", "SNOW"}
VALID_TRAFFIC_LEVELS = {"LOW", "MODERATE", "HIGH", "SEVERE_CONGESTION"}

class TelemetryEventSchema(BaseModel):
    shipment_id: str = Field(..., min_length=3, description="Identificador único del envío")
    vehicle_id: str = Field(..., min_length=3, description="Identificador del vehículo de flota")
    timestamp: str = Field(..., description="Timestamp ISO 8601")
    latitude: float = Field(..., ge=43.0, le=44.5, description="Latitud en área de Treasure Valley")
    longitude: float = Field(..., ge=-117.2, le=-115.5, description="Longitud en área de Treasure Valley")
    speed_kmh: float = Field(..., ge=0.0, le=160.0, description="Velocidad del vehículo en km/h")
    traffic_density: str = Field(..., description="Nivel de tráfico reportado")
    weather_condition: str = Field(..., description="Condición meteorológica")
    cargo_temp_celsius: float = Field(..., ge=-15.0, le=40.0, description="Temperatura de carga térmica")
    distance_remaining_km: float = Field(..., ge=0.0, le=500.0, description="Distancia restante en km")
    scheduled_eta_minutes: int = Field(..., ge=1, le=1440, description="ETA programado en minutos")

    @field_validator("weather_condition")
    @classmethod
    def validate_weather(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if v_upper not in VALID_WEATHER_CONDITIONS:
            raise ValueError(f"Condición climática '{v}' inválida. Debe ser una de {VALID_WEATHER_CONDITIONS}")
        return v_upper

    @field_validator("traffic_density")
    @classmethod
    def validate_traffic(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if v_upper not in VALID_TRAFFIC_LEVELS:
            raise ValueError(f"Nivel de tráfico '{v}' inválido. Debe ser uno de {VALID_TRAFFIC_LEVELS}")
        return v_upper

class DataValidator:
    """
    Validador de datos para producción y streaming continuo.
    """
    def __init__(self, reject_on_error: bool = True):
        self.reject_on_error = reject_on_error

    def validate_event(self, event: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Valida un evento individual contra el esquema estricto de Pydantic.
        Retorna: (is_valid, validated_dict, error_message)
        """
        try:
            validated = TelemetryEventSchema(**event)
            return True, validated.model_dump(), None
        except ValidationError as e:
            error_msg = f"Error de validación de datos: {e.errors()}"
            logger.warning(f"[Data Quality Alert] Evento rechazado: {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Error inesperado en validación: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def validate_batch(self, events: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filtra y valida un lote de eventos, separando los válidos de los anómalos.
        Retorna: (valid_events, rejected_events)
        """
        valid_events = []
        rejected_events = []
        for ev in events:
            is_valid, clean_dict, err = self.validate_event(ev)
            if is_valid:
                valid_events.append(clean_dict)
            else:
                rejected_events.append({"event": ev, "error": err})
        return valid_events, rejected_events

if __name__ == "__main__":
    validator = DataValidator()
    test_event_ok = {
        "shipment_id": "SH-2026-0001",
        "vehicle_id": "VH-101",
        "timestamp": "2026-09-05T18:00:00Z",
        "latitude": 43.6150,
        "longitude": -116.2023,
        "speed_kmh": 45.5,
        "traffic_density": "MODERATE",
        "weather_condition": "RAIN",
        "cargo_temp_celsius": 4.5,
        "distance_remaining_km": 35.0,
        "scheduled_eta_minutes": 45
    }
    is_ok, data, err = validator.validate_event(test_event_ok)
    print(f"Evento Válido: {is_ok} | Datos: {data}")

    test_event_corrupt = test_event_ok.copy()
    test_event_corrupt["speed_kmh"] = 999.0  # Anomaly
    is_ok, data, err = validator.validate_event(test_event_corrupt)
    print(f"Evento Corrupto Detectado: {not is_ok} | Error: {err}")
