import pytest
import numpy as np
from src.decision_engine.route_optimizer import RouteOptimizer, haversine_distance

@pytest.fixture
def optimizer():
    return RouteOptimizer()

def test_haversine_distance_known_points():
    # Distancia entre Cocina Central (Boise 43.615, -116.202) y Meridian (43.612, -116.391)
    # Aprox 15-16 km
    d = haversine_distance(43.615, -116.202, 43.612, -116.391)
    assert 14.0 <= d <= 17.0

def test_generate_clients(optimizer):
    df_clients = optimizer.generate_clients(n_clients=50, seed=42)
    assert len(df_clients) == 50
    assert "latitude" in df_clients.columns
    assert "longitude" in df_clients.columns
    assert "distance_to_kitchen_km" in df_clients.columns
    # Coordenadas en rango de Treasure Valley
    assert df_clients["latitude"].between(43.3, 43.9).all()
    assert df_clients["longitude"].between(-116.9, -115.8).all()

def test_solve_vrp_sla_and_route_types(optimizer):
    df_clients = optimizer.generate_clients(n_clients=60, seed=42)
    df_stops, df_routes, summary = optimizer.solve_vrp(
        df_clients,
        n_routes=6,
        pct_regular=0.5, # 3 One-Way, 3 Round-Trip
        speed_kmh=40.0,
        service_time_min=3.0,
        max_time_min=90.0
    )
    
    assert len(df_routes) == 6
    assert summary["opt_total_distance_km"] > 0
    assert summary["saved_distance_km"] >= 0  # Heurística 2-opt mejora o iguala ruta manual
    assert "sla_compliance_global_pct" in summary
    
    # Comprobar que rutas Round-Trip tienen parada final en cocina central
    round_trip_routes = df_routes[df_routes["route_type"] == "Ida y Vuelta (Round-Trip)"]["route_id"]
    for r_id in round_trip_routes:
        r_stops = df_stops[df_stops["route_id"] == r_id]
        last_stop = r_stops.iloc[-1]
        assert "Cocina Central" in last_stop["location_name"]
