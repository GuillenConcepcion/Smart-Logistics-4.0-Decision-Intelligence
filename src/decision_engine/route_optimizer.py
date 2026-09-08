"""
Motor de Optimización de Rutas para Distribución de Última Milla (Amazon Last-Mile Challenge)
Implementa clustering K-Means y secuenciación heurística 2-opt para VRP.
Soporta rutas de ida (One-Way) e ida y vuelta (Round-Trip) con verificación de SLA.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# Radio de la Tierra en km para Haversine
R_EARTH = 6371.0

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia de círculo grande entre dos puntos en la Tierra.
    Soporta inputs tanto escalares como arrays de NumPy.
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2.0 * np.arcsin(np.sqrt(a))
    return R_EARTH * c

class RouteOptimizer:
    def __init__(self, kitchen_lat=43.615, kitchen_lon=-116.202):
        # Cocina Central de Boise (Depot)
        self.kitchen_lat = kitchen_lat
        self.kitchen_lon = kitchen_lon

    def generate_clients(self, n_clients=200, seed=42):
        """
        Genera clientes aleatorios realistas en el área de Treasure Valley, Idaho.
        Área aproximada de 2,745 km2 distribuida en Boise, Meridian, Nampa y Caldwell.
        """
        np.random.seed(seed)
        
        # Generar centros urbanos aproximados en Treasure Valley
        centers = [
            (43.615, -116.202, 0.4),  # Boise (mayor densidad)
            (43.612, -116.391, 0.35), # Meridian
            (43.578, -116.560, 0.25)  # Nampa
        ]
        
        lats = []
        lons = []
        
        for lat_c, lon_c, weight in centers:
            count = int(n_clients * weight)
            # Distribución normal alrededor del centro para simular densidad urbana
            lats.extend(np.random.normal(lat_c, 0.05, count))
            lons.extend(np.random.normal(lon_c, 0.08, count))
            
        # Ajustar si faltan algunos debido a redondeos
        while len(lats) < n_clients:
            lats.append(np.random.normal(43.612, 0.05))
            lons.append(np.random.normal(-116.35, 0.08))
            
        df = pd.DataFrame({
            "client_id": [f"MOW-{1000 + i}" for i in range(n_clients)],
            "latitude": lats,
            "longitude": lons
        })
        
        # Calcular distancia directa a la cocina central
        df["distance_to_kitchen_km"] = haversine_distance(
            self.kitchen_lat, self.kitchen_lon, df["latitude"], df["longitude"]
        )
        return df

    def solve_vrp(self, df_clients, n_routes=21, pct_regular=0.7, 
                  speed_kmh=40.0, service_time_min=3.0, max_time_min=90.0):
        """
        Resuelve el VRP mediante clustering K-Means y optimización 2-opt TSP para cada ruta.
        Determina rutas One-Way (regular) o Round-Trip (ocasional).
        """
        n_clients = len(df_clients)
        # 1. Agrupar clientes en clústeres usando K-Means
        coords = df_clients[["latitude", "longitude"]].values
        kmeans = KMeans(n_clusters=n_routes, random_state=42, n_init=10)
        df_clients["route_id"] = kmeans.fit_predict(coords)
        
        # Asignar tipo de conductor (Regular vs Ocasional) de forma determinista para consistencia
        # Rutas de 0 a int(n_routes * pct_regular) serán One-Way, el resto Round-Trip
        num_one_way = int(n_routes * pct_regular)
        route_types = {r: "One-Way" if r < num_one_way else "Round-Trip" for r in range(n_routes)}
        
        routes_data = {}
        all_stops_list = []
        
        # 2. Optimizar cada ruta (TSP)
        for r_id in range(n_routes):
            r_clients = df_clients[df_clients["route_id"] == r_id].copy()
            if len(r_clients) == 0:
                continue
                
            is_one_way = route_types[r_id] == "One-Way"
            
            # Resolver TSP
            best_sequence = self._optimize_tsp(r_clients, is_one_way)
            
            # Calcular tiempos y distancias detallados paso a paso
            stops = []
            curr_lat, curr_lon = self.kitchen_lat, self.kitchen_lon
            curr_dist = 0.0
            curr_time = 0.0
            
            # Registro del depósito (Inicio)
            stops.append({
                "route_id": f"Ruta {r_id + 1:02d}",
                "stop_number": 0,
                "location_name": "Cocina Central (Inicio)",
                "latitude": self.kitchen_lat,
                "longitude": self.kitchen_lon,
                "segment_dist_km": 0.0,
                "cum_dist_km": 0.0,
                "segment_time_min": 0.0,
                "cum_time_min": 0.0,
                "sla_met": True,
                "sla_limit_min": max_time_min,
                "driver_type": "Regular (Frecuente)" if is_one_way else "Ocasional (Voluntario)",
                "route_type": "Solo Ida (One-Way)" if is_one_way else "Ida y Vuelta (Round-Trip)"
            })
            
            for idx, stop_idx in enumerate(best_sequence):
                client = r_clients.iloc[stop_idx]
                dist = haversine_distance(curr_lat, curr_lon, client["latitude"], client["longitude"])
                travel_time = (dist / speed_kmh) * 60.0
                
                curr_dist += dist
                curr_time += travel_time
                
                # Para el cliente, el tiempo de entrega es al llegar (antes del servicio)
                arrival_time = curr_time
                sla_status = arrival_time <= max_time_min
                
                # Después de la entrega, se realiza el servicio
                curr_time += service_time_min
                
                curr_lat, curr_lon = client["latitude"], client["longitude"]
                
                stops.append({
                    "route_id": f"Ruta {r_id + 1:02d}",
                    "stop_number": idx + 1,
                    "location_name": client["client_id"],
                    "latitude": client["latitude"],
                    "longitude": client["longitude"],
                    "segment_dist_km": dist,
                    "cum_dist_km": curr_dist,
                    "segment_time_min": travel_time,
                    "cum_time_min": arrival_time, # Tiempo de entrega al cliente
                    "sla_met": sla_status,
                    "sla_limit_min": max_time_min,
                    "driver_type": "Regular (Frecuente)" if is_one_way else "Ocasional (Voluntario)",
                    "route_type": "Solo Ida (One-Way)" if is_one_way else "Ida y Vuelta (Round-Trip)"
                })
                
            # Si es Round-Trip, regresar a la cocina
            if not is_one_way:
                dist = haversine_distance(curr_lat, curr_lon, self.kitchen_lat, self.kitchen_lon)
                travel_time = (dist / speed_kmh) * 60.0
                curr_dist += dist
                curr_time += travel_time
                
                stops.append({
                    "route_id": f"Ruta {r_id + 1:02d}",
                    "stop_number": len(best_sequence) + 1,
                    "location_name": "Cocina Central (Retorno)",
                    "latitude": self.kitchen_lat,
                    "longitude": self.kitchen_lon,
                    "segment_dist_km": dist,
                    "cum_dist_km": curr_dist,
                    "segment_time_min": travel_time,
                    "cum_time_min": curr_time,
                    "sla_met": True,
                    "sla_limit_min": max_time_min,
                    "driver_type": "Ocasional (Voluntario)",
                    "route_type": "Ida y Vuelta (Round-Trip)"
                })
                
            all_stops_list.extend(stops)
            
            # Guardar resumen de la ruta
            routes_data[f"Ruta {r_id + 1:02d}"] = {
                "route_id": f"Ruta {r_id + 1:02d}",
                "num_clients": len(r_clients),
                "route_type": "Solo Ida (One-Way)" if is_one_way else "Ida y Vuelta (Round-Trip)",
                "total_distance_km": curr_dist,
                "total_time_min": curr_time,
                "max_delivery_time_min": max([s["cum_time_min"] for s in stops if s["stop_number"] > 0 and s["location_name"] != "Cocina Central (Retorno)"]),
                "sla_compliance_pct": sum([1 for s in stops if s["stop_number"] > 0 and s["location_name"] != "Cocina Central (Retorno)" and s["sla_met"]]) / len(r_clients) * 100.0
            }
            
        df_stops = pd.DataFrame(all_stops_list)
        df_routes = pd.DataFrame(routes_data.values())
        
        # 3. Simular Ruteo Manual para comparación (shuffled sequencing)
        manual_routes_dist = 0.0
        manual_routes_time = 0.0
        
        for r_id in range(n_routes):
            r_clients = df_clients[df_clients["route_id"] == r_id].copy()
            if len(r_clients) == 0:
                continue
            is_one_way = route_types[r_id] == "One-Way"
            
            # Secuencia manual ineficiente (desordenada)
            manual_seq = list(range(len(r_clients))) # Sin optimizar (orden por defecto)
            
            curr_lat, curr_lon = self.kitchen_lat, self.kitchen_lon
            r_dist = 0.0
            r_time = 0.0
            for stop_idx in manual_seq:
                client = r_clients.iloc[stop_idx]
                dist = haversine_distance(curr_lat, curr_lon, client["latitude"], client["longitude"])
                r_dist += dist
                r_time += (dist / speed_kmh) * 60.0 + service_time_min
                curr_lat, curr_lon = client["latitude"], client["longitude"]
            if not is_one_way:
                dist = haversine_distance(curr_lat, curr_lon, self.kitchen_lat, self.kitchen_lon)
                r_dist += dist
                r_time += (dist / speed_kmh) * 60.0
                
            manual_routes_dist += r_dist
            manual_routes_time += r_time
            
        summary = {
            "opt_total_distance_km": df_routes["total_distance_km"].sum(),
            "opt_total_time_hours": df_routes["total_time_min"].sum() / 60.0,
            "sla_compliance_global_pct": (df_stops[(df_stops["stop_number"] > 0) & (df_stops["location_name"].str.startswith("MOW-"))]["sla_met"].sum() / n_clients) * 100.0,
            "manual_total_distance_km": manual_routes_dist,
            "manual_total_time_hours": manual_routes_time / 60.0,
            "saved_distance_km": max(0.0, manual_routes_dist - df_routes["total_distance_km"].sum()),
            "saved_time_hours": max(0.0, (manual_routes_time - df_routes["total_time_min"].sum()) / 60.0)
        }
        
        return df_stops, df_routes, summary

    def _optimize_tsp(self, df_clients, is_one_way):
        """
        Encuentra una secuencia óptima para visitar todos los clientes usando el algoritmo 2-opt.
        Inicia con un camino Nearest Neighbor.
        """
        n = len(df_clients)
        if n == 0:
            return []
        
        # Calcular matriz de distancias
        # El índice 0 representa la Cocina Central, los índices 1..n representan los clientes
        coords = np.zeros((n + 1, 2))
        coords[0] = [self.kitchen_lat, self.kitchen_lon]
        coords[1:] = df_clients[["latitude", "longitude"]].values
        
        dist_matrix = np.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(i + 1, n + 1):
                d = haversine_distance(coords[i, 0], coords[i, 1], coords[j, 0], coords[j, 1])
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d
                
        # 1. Encontrar secuencia inicial con Nearest Neighbor (empezando en Depot 0)
        visited = [False] * (n + 1)
        visited[0] = True
        sequence = [0]
        
        for _ in range(n):
            curr = sequence[-1]
            best_next = -1
            best_dist = float('inf')
            for j in range(1, n + 1):
                if not visited[j] and dist_matrix[curr, j] < best_dist:
                    best_dist = dist_matrix[curr, j]
                    best_next = j
            visited[best_next] = True
            sequence.append(best_next)
            
        # 2. Correr optimización 2-opt
        # Para One-Way: No cerramos el ciclo al calcular el costo.
        # Para Round-Trip: Sumamos la distancia de retorno al depot (nodo 0) en el cálculo.
        improved = True
        while improved:
            improved = False
            for i in range(1, n):
                for j in range(i + 1, n + 1):
                    # Evaluar el cambio de costo al invertir la sección sequence[i:j+1]
                    # La sección antes de i y después de j queda intacta.
                    # El cambio de costo afecta las conexiones (i-1) -> i y j -> (j+1)
                    # En la nueva secuencia, tendremos (i-1) -> j y i -> (j+1)
                    
                    old_cost = dist_matrix[sequence[i-1], sequence[i]]
                    new_cost = dist_matrix[sequence[i-1], sequence[j]]
                    
                    if j < n:
                        old_cost += dist_matrix[sequence[j], sequence[j+1]]
                        new_cost += dist_matrix[sequence[i], sequence[j+1]]
                    elif not is_one_way:
                        # Si es round-trip y j es el último nodo, se conecta de vuelta al depot (0)
                        old_cost += dist_matrix[sequence[j], 0]
                        new_cost += dist_matrix[sequence[i], 0]
                        
                    if new_cost < old_cost - 1e-6:
                        # Invertir el tramo i a j
                        sequence[i:j+1] = list(reversed(sequence[i:j+1]))
                        improved = True
                        
        # Retornar la secuencia de clientes mapeada a sus índices en df_clients (restando 1)
        client_indices = [idx - 1 for idx in sequence[1:]]
        return client_indices
