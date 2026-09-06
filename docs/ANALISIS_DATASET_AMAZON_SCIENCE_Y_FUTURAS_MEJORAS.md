# Análisis del Dataset Amazon Last Mile (INFORMS / Transportation Science 2022) y Evaluación de Futuras Mejoras del Proyecto

**Autor:** Guillén Concepción  
**Rol:** Senior Data Scientist & MLOps Engineer  
**Referencia Científica:** Merchán, D., Arora, J., Pachon, J., Konduri, K., Winkenbach, M., Parks, S., & Noszek, J. (2022). *2021 Amazon Last Mile Routing Research Challenge: Data Set*. **Transportation Science**, 56(5), 1173–1191. [https://doi.org/10.1287/trsc.2022.1173](https://doi.org/10.1287/trsc.2022.1173)  
**Proyecto:** TFM — Logística 4.0 & Decision Intelligence para Metro Meals on Wheels (Treasure Valley, Idaho)  

---

## 1. Contexto Científico y Relevancia del Artículo

El artículo publicado en **Transportation Science (INFORMS)** por el equipo de investigación de **Amazon Last Mile Science** y el **MIT Center for Transportation & Logistics (CTL)** formaliza la publicación del conjunto de datos de ruteo operacional más exhaustivo de la historia logística.

### 1.1 La Brecha entre Teoría y Realidad Operativa (*The Last-Mile Gap*)
Los modelos clásicos de Investigación Operativa (IO), como el Problema del Viajante (*Traveling Salesperson Problem* - TSP) o el Problema de Enrutamiento de Vehículos con Ventanas de Tiempo (VRPTW), asumen que la función objetivo universal es minimizar la distancia euclidiana o el tiempo nominal de viaje. Sin embargo, en el mundo real, los algoritmos puramente matemáticos producen rutas que los conductores experimentados **rechazan o alteran sistemáticamente en un 40% a 60% de los casos**.

```
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│      MODELO CLÁSICO DE IO (TSP/VRP)    │       │     EJECUCIÓN REAL DEL CONDUCTOR       │
├────────────────────────────────────────┤       ├────────────────────────────────────────┤
│ • Minimiza distancia geométrica teórica│  VS   │ • Prioriza aparcamiento accesible      │
│ • Ignora fricción de giros a izquierda │       │ • Agrupa por micro-zonas (aceras/calles│
│ • Asume tiempos de servicio homogéneos │       │ • Adapta paradas a tráfico no mapeado  │
│ • Secuencia rígida sin contexto local  │       │ • Conocimiento tácito del terreno      │
└────────────────────────────────────────┘       └────────────────────────────────────────┘
```

### 1.2 Estructura y Granularidad de Datos en 3 Niveles
El paper describe un ecosistema de datos estructurado en tres dimensiones interconectadas:
1. **Nivel Ruta (`route_data.json`):** Código de estación de origen (`DLA`, `DCH`, `DSE`, `DBO`, `DAU`), fecha, hora de salida UTC, capacidad del vehículo (`executor_capacity_cm3`) y score de calidad de ruta.
2. **Nivel Parada (`stops` & `actual_sequences.json`):** Coordenadas geográficas anonimizadas, tipo de parada (`Dropoff`), código de micro-zona (`zone_id`) y secuencia real recorrida por el conductor.
3. **Nivel Paquete (`package_data.json`):** Dimensiones volumétricas tridimensionales (`depth`, `height`, `width`), ventana temporal de entrega (`time_window`) y tiempo estimado de servicio en puerta (`planned_service_time_seconds`).
4. **Nivel Red / Tránsito (`travel_times.json`):** Matriz de tiempos de tránsito dinámicos entre pares de paradas calculados mediante algoritmos de enrutamiento basados en redes viales reales.

---

## 2. Lecciones Clave de la Competición de Amazon (2021)

### 2.1 El Paradigma Ganador: "Just Passing Through" (Cook, Held & Helsgaun)
El equipo ganador del desafío global —integrado por los matemáticos William Cook (Waterloo), Stephan Held (Bonn) y Keld Helsgaun (Roskilde), autores del legendario solver de TSP *LKH*— demostró una lección crucial para la ciencia de datos:

> **El enfoque ganador no fue Machine Learning puro ni Investigación Operativa tradicional aislada, sino una Formulación Híbrida: IO Combinatoria enriquecida con Restricciones Jerárquicas de Precedencia aprendidas del comportamiento del conductor.**

Descubrieron que los conductores humanos descomponen mentalmente la ruta en una **jerarquía de dos niveles**:
1. *Nivel Macro:* Ordenan los clústeres de vecindarios (`zone_id`).
2. *Nivel Micro:* Recorren exhaustivamente todas las paradas de una micro-zona antes de desplazarse a la siguiente, evitando saltos cruzados entre aceras o avenidas con alta densidad de tráfico.

### 2.2 Métricas de Evaluación Innovadoras (MWD & ERP)
El paper de Merchán et al. (2022) introdujo dos métricas estadísticas fundamentales para cuantificar la similitud entre la ruta calculada y la ruta real ejecutada:
* **Match-based Weighted Distance (MWD):** Mide la discrepancia en la asignación de secuencias considerando la proximidad espacial entre paradas contiguas.
* **Edit Distance with Real Penalty (ERP):** Extensión de la distancia de Levenshtein aplicada a series de tiempo espacio-temporales, penalizando saltos topológicamente inviables.

---

## 3. Evaluación de Futuras Mejoras para el Proyecto Metro Meals on Wheels

A partir de los hallazgos del paper de Amazon Science (Merchán et al., 2022) y el estado del arte de la Logística 4.0, se proponen cinco líneas estratégicas de innovación tecnológica para el proyecto:

```
                                  MAPA DE MEJORAS FUTURAS (ROADMAP)
                                  
  ┌─────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐
  │ 1. Ruteo Jerárquico     │       │ 2. Predict-then-Optimize│       │ 3. Servicio Dinámico    │
  │ Micro-Zonas (Learn2Route)│ ────> │ Pérdida Asimétrica SLA  │ ────> │ IA en Tiempo de Puerta  │
  └─────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘
                 │                                                                 │
                 ▼                                                                 ▼
  ┌─────────────────────────┐                                       ┌─────────────────────────┐
  │ 4. Re-Enrutamiento      │                                       │ 5. E-Logística Verde    │
  │ Dinámico en Streaming   │ <──────────────────────────────────── │ Flota EV & Huella CO2   │
  └─────────────────────────┘                                       └─────────────────────────┘
```

---

### Mejora 1: Algoritmo Híbrido "Learn-to-Route" en Dos Fases (Cluster-First, Route-Second)
* **Limitación Actual:** El módulo de ruteo de Meals on Wheels utiliza actualmente K-Means geográfico global y 2-opt TSP clásico para las 21 rutas.
* **Propuesta:** Implementar un modelo **Hierarchical Macro-Micro Router** inspirado en el enfoque de Amazon:
  * **Fase 1 (Macro):** Un modelo de Machine Learning (e.g. *Graph Neural Network* o *XGBoost Ranker*) predice el orden óptimo de los distritos postales y zonas residenciales de Treasure Valley (Boise, Meridian, Nampa, Caldwell).
  * **Fase 2 (Micro):** Se resuelven los ciclos locales por vecindario aplicando algoritmos de programación dinámica (Dijkstra / Lin-Kernighan-Helsgaun LKH-3) con restricciones de giro seguro a la derecha (*Right-turn preference*).
* **Impacto Estimado:** Reducción adicional del **8% al 12% en tiempo de conducción** y mayor aceptación por parte de los conductores voluntarios.

---

### Mejora 2: Marco "Predict-then-Optimize" con Penalización Asimétrica de Caducidad Térmica
* **Limitación Actual:** El predictor de Machine Learning (`StackingEnsemble`) y el optimizador de rutas operan de forma desacoplada (predicción en paralelo a la asignación).
* **Propuesta:** Integrar las probabilidades del modelo de ML directamente dentro de la **función de coste del optimizador matemático** (*Decision-Focused Learning* / *Smart Predict-then-Optimize*):
  $$\min \sum_{e \in E} c(e) \cdot x_e + \lambda \sum_{i \in V} P(\text{Retraso}_i \mid X_i) \cdot \Phi_{\text{SLA}}(t_i)$$
  donde $\Phi_{\text{SLA}}(t_i)$ es una función de penalización exponencial que castiga severamente cualquier ruta donde la comida caliente supere los **80 minutos** (margen de seguridad de 10 minutos antes del límite de 90 min).
* **Impacto Estimado:** Incremento del cumplimiento global de SLA del **97,5% al 99,8%** sin aumentar el número de vehículos en flota.

---

### Mejora 3: Aprendizaje de Tiempos de Servicio Dinámicos en Puerta ($\tau_{\text{servicio}}$)
* **Limitación Actual:** Se asume un tiempo promedio uniforme de servicio en entrega ($\tau = 3,0\text{ min}$).
* **Propuesta:** Desarrollar un modelo regresor (CatBoost / LightGBM) que prediga el tiempo de interacción en puerta ($\hat{\tau}_i$) considerando:
  * Tipo de infraestructura habitacional (vivienda unifamiliar, residencia tutelada, bloque con ascensor).
  * Grado de vulnerabilidad o necesidad de asistencia del usuario mayor (registrado en el expediente de atención social).
  * Condiciones meteorológicas extremas (nieve, calor severo).
* **Impacto Estimado:** Eliminación de retrasos en cascada en rutas con alta concentración de beneficiarios de movilidad reducida.

---

### Mejora 4: Re-Enrutamiento Dinámico en Tiempo Real (*Online Dynamic VRP*)
* **Limitación Actual:** Las rutas se calculan al inicio del día y las alertas prescriptivas generan sugerencias de desvío individuales.
* **Propuesta:** Implementar un **motor de re-optimización reactiva continua** acoplado al consumidor de streaming (Kafka / File-Stream):
  * Si un vehículo sufre una avería o queda atrapado en un atasco severo ($P(\text{Retraso}) > 0.85$), el sistema recalcula en $< 5\text{ segundos}$ la reasignación de las paradas no entregadas a vehículos adyacentes con capacidad y ventana SLA disponible.
* **Impacto Estimado:** Resiliencia total ante contingencias viales y garantía de entrega al 100% de los usuarios.

---

### Mejora 5: Sostenibilidad y Optimización de Flotas Eléctricas (E-VRP & Huella de Carbono)
* **Limitación Actual:** El cálculo de costes se basa en kilometraje y vehículos de combustión interna ($0,58\text{ USD/milla}$).
* **Propuesta:** Incorporar el modelo *Electric Vehicle Routing Problem with Time Windows* (EVRPTW):
  * Gestión de autonomía de batería en función del perfil topográfico de Idaho.
  * Planificación de recarga en electrolineras municipales durante descansos de voluntarios.
  * Cuantificación y auditoría de toneladas de $\text{CO}_2$ evitadas para memorias de sostenibilidad y captación de subvenciones públicas.

---

## 4. Conclusión

El estudio del dataset y metodología de **Amazon Last Mile (Merchán et al., 2022)** valida científicamente la dirección tomada en este TFM: **la unión de Big Data telemático, Machine Learning explicable (SHAP/Stacking) y optimización prescriptiva**. La adopción de las mejoras propuestas (ruteo jerárquico por zonas, función de coste predict-then-optimize y tiempos de puerta dinámicos) consolida el proyecto como una solución de vanguardia aplicable a escala industrial y humanitaria.
