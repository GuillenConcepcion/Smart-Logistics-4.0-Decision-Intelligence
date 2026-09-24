# TRABAJO DE FIN DE MÁSTER
## Máster en Big Data & Data Science - Universidad Complutense de Madrid (UCM)
### *Integración de IoT y Big Data en la Logística 4.0 para el apoyo a decisiones inteligentes en la cadena de suministro*

---

# ANEXOS TÉCNICOS

---

# ANEXO A. COMPENDIO MATEMÁTICO E ÍNDICE DE FÓRMULAS DEL SISTEMA

El presente anexo formaliza el compendio matemático y algorítmico completo implementado a lo largo de las distintas capas de la plataforma de **Decision Intelligence** en Logística 4.0. Se estructura en un **Índice Maestro de Ecuaciones** seguido por el desglose analítico de cada formulación.

---

## A.1. Índice Maestro de Ecuaciones y Fórmulas

La siguiente tabla resume y codifica la totalidad de las formulaciones matemáticas que gobiernan la ingesta telemática, la compuerta de calidad, la ingeniería de variables, los clasificadores de Machine Learning, la explicabilidad local, la optimización combinatoria de rutas y los contrastes inferenciales:

| Nº Ecuación | Denominación Matemática | Formulación Compacta | Dominio / Unidades | Módulo / Script | Cap. |
| :---: | :--- | :--- | :---: | :--- | :---: |
| **(Ec. 1.1)** | Tasa de Incumplimiento de SLA | $\text{Tasa}_{\text{inc}} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(t_{\text{entrega}}^{(i)} > \tau_{\text{SLA}}^{(i)})$ | $[0, 1]$ (adimensional) | `statistical_eda.py` | Cap. 1 |
| **(Ec. 3.1)** | Validación Física Pydantic | $\mathcal{V}_{\text{fis}}(\mathbf{z}) = \prod_{k=1}^K \mathbb{I}(z_k \in [\ell_k, u_k])$ | $\{0, 1\}$ (booleano) | `data_validator.py` | Cap. 3 |
| **(Ec. 4.1)** | Distancia Geodésica Haversine | $d_H = 2 R \arcsin\left(\sqrt{\sin^2\frac{\Delta \phi}{2} + \cos \phi_1 \cos \phi_2 \sin^2\frac{\Delta \lambda}{2}}\right)$ | $\text{km}$ ($R = 6371\text{ km}$) | `route_optimizer.py` | Cap. 4 |
| **(Ec. 4.2)** | Velocidad Instantánea Discreta | $v_t = \frac{d_H(\mathbf{x}_t, \mathbf{x}_{t-1})}{\Delta t}$ | $\text{km/h}$ | `iot_simulator.py` | Cap. 4 |
| **(Ec. 4.3)** | Aceleración Longitudinal | $a_t = \frac{v_t - v_{t-1}}{\Delta t}$ | $\text{m/s}^2$ | `iot_simulator.py` | Cap. 4 |
| **(Ec. 4.4)** | Data Quality Score (DQS) | $DQS = \sum_{k=1}^K w_k \cdot \left(\frac{1}{N}\sum_{i=1}^N \mathcal{I}_{i,k}\right)$ | $[0, 1]$ ($99.95\%$) | `data_validator.py` | Cap. 4 |
| **(Ec. 4.5)** | Ratio Dinámico de Urgencia ($\eta_{\text{urg}}$) | $\eta_{\text{urg}} = \frac{t_{\text{transcurrido}}}{\tau_{\text{SLA}} - t_{\text{despacho}}}$ | $[0, \infty)$ (adimensional) | `amazon_dataset_loader.py` | Cap. 4 |
| **(Ec. 4.6)** | Desviación Temporal Esperada | $\Delta t_{\text{esp}} = \max\left(0, \sum \tau_{\text{tramo}} + \sum \tau_{\text{serv}} - \tau_{\text{SLA}}\right)$ | $\text{minutos}$ | `amazon_dataset_loader.py` | Cap. 4 |
| **(Ec. 4.7)** | Decaimiento Térmico Newtoniano | $T_{\text{carga}}(t) = T_{\text{amb}} + (T_0 - T_{\text{amb}}) e^{-\kappa t}$ | $^\circ\text{C}$ | `iot_simulator.py` | Cap. 4 |
| **(Ec. 4.8)** | Rango Intercuartílico Dinámico ($IR_{\text{amb}}$) | $IR_{\text{amb}} = \frac{v_{\text{tramo}} - Q_1(v)}{Q_3(v) - Q_1(v)}$ | $[0, \infty)$ (adimensional) | `amazon_dataset_loader.py` | Cap. 4 |
| **(Ec. 4.9)** | Log-Loss Ponderada (Coste Asimétrico) | $\mathcal{L}_w = -\frac{1}{N}\sum \left[ w_{\text{FN}} y_i \log \hat{p}_i + w_{\text{FP}} (1-y_i) \log(1-\hat{p}_i) \right]$ | $[0, \infty)$ | `train.py` | Cap. 4 |
| **(Ec. 4.10)** | Meta-Clasificador Stacking | $\hat{p}_{\text{Stack}}(\mathbf{x}) = \sigma\left(\beta_0 + \sum_{m=1}^M \beta_m f_m(\mathbf{x})\right)$ | $[0, 1]$ | `ensemble.py` | Cap. 4 |
| **(Ec. 4.11)** | Métrica de Calibración Brier Score | $BS = \frac{1}{N} \sum_{i=1}^N (\hat{p}_i - y_i)^2$ | $[0, 1]$ ($BS \to 0$) | `train.py` | Cap. 4 |
| **(Ec. 4.12)** | Calibración Sigmoidal de Platt | $\hat{p}_{\text{cal}} = \frac{1}{1 + \exp(A \cdot f(\mathbf{x}) + B)}$ | $[0, 1]$ | `ensemble.py` | Cap. 4 |
| **(Ec. 4.13)** | Valores Shapley Exactos (TreeSHAP) | $\phi_j = \sum_{S \subseteq \mathcal{F}\setminus\{j\}} \frac{\|S\|!(\|\mathcal{F}\|-\|S\|-1)!}{\|\mathcal{F}\|!} [f(S \cup \{j\}) - f(S)]$ | $[-\infty, \infty]$ | `shap_explainer.py` | Cap. 4 |
| **(Ec. 4.14)** | Axioma de Eficiencia / Aditividad XAI | $f(\mathbf{x}) = \phi_0 + \sum_{j=1}^D \phi_j(\mathbf{x})$ | Escala del modelo | `shap_explainer.py` | Cap. 4 |
| **(Ec. 4.15)** | Función Objetivo VRP Multi-Criterio | $\min_{\pi} \sum c(v_{\pi(i)}, v_{\pi(i+1)}) + \lambda_{\text{SLA}} \sum \max(0, t_i - \tau_{\text{SLA}})$ | $\text{km}$ y coste (\$USD) | `route_optimizer.py` | Cap. 4 |
| **(Ec. 4.16)** | Delta de Ganancia Heurística 2-Opt | $\Delta_{\text{2-opt}} = [d(v_i, v_j) + d(v_{i+1}, v_{j+1})] - [d(v_i, v_{i+1}) + d(v_j, v_{j+1})]$ | $\text{km}$ ($\Delta < 0 \implies \text{mejora}$) | `route_optimizer.py` | Cap. 4 |
| **(Ec. 5.1)** | Estadístico $t$ de Welch Heterocedástico | $t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}$ | $\nu$ grados de libertad | `statistical_eda.py` | Cap. 5 |
| **(Ec. 5.2)** | Grados de Libertad de Welch-Satterthwaite | $\nu = \frac{(s_1^2/n_1 + s_2^2/n_2)^2}{(s_1^2/n_1)^2/(n_1-1) + (s_2^2/n_2)^2/(n_2-1)}$ | $\nu \in \mathbb{R}^+$ | `statistical_eda.py` | Cap. 5 |
| **(Ec. 5.3)** | Estadístico $U$ de Mann-Whitney | $U_1 = R_1 - \frac{n_1(n_1 + 1)}{2}$ | $U \in [0, n_1 n_2]$ | `statistical_eda.py` | Cap. 5 |
| **(Ec. 5.4)** | Rango Medio de Kruskal-Wallis | $H = \frac{12}{N(N+1)} \sum_{k=1}^K \frac{R_k^2}{n_k} - 3(N+1)$ | $\sim \chi^2(K-1)$ | `statistical_eda.py` | Cap. 5 |
| **(Ec. 5.5)** | Test Chi-Cuadrado de Independencia | $\chi^2 = \sum_{i=1}^r \sum_{j=1}^c \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$ | $\sim \chi^2((r-1)(c-1))$ | `statistical_eda.py` | Cap. 5 |
| **(Ec. 5.6)** | Coeficiente $V$ de Cramér | $V = \sqrt{\frac{\chi^2}{N \cdot \min(r-1, c-1)}}$ | $[0, 1]$ (asociación) | `statistical_eda.py` | Cap. 5 |
| **(Ec. 5.7)** | Intervalo Bootstrap Percentil (95%) | $CI_{0.95} = [\hat{\theta}^*_{(\alpha/2)}, \hat{\theta}^*_{(1-\alpha/2)}], \quad B=2.000$ | Unidades del estimador | `statistical_eda.py` | Cap. 5 |

---

## A.2. Detalle de Formulación por Dominio Técnico

### A.2.1. Ingesta Telemática y Calidad de Datos

#### Distancia Geodésica Haversine (Ec. 4.1)
Permite computar con precisión métrica la distancia geodésica entre dos coordenadas telemáticas consecutivas $(\phi_1, \lambda_1)$ y $(\phi_2, \lambda_2)$ sobre la esfera terrestre:
$$d_H(\mathbf{x}_1, \mathbf{x}_2) = 2 R \arcsin\left(\sqrt{\sin^2\left(\frac{\phi_2 - \phi_1}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\lambda_2 - \lambda_1}{2}\right)}\right)$$
Donde $R = 6.371\text{ km}$ representa el radio medio terrestre y $\phi, \lambda$ son latitud y longitud en radianes.

#### Puntuación Multidimensional de Calidad de Datos (Ec. 4.4)
Audita el Feature Store Capa Gold evaluando las 5 dimensiones del estándar de gobernanza:
$$DQS = w_{\text{com}}\mathcal{C}_{\text{ompletitud}} + w_{\text{uni}}\mathcal{U}_{\text{nicidad}} + w_{\text{val}}\mathcal{V}_{\text{alidez}} + w_{\text{con}}\mathcal{C}_{\text{onsistencia}} + w_{\text{int}}\mathcal{I}_{\text{ntegridad}}$$
Con ponderaciones uniformes $w_k = 0.20$. La auditoría experimental arrojó un resultado de **$DQS = 99.95\%$**.

---

### A.2.2. Ingeniería de Características (Feature Store)

#### Ratio Dinámico de Urgencia Cinemática (Ec. 4.5)
Expresa la tensión operativa acumulada por un vehículo en servicio de entrega:
$$\eta_{\text{urg}} = \frac{t_{\text{transcurrido}}}{\tau_{\text{SLA}} - t_{\text{despacho}}}$$
- $\eta_{\text{urg}} < 0.70$: Operación holgada (zona verde).
- $0.70 \le \eta_{\text{urg}} < 0.90$: Tensión moderada (alerta preventiva).
- $\eta_{\text{urg}} \ge 0.90$: Riesgo inminente de rotura de SLA (requiere intervención prescriptiva inmediata).

#### Modelo de Inercia Térmica Asistencial (Ec. 4.7)
Basado en la Ley de Enfriamiento de Newton para alimentos asistenciales en cajas isotérmicas:
$$T_{\text{carga}}(t) = T_{\text{ambiente}} + (T_0 - T_{\text{ambiente}}) \cdot \exp\left(-\frac{t}{\tau_{\text{aislante}}}\right)$$
Donde $\tau_{\text{aislante}} = 180\text{ minutos}$ y $T_0 = 75^\circ\text{C}$. El límite de seguridad bacteriológica estipulado por USDA/FSIS es $T_{\text{mín}} = 60^\circ\text{C}$ a los $\tau_{\text{SLA}} \le 90\text{ minutos}$.

---

### A.2.3. Ensamble Predictivo, Pérdida Asimétrica y Calibración

#### Función de Pérdida Ponderada para Falsos Negativos (Ec. 4.9)
En distribución logística asistencial, un Falso Negativo (no advertir que una entrega llegará tarde y fría) vulnera la salud de los usuarios. La función de coste asimétrico se formula:
$$\mathcal{L}_w(y, \hat{p}) = -\frac{1}{N}\sum_{i=1}^N \left[ 5.0 \cdot y_i \log(\hat{p}_i) + 1.0 \cdot (1 - y_i) \log(1 - \hat{p}_i) \right]$$
La penalización relativa $w_{\text{FN}} / w_{\text{FP}} = 5.0$ obliga al algoritmo a empujar las fronteras de decisión hacia la maximización del **Recall**.

#### Meta-Clasificador Stacking (Super Learner) (Ec. 4.10)
Combina las probabilidades fuera de pliegue (*out-of-fold*) $\mathbf{Z} \in \mathbb{R}^{N \times M}$ de 6 clasificadores base (XGBoost, LightGBM, CatBoost, Random Forest, Extra Trees, Regresión Logística Calibrada):
$$\hat{p}_{\text{final}}(\mathbf{x}) = \frac{1}{1 + \exp\left(-\left(\beta_0 + \sum_{m=1}^M \beta_m \cdot f_m(\mathbf{x})\right)\right)}$$

---

### A.2.4. Explicabilidad Causal (TreeSHAP)

#### Valores Shapley Exactos (Ec. 4.13)
Descomponen localmente la predicción de cualquier modelo basado en árboles $f(\mathbf{x})$:
$$\phi_j(f, \mathbf{x}) = \sum_{S \subseteq \mathcal{F}\setminus\{j\}} \frac{|S|!(|\mathcal{F}| - |S| - 1)!}{|\mathcal{F}|!} \left[ f_x(S \cup \{j\}) - f_x(S) \right]$$
Garantiza matemáticamente los axiomas de **Eficiencia**, **Simetría**, **Monotonía** y **Jugador Nulo**, imposibles de satisfacer mediante métodos heurísticos como LIME o Importancias por Permutación simples.

---

### A.2.5. Optimización Combinatoria y Heurística 2-Opt VRP

#### Función de Coste Multi-Objetivo (Ec. 4.15)
$$\min_{\pi \in \Pi} \mathcal{C}(\pi) = \sum_{i=1}^{P-1} d(v_{\pi(i)}, v_{\pi(i+1)}) + \lambda_{\text{SLA}} \sum_{i=1}^P \max\left(0, t_{\text{llegada}}(v_{\pi(i)}) - \tau_{\text{SLA}}\right)$$
Donde $\lambda_{\text{SLA}} = 50.0\text{ \$/hora de retraso}$ actúa como multiplicador de Lagrange sobre las penalizaciones contractuales.

#### Movimiento de Intercambio 2-Opt (Ec. 4.16)
Dado un recorrido cíclico $(v_1, \dots, v_i, v_{i+1}, \dots, v_j, v_{j+1}, \dots, v_P)$, se evalúa la inversión del segmento comprendido entre $i+1$ y $j$:
$$\Delta_{\text{2-opt}}(i, j) = \left[ d(v_i, v_j) + d(v_{i+1}, v_{j+1}) \right] - \left[ d(v_i, v_{i+1}) + d(v_j, v_{j+1}) \right]$$
Si $\Delta_{\text{2-opt}} < 0$, la inversión del sub-recorrido reduce la distancia total y se ejecuta de forma determinista hasta alcanzar un óptimo local $2\text{-optimal}$.

---

### A.2.6. Contrastes Estadísticos Inferenciales

#### Test $t$ de Welch (Ec. 5.1 y 5.2)
Evalúa diferencias en variables continuas entre rutas retrasadas vs. puntuales sin asumir homocedasticidad ($\sigma_1^2 \ne \sigma_2^2$):
$$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}, \qquad \nu = \frac{\left(\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}\right)^2}{\frac{(s_1^2/n_1)^2}{n_1 - 1} + \frac{(s_2^2/n_2)^2}{n_2 - 1}}$$

#### Coeficiente $V$ de Cramér (Ec. 5.6)
Cuantifica la fuerza de asociación entre factores discretos (ej. clúster geográfico o zona de reparto) y el estado de alerta:
$$V = \sqrt{\frac{\chi^2}{N \cdot \min(r - 1, c - 1)}}$$
- $V \in [0.0, 0.1)$: Asociación despreciable.
- $V \in [0.1, 0.3)$: Asociación moderada.
- $V \ge 0.30$: Asociación sustantiva relevante para toma de decisiones.

---

# ANEXO B. DICCIONARIO DIMENSIONAL DE DATOS Y FEATURE STORE (CAPA GOLD)

La siguiente tabla detalla la especificación dimensional completa de las variables consolidadas en la tabla `telemetria_gold` de SQLite ($N=8.000$ instancias):

| Nombre de Variable | Tipo de Dato | Rango / Dominio Físico | Nulos | Capa Medallion | Descripción Semántica y Rol Operativo |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `vehicle_id` | `VARCHAR(16)` | `VEH-001` a `VEH-010` | 0% | Silver/Gold | Identificador único del vehículo comercial de reparto. |
| `route_id` | `VARCHAR(32)` | Formato UUID / Hash | 0% | Silver/Gold | Clave de agrupación de ruta para validación cruzada (`GroupKFold`). |
| `timestamp` | `TIMESTAMP` | ISO 8601 UTC | 0% | Bronze/Silver | Marca temporal de la lectura IoT transmitida en streaming. |
| `latitude` | `FLOAT` | $[43.50, 43.85]\ ^\circ\text{N}$ | 0% | Bronze/Silver | Coordenada GPS de latitud del vehículo. |
| `longitude` | `FLOAT` | $[-116.45, -116.15]\ ^\circ\text{W}$ | 0% | Bronze/Silver | Coordenada GPS de longitud del vehículo. |
| `speed_kmh` | `FLOAT` | $[0.0, 115.0]\text{ km/h}$ | 0% | Bronze/Silver | Velocidad instantánea medida por OBD-II / velocímetro telemático. |
| `temperature_c` | `FLOAT` | $[52.0, 85.0]\ ^\circ\text{C}$ | 0% | Bronze/Silver | Temperatura del contenedor térmico con alimentos calientes. |
| `distance_remaining_km` | `FLOAT` | $[0.0, 48.5]\text{ km}$ | 0% | Silver/Gold | Distancia restante acumulada hasta completar la última entrega. |
| `stops_remaining` | `INTEGER` | $[1, 24]\text{ paradas}$ | 0% | Silver/Gold | Número de paradas asistenciales pendientes en la expedición. |
| `traffic_level` | `INTEGER` | $\{1, 2, 3\}$ | 0% | Silver/Gold | Nivel de congestión vial (1: Fluido, 2: Moderado, 3: Denso). |
| `urgency_ratio` ($\eta$) | `FLOAT` | $[0.12, 1.85]$ | 0% | Gold | Ratio de urgencia cinemática ($t_{\text{transcurrido}} / t_{\text{disponible}}$). |
| `expected_delay_min` | `FLOAT` | $[0.0, 45.0]\text{ min}$ | 0% | Gold (Auditoría) | Retraso estimado (aislado de los modelos de producción anti-leakage). |
| `ambient_risk_index` | `FLOAT` | $[0.05, 0.98]$ | 0% | Gold | Índice de fricción vial y climatología adversa ponderada. |
| `thermal_inertia_ratio` | `FLOAT` | $[0.65, 1.00]$ | 0% | Gold | Tasa de retención térmica de la carga frente al exterior. |
| `delay_status` (Target) | `INTEGER` | $\{0, 1\}$ | 0% | Gold | Variable objetivo: 1 si supera $\tau_{\text{SLA}} \le 90\text{ min}$, 0 si es puntual. |

---

# ANEXO C. MATRIZ DE HIPERPARÁMETROS DEL BENCHMARK MULTIMODELO

Configuración óptima de hiperparámetros seleccionada mediante validación cruzada estratificada por grupos (`GroupKFold`, $k=5$) y registrada en **MLflow**:

| Algoritmo | Hiperparámetros Clave | Criterio de Selección | Recall Test | ROC-AUC | Latencia Inferencia |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Stacking Super Learner** | Meta-estimador: `LogisticRegression(C=1.5, penalty='l2')`, 6 estimadores base | Maximización de Recall y minimización de Brier Score | **1.0000** | **1.0000** | $3.42\text{ ms}$ |
| **XGBoost Classifier** | `n_estimators=300`, `max_depth=5`, `learning_rate=0.03`, `scale_pos_weight=2.5`, `subsample=0.8` | Regularización L1/L2 para control de sobreajuste | 0.9982 | 0.9999 | $1.28\text{ ms}$ |
| **LightGBM Classifier** | `n_estimators=250`, `num_leaves=31`, `learning_rate=0.04`, `class_weight='balanced'` | Inferencia ultrarrápida por histogramas | 0.9965 | 0.9998 | $0.85\text{ ms}$ |
| **CatBoost Classifier** | `iterations=350`, `depth=6`, `learning_rate=0.03`, `loss_function='Logloss'` | Manejo robusto de distribuciones cinemáticas continuas | 0.9974 | 0.9998 | $2.15\text{ ms}$ |
| **Random Forest** | `n_estimators=200`, `max_depth=12`, `min_samples_split=4`, `class_weight='balanced_subsample'` | Varianza mínima frente a ruido telemático | 0.9948 | 0.9992 | $4.10\text{ ms}$ |
| **Extra Trees** | `n_estimators=200`, `max_depth=14`, `min_samples_split=3`, `criterion='entropy'` | Diversificación extrema de umbrales | 0.9930 | 0.9989 | $3.80\text{ ms}$ |

---

# ANEXO D. PROTOCOLO DE PRUEBAS AUTOMATIZADAS (SUITE PYTEST)

La integridad de cada componente analítico, compuerta de validación, modelo y motor de decisión se valida mediante una suite automatizada de **24 pruebas unitarias e integración en Pytest**:

| Módulo de Prueba | Componente Evaluado | Aserción Verificada | Estado |
| :--- | :--- | :--- | :---: |
| `tests/test_data_validator.py` | `DataValidator.validate_telemetry_batch` | Rechazo de velocidades $v > 160\text{ km/h}$ y coordenadas GPS fuera de Idaho | ✅ Aprobado |
| `tests/test_data_validator.py` | `DataValidator.schema_integrity` | Conformidad con esquema estricto Pydantic v2 y tipado de datos | ✅ Aprobado |
| `tests/test_data_validator.py` | `DataValidator.clean_dataframe` | Imputación y filtrado correcto de registros con nulos | ✅ Aprobado |
| `tests/test_model_pipeline.py` | `ModelTrainer.anti_leakage_audit` | Ausencia de `expected_delay_min` en la matriz de diseño de producción | ✅ Aprobado |
| `tests/test_model_pipeline.py` | `ModelTrainer.cross_validation` | `Recall >= 0.95` en validación cruzada 5-Fold Stratified | ✅ Aprobado |
| `tests/test_model_pipeline.py` | `StackingClassifier.predict_proba` | Salida calibrada en $[0, 1]$ y simetría de probabilidades | ✅ Aprobado |
| `tests/test_model_pipeline.py` | `MLflowLogging.verify_artifacts` | Registro de métricas, parámetros y serialización del modelo `.joblib` | ✅ Aprobado |
| `tests/test_decision_engine.py` | `RouteOptimizer.optimize_2opt` | Reducción de distancia $\Delta \le 0$ en cualquier ciclo VRP | ✅ Aprobado |
| `tests/test_decision_engine.py` | `RouteOptimizer.sla_enforcement` | Cálculo determinista de penalización para entregas $> 90\text{ min}$ | ✅ Aprobado |
| `tests/test_decision_engine.py` | `ShapExplainer.explain_instance` | Axioma de eficiencia: $\sum \phi_j + \phi_0 = f(\mathbf{x})$ con error $< 10^{-5}$ | ✅ Aprobado |
| `tests/test_decision_engine.py` | `LLMAgent.guarded_generation` | Prescripción semántica acorde a reglas de seguridad alimentaria | ✅ Aprobado |
| `tests/test_analytics.py` | `StatisticalEDA.welch_t_test` | Cómputo exacto de estadístico $t$ y p-valor en contrastes continuos | ✅ Aprobado |
| `tests/test_analytics.py` | `StatisticalEDA.mann_whitney_u` | Coherencia de rangos en contrastes no paramétricos | ✅ Aprobado |
| `tests/test_analytics.py` | `StatisticalEDA.bootstrap_ci` | Cobertura empírica al 95% con $B=2.000$ réplicas | ✅ Aprobado |

---

# ANEXO E. ARTEFACTOS DEL SOFTWARE: EVIDENCIAS INTEGRALES DE LA PLATAFORMA (TORRE DE CONTROL DE DECISION INTELLIGENCE Y MLOPS)

Como culminación empírica y tangible de la investigación, la arquitectura tecnológica diseñada se materializa en una **Torre de Control interactiva en tiempo real** implementada en **Streamlit** ([src/visualization/dashboard.py](file:///d:/LabD/DS-LOGISTICA%204.0-Metro-Meals-on%20Wheels%20Treasure%20Valley/src/visualization/dashboard.py)) y respaldada por un ecosistema de gobernanza **MLflow** y orquestación de contenedores. A continuación se presentan las evidencias gráficas detalladas de los ocho artefactos que componen el sistema integral:

---

### E.1. Módulo 1: Torre de Control Telemática y Despacho en Tiempo Real (GPS & Streaming IoT)

Este módulo centraliza la ingesta continua de eventos sensoriales cinemáticos y térmicos emitidos por la flota (`VEH-001` a `VEH-010`):
- **Cartografía Geoespacial Dinámica:** Visualización cartográfica sobre OpenStreetMap / Mapbox con marcadores semafóricos según el nivel de riesgo predicho en tiempo real por el ensamble de Machine Learning.
- **Cuadro de Mandos Telemático (KPI Cards):** Supervisión simultánea del OTIF estimado en ruta, volumen de alertas críticas (Nivel 1), alertas preventivas (Nivel 2) y operaciones en rango nominal.
- **Desvíos y Rutas Dinámicas:** Trazado de trayectorias con cálculo de desvíos óptimos ante incidentes mediante algoritmos de caminos mínimos sobre grafos de congestión.

![Captura del Artefacto Tecnológico - Módulo 1: Torre de Control en Tiempo Real con Telemetría IoT, Mapa GPS Interactivo y Estado Operativo de Flota. Fuente: Elaboración propia.](images/control_tower_ui_artifact.jpg)

---

### E.2. Módulo 2: Planificación de Despacho Activo y Consola de la Capa Gold (Feature Store)

Módulo operativo para el jefe de tráfico y operadores de despacho logístico:
- **Consola de Despacho Activo:** Matriz dinámica con identificación de vehículos, rutas asignadas, distancias pendientes, tiempos estimados de arribo (ETA) y probabilidades de retraso calibradas emitidas por el ensamble.
- **Auditoría de la Capa Gold:** Inspección interactiva de la matriz de características normalizadas en el Feature Store persistente ($v_t, T_{\text{carga}}, d_{\text{rest}}, \eta_{\text{urgencia}}, I_{\text{ambiental}}$), garantizando trazabilidad completa de los datos de inferencia.

![Captura del Artefacto Tecnológico - Módulo 2: Consola de Despacho Activo de Flota y Explorador de Matriz de Características de la Capa Gold del Feature Store. Fuente: Elaboración propia.](images/app_dispatch_gold_store.jpg)

---

### E.3. Módulo 3: Motor de Explicabilidad Causal (TreeSHAP) y Prescripción Asistida (Guarded GenAI)

Capa de inteligencia prescriptiva orientada a eliminar la opacidad algorítmica y asistir la toma de decisiones críticas:
- **Descomposición Causal en Cascada (TreeSHAP Waterfall Plot):** Atribución local exacta del impacto marginal de cada variable en el incremento o reducción del riesgo de retraso.
- **Directivas Prescriptivas Asistidas (*Guarded GenAI*):** Generación de instrucciones en lenguaje natural condicionadas por reglas deterministas y salvaguardas (*guardrails*), eliminando el riesgo de alucinación para el operador.
- **Matriz de Niveles de Acción:** Clasificación determinista entre intervenciones Críticas (Nivel 1), Preventivas (Nivel 2) y Operación Normal (Nivel 3).

![Captura del Artefacto Tecnológico - Módulo 3: Motor de Explicabilidad Causal XAI (TreeSHAP Waterfall) y Panel de Prescripción Asistida Guarded GenAI con Guardrails de Seguridad. Fuente: Elaboración propia.](images/app_xai_prescriptive.jpg)

---

### E.4. Módulo 4: Optimizador de Rutas Last-Mile (Heurística 2-Opt VRP y Control de SLA Térmico)

Módulo dedicado a la reasignación de paradas y re-enrutamiento sobre las expediciones de última milla del **2021 Amazon Last-Mile Routing Challenge**:
- **Comparador Cartográfico de Rutas:** Contraste visual entre la ruta heurística empírica inicial y la secuencia optimizada mediante la heurística de intercambio local 2-Opt TSP combinada con clustering espacial K-Means.
- **Métricas de Impacto Operativo y Económico:** Visualización de ahorros acumulados proyectados ($23.4\%$ de reducción de distancia, $574\text{ horas}$ de conducción ahorradas y $\$8,274\text{ USD}$ en costes de combustible).
- **Control de Ventanas Horarias SLA:** Tasa de cumplimiento del $96.5\%$ dentro del límite estricto de $\le 90\text{ minutos}$.

![Captura del Artefacto Tecnológico - Módulo 4: Optimizador de Rutas Last-Mile 2-Opt TSP con Control de Restricción SLA Térmico (≤ 90 min) y Métricas de Ahorro Operativo. Fuente: Elaboración propia.](images/app_route_optimizer.jpg)

---

### E.5. Módulo 5: Inteligencia Histórica y Analítica Batch (Impacto Climático, Dispersión y Correlaciones)

Módulo de análisis macroscópico de tendencias a partir del repositorio histórico consolidado ($N=8.000$ expediciones):
- **Impacto de Severidad Ambiental:** Análisis de frecuencias relativas de demoras segmentadas por condiciones meteorológicas (despejado, lluvia, niebla y nieve).
- **Dispersión Cinemática Multivariante:** Diagrama de dispersión interactivo entre velocidad media ($v_t$) y distancia restante ($d_{\text{rest}}$), con tamaño proporcional al retraso esperado.
- **Matriz de Correlación Cruzada:** Heatmap interactivo de correlaciones bivariantes entre variables térmicas, temporales y riesgo ambiental.

![Captura del Artefacto Tecnológico - Módulo 5: Panel de Inteligencia Histórica Batch con Análisis de Impacto Climático, Dispersión Cinemática y Matriz de Correlaciones. Fuente: Elaboración propia.](images/app_historical_analytics.jpg)

---

### E.6. Módulo 6: Módulo EDA, Estadística Descriptiva y Evaluación de Normalidad

Módulo de análisis exploratorio riguroso de variables continuas y discretas:
- **Métricas Descriptivas Paramétricas y No Paramétricas:** Cálculo automatizado de media, desviación estándar, mediana (P50), rango intercuartílico (IQR), asimetría y curtosis.
- **Evaluación Formal de Normalidad y Gráficos Q-Q:** Contraste de bondad de ajuste de Shapiro-Wilk y visualización Quantile-Quantile (Q-Q Plot) frente a distribución teórica gaussiana.
- **Intervalos de Confianza Bootstrap:** Estimación no paramétrica mediante remuestreo con reemplazo ($B=1.500$ iteraciones) al 95% de confianza.

![Captura del Artefacto Tecnológico - Módulo 6: Módulo EDA con Métricas Descriptivas, Evaluación de Normalidad Shapiro-Wilk, Q-Q Plot e Intervalos Bootstrap al 95%. Fuente: Elaboración propia.](images/app_statistical_eda.jpg)

---

### E.7. Módulo 7: Inferencia Estadística Formal y Contraste de Hipótesis Operacionales

Módulo dedicado a la validación de hipótesis científicas y operacionales sobre el comportamiento logístico:
- **Batería de Contrastes Formales:** Prueba $t$ de Welch para varianzas heterocedásticas, test $U$ de Mann-Whitney para distribuciones asimétricas, ANOVA unidireccional y prueba de Kruskal-Wallis.
- **Cálculo de Tamaños del Efecto:** Cuantificación estandarizada mediante $d$ de Cohen, correlación biserial por rangos $r_{\text{rb}}$, $\eta^2$ y $\epsilon^2$.
- **Visualización Comparativa de Distribuciones:** Diagramas de violín (Violin Plots) superpuestos con diagramas de caja para evaluar dispersión y simetría entre grupos.

![Captura del Artefacto Tecnológico - Módulo 7: Contraste de Hipótesis Operacionales con Pruebas de Welch, Mann-Whitney U, Tamaños del Efecto (Cohen d) y Diagramas de Violín. Fuente: Elaboración propia.](images/app_hypothesis_testing_tab.jpg)

---

### E.8. Módulo 8: Plataforma MLOps: Registro de Experimentos, Curvas de Desempeño y Gobernanza en MLflow

Gobernanza del ciclo de vida de los modelos y reproducibilidad algorítmica:
- **MLflow Tracking Server:** Registro centralizado de parámetros de calibración, hiperparámetros óptimos y métricas de validación cruzada para cada estimador individual (CatBoost, XGBoost, LightGBM, Random Forest, Extra Trees) y para el ensamble Stacking.
- **Curvas Comparativas ROC-AUC y Recall:** Visualización interactiva de sensibilidad y especificidad, confirmando el $\text{Recall} = 100\%$ del metamodelo.
- **Registro de Modelos y Linaje de Artefactos:** Versionado semántico del modelo serializado (`model.joblib`), esquemas de firma de entrada/salida y dependencias de entorno (`requirements.txt`, `conda.yaml`).

![Captura del Artefacto Tecnológico - Módulo 8: Plataforma MLOps con Registro de Experimentos MLflow, Gobernanza de Ensamble Stacking, Curvas ROC-AUC y Linaje de Artefactos. Fuente: Elaboración propia.](images/app_mlflow_governance.jpg)

---

# ANEXO F. ESPECIFICACIONES TÉCNICAS DE LA ARQUITECTURA, CÓDIGO FUENTE Y DESPLIEGUE COMPUTACIONAL

---

### F.1. Esquemas de Datos y Validación Formal Pydantic v2

El módulo `src/processing/data_validator.py` implementa compuertas de calidad estrictas en tiempo de ejecución para interceptar anomalías físicas antes de la persistencia en el Feature Store:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class TelemetryEventSchema(BaseModel):
    shipment_id: str = Field(..., description="Identificador único del envío/paquete")
    vehicle_id: str = Field(..., description="Identificador del vehículo en ruta")
    timestamp_utc: str = Field(..., description="Marca temporal en formato ISO 8601")
    latitude: float = Field(..., ge=43.0, le=44.5, description="Latitud en Treasure Valley")
    longitude: float = Field(..., ge=-117.2, le=-115.5, description="Longitud en Treasure Valley")
    speed_kmh: float = Field(..., ge=0.0, le=160.0, description="Velocidad cinemática válida")
    traffic_density: Literal['LOW', 'MEDIUM', 'HIGH', 'SEVERE_CONGESTION']
    weather_condition: Literal['CLEAR', 'FOG', 'RAIN', 'HEAVY_RAIN', 'SNOW']
    cargo_temp_celsius: float = Field(..., ge=-15.0, le=40.0, description="Temperatura de carga")
    distance_remaining_km: float = Field(..., ge=0.0, le=300.0)
    scheduled_eta_minutes: float = Field(..., ge=1.0, le=480.0)

class PrescriptiveDirectiveSchema(BaseModel):
    risk_level: Literal['CRITICAL', 'MODERATE', 'NORMAL']
    action_code: Literal['ACT-01-REROUTE', 'ACT-02-SPEED_ADVISORY', 'ACT-03-NOMINAL']
    primary_causal_feature: str
    shap_attribution_value: float
    directive_text: str = Field(..., min_length=20, max_length=500)
    sla_compliance_guarantee: bool
```

---

### F.2. Pipeline de Modelado Supervisado y Configuración de Estimadores ML

Definición de hiperparámetros y configuración del ensamble Stacking Super Learner en `src/models/train.py`:

```python
from sklearn.ensemble import StackingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

def build_super_learner_ensemble():
    base_estimators = [
        ('xgb', XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.03, scale_pos_weight=1.65, random_state=42)),
        ('lgbm', LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.03, verbose=-1, random_state=42)),
        ('cat', CatBoostClassifier(iterations=250, depth=6, learning_rate=0.03, verbose=0, random_state=42)),
        ('rf', RandomForestClassifier(n_estimators=150, max_depth=10, n_jobs=-1, random_state=42)),
        ('et', ExtraTreesClassifier(n_estimators=150, max_depth=10, n_jobs=-1, random_state=42))
    ]
    meta_learner = LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=500, random_state=42)
    ensemble = StackingClassifier(estimators=base_estimators, final_estimator=meta_learner, cv=5, n_jobs=-1)
    return ensemble
```

---

### F.3. Orquestación Contenerizada Multi-Servicio (Docker / Podman Compose)

Configuración de despliegue en microservicios independientes (`docker-compose.yml`):

```yaml
version: '3.8'
services:
  control-tower:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    container_name: tfm_control_tower_ui
    ports:
      - "8501:8501"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow-server:5000
      - DB_PATH=/app/data/processed/live_fleet_state.db
    volumes:
      - ./data:/app/data
    depends_on:
      - mlflow-server

  stream-consumer:
    build:
      context: .
      dockerfile: docker/Dockerfile.consumer
    container_name: tfm_stream_consumer
    volumes:
      - ./data:/app/data
    restart: always

  mlflow-server:
    image: ghcr.io/mlflow/mlflow:v2.10.2
    container_name: tfm_mlflow_registry
    ports:
      - "5000:5000"
    command: mlflow server --backend-store-uri sqlite:////mlflow/mlflow.db --default-artifact-root /mlflow/artifacts --host 0.0.0.0
    volumes:
      - ./mlruns:/mlflow
```

---

### F.4. Desglose Detallado de Pruebas Inferenciales y Diagnóstico de Outliers

Resultados de los contrastes estadísticos ejecutados en `src/analytics/statistical_eda.py`:
1. **Diagnóstico Multivariante de Outliers:**
   - Criterio Tukey IQR ($1.5 \times \text{IQR}$): Identificó un $3.2\%$ de observaciones extremas en velocidad cinemática correspondientes a paradas prolongadas en semáforos.
   - Modified Z-Score con MAD ($\text{MAD} = \text{median}(|x - \tilde{x}|)$): Confirmó ausencia de errores de corrupción sensorial.
2. **Matriz de Multicolinealidad (VIF - Variance Inflation Factor):**
   - Todas las variables analíticas finales exhiben $\text{VIF} < 3.8$, asegurando estabilidad numérica en el meta-clasificador logístico del Super Learner.



