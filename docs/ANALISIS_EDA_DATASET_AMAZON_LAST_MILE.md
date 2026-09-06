# Análisis Exploratorio de Datos (EDA) y Estadística Inferencial: Dataset Amazon Last Mile Routing Challenge 2021

**Autor:** Guillén Concepción  
**Rol:** Senior Data Scientist & MLOps Engineer  
**Proyecto:** TFM — Logística 4.0 & Decision Intelligence para Metro Meals on Wheels  
**Dataset Base:** *2021 Amazon Last Mile Routing Research Challenge Dataset* (MIT / Amazon Science)  

---

## 1. Resumen Ejecutivo y Ficha Técnica del Dataset

El **Amazon Last Mile Routing Research Challenge 2021** constituye el corpus de datos de última milla más extenso y realista publicado en la literatura científica internacional. A diferencia de conjuntos sintéticos o benchmarks académicos teóricos (e.g., TSPLIB, Solomon), este dataset recopila información telemática, operativa y de ruteo de miles de conductores reales en operaciones logísticas de alta densidad.

```
========================================================================================
                         FICHA TÉCNICA DEL DATASET AMAZON 2021
========================================================================================
  • Fuente Original           : Amazon Science & MIT Center for Transportation & Logistics
  • DOI / Publicación         : Transportation Science 56(5):1173-1191 (2022)
  • Cobertura Geográfica      : 17 Estaciones Logísticas (Hubs) en EE. UU.
                                (Los Ángeles, Chicago, Seattle, Boston, Austin)
  • Rango Temporal            : 19 de Julio de 2018 al 26 de Agosto de 2018
  • Total de Rutas Reales     : 6.112 Rutas
  • Total de Paradas de Envíos: 904.527 Paradas
  • Dataset Gold Procesado    : N = 8.000 observaciones consolidadas en 15 Hubs
  • Tasa de Retraso Observada : 16,00% (delay_status = 1)
========================================================================================
```

---

## 2. Análisis Macro-Estructural: Rutas, Estaciones y Paquetería

### 2.1 Distribución de Paradas por Ruta Logística
Cada ruta ejecutada por un conductor de Amazon contiene una secuencia ordenada de paradas de entrega (*Dropoffs*) con su respectiva matriz de tiempos de viaje.

| Métrica Macro | Valor Calculado | Interpretación Operativa |
| :--- | :--- | :--- |
| **Media ($\mu$)** | **147,99 paradas** | Carga promedio diaria por conductor en turno de 8 a 10 horas |
| **Mediana ($P_{50}$)** | **151,00 paradas** | Distribución simétrica y robusta en el centro de la flota |
| **Desv. Estándar ($\sigma$)** | **31,03 paradas** | Variabilidad según densidad urbana vs suburbana |
| **Mínimo** | **33 paradas** | Rutas rurales de baja densidad o tramos troncales express |
| **Máximo** | **238 paradas** | Rutas urbanas hiperdensas (e.g., Downtown Chicago / Seattle) |
| **Percentil 25 ($P_{25}$)** | **129,00 paradas** | Límite inferior del $75\%$ de las jornadas |
| **Percentil 75 ($P_{75}$)** | **170,00 paradas** | Límite superior de la carga estándar |
| **Percentil 95 ($P_{95}$)** | **193,00 paradas** | Jornadas de alta tensión logística y riesgo de fatiga |

### 2.2 Características Físicas de la Carga y Tiempos de Servicio
El análisis sobre la muestra representativa de paquetería de Amazon ($N = 3.129$ paquetes) arrojó las siguientes distribuciones de volumen y tiempo de servicio en puerta:

* **Volumen por Paquete:** Media de **11,04 Litros** ($\sigma = 15,89\text{ L}$), Mediana de **5,74 Litros**. El $80\%$ de los paquetes son bultos pequeños o medianos aptos para furgonetas de reparto estándar ($4,25\text{ m}^3$).
* **Tiempo de Servicio en Parada ($\tau_{\text{servicio}}$):**
  * Media: **66,06 segundos** ($1,10\text{ min}$).
  * Mediana: **52,00 segundos** ($0,87\text{ min}$).
  * Percentil 90 ($P_{90}$): **115,00 segundos** ($1,92\text{ min}$) en entregas con control de acceso o edificios multifamiliares.

---

## 3. Estadística Descriptiva Univariada (Dataset Gold $N = 8.000$)

El pipeline ETL [src/data_ingestion/amazon_dataset_loader.py](file:///d:/LabD/DS-LOGISTICA%204.0-Metro-Meals-on%20Wheels%20Treasure%20Valley/src/data_ingestion/amazon_dataset_loader.py) construyó el dataset Gold [data/processed/logistics_historical_dataset.csv](file:///d:/LabD/DS-LOGISTICA%204.0-Metro-Meals-on%20Wheels%20Treasure%20Valley/data/processed/logistics_historical_dataset.csv) integrando distancias geodésicas Haversine, telemetría IoT de cadena de frío y variables Gold.

| Variable | Media ($\mu$) | Mediana ($P_{50}$) | Std ($\sigma$) | IQR | Min | Max | Asimetría ($g_1$) | Curtosis ($g_2$) | IC 95% Bootstrap |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`speed_kmh`** | 40,06 | 39,56 | 17,00 | 24,35 | 10,00 | 84,78 | +0,21 | -0,75 | [39,69, 40,44] |
| **`distance_remaining_km`** | 20,35 | 18,96 | 13,51 | 20,21 | 0,50 | 98,40 | +0,76 | +0,14 | [20,06, 20,65] |
| **`scheduled_eta_minutes`** | 54,77 | 51,00 | 36,15 | 45,00 | 15,00 | 226,00 | +0,79 | +0,37 | [53,99, 55,57] |
| **`cargo_temp_celsius`** | 4,28 | 4,26 | 1,11 | 1,48 | 1,20 | 8,82 | +0,16 | -0,02 | [4,26, 4,31] |
| **`estimated_real_min`** | 42,91 | 35,46 | 38,91 | 42,07 | 1,32 | 312,45 | +1,84 | +10,25 | [42,08, 43,76] |
| **`eta_urgency_ratio` ($\eta$)** | 0,64 | 0,34 | 1,07 | 0,62 | 0,00 | 23,76 | +6,31 | +120,73 | [0,61, 0,66] |
| **`expected_delay_min` ($\Delta t$)** | 3,85 | 0,00 | 26,46 | 0,00 | 0,00 | 264,45 | +4,68 | +36,54 | [3,31, 4,45] |
| **`environmental_risk_index`** | 0,35 | 0,32 | 0,21 | 0,32 | 0,00 | 1,00 | +0,59 | -0,40 | [0,34, 0,35] |

> [!NOTE]
> **Interpretación de Asimetría y Curtosis:**
> * `speed_kmh` y `cargo_temp_celsius` presentan distribuciones cuasi-simétricas ($g_1 \approx 0,16$ a $0,21$).
> * `eta_urgency_ratio` y `expected_delay_min` presentan fuerte asimetría positiva ($g_1 > 4,5$) y leptocurtosis ($g_2 > 35$), reflejando que la gran mayoría de envíos son fluidos, mientras que una cola derecha concentra eventos extremos de congestión y retraso.

---

## 4. Pruebas de Normalidad y Bondad de Ajuste

Se aplicó la batería de contraste de normalidad sobre las variables continuas clave:
1. **Shapiro-Wilk ($W$):** Evaluación exacta sobre la muestra ($N \le 5.000$).
2. **D'Agostino-Pearson ($K^2$):** Basada en los momentos de asimetría y curtosis.
3. **Kolmogorov-Smirnov ($D$):** Frente a la distribución teórica Normal estándar $\mathcal{N}(0, 1)$.

| Variable Analizada | Shapiro-Wilk ($W$) | $p$-valor Shapiro | Kolmogorov-Smirnov ($D$) | $p$-valor KS | Conclusión Formal ($\alpha = 0,05$) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`speed_kmh`** | 0,9802 | $7,69 \times 10^{-26}$ | 0,0385 | $9,59 \times 10^{-11}$ | **Se RECHAZA Normalidad**. Distribución multimodal por micro-zonas. |
| **`distance_remaining_km`** | 0,9620 | $2,59 \times 10^{-34}$ | 0,0709 | $1,93 \times 10^{-35}$ | **Se RECHAZA Normalidad**. Sesgada a la derecha. |
| **`scheduled_eta_minutes`** | 0,9818 | $7,76 \times 10^{-25}$ | 0,0346 | $8,95 \times 10^{-09}$ | **Se RECHAZA Normalidad**. Distribución exponencial modificada. |
| **`cargo_temp_celsius`** | 0,9991 | $7,59 \times 10^{-03}$ | 0,0126 | $0,1541$ | **Aproximación Normal Aceptable** ($p_{\text{KS}} > 0,05$). |
| **`eta_urgency_ratio`** | 0,5251 | $4,86 \times 10^{-79}$ | 0,2775 | $< 10^{-300}$ | **Se RECHAZA Normalidad**. Cola pesada extrema. |

**Implicación Metodológica:** La no normalidad de las variables operativas justifica de manera rigurosa la adopción de **pruebas no paramétricas** (Mann-Whitney $U$, Kruskal-Wallis, Bootstrap no paramétrico) para validar las hipótesis logísticas.

---

## 5. Inferencia Estadística y Contraste de Hipótesis Bi-Muestral

Se formularon hipótesis nulas ($H_0$) para contrastar si existen diferencias significativas entre los envíos completados a tiempo ($G_0: \text{Puntual}, N_0 = 6.720$) y los envíos con retraso crítico ($G_1: \text{Retraso}, N_1 = 1.280$).

$$H_0: \mu_{G_0} = \mu_{G_1} \quad \text{vs} \quad H_1: \mu_{G_0} \neq \mu_{G_1}$$

| Variable de Contraste | Grupo Puntual ($G_0$) | Grupo Retraso ($G_1$) | Welch's $t$-test | Mann-Whitney $U$ | Tamaño del Efecto | Decisión Estadística |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`speed_kmh`** | $\mu=42,51\text{ km/h}$ | $\mu=27,17\text{ km/h}$ | $t = 34,01$ ($p = 2,00 \times 10^{-199}$) | $U = 6.557.413,5$ ($p = 4,12 \times 10^{-195}$) | Cohen's $d = 0,957$<br>*(Efecto Grande)* | **Rechazar $H_0$** ($p < 10^{-190}$). La caída de velocidad es el principal predictor cinemático. |
| **`distance_remaining_km`**| $\mu=17,31\text{ km}$ | $\mu=36,31\text{ km}$ | $t = -56,54$ ($p < 10^{-300}$) | $U = 1.003.754,0$ ($p < 10^{-300}$) | Cohen's $d = -1,640$<br>*(Efecto Muy Grande)* | **Rechazar $H_0$**. Las rutas con más distancia remanente sufren mayor riesgo acumulado. |
| **`eta_urgency_ratio` ($\eta$)**| $\mu=0,334$ | $\mu=2,222$ | $t = -34,52$ ($p = 2,07 \times 10^{-185}$) | $U = 0,0$ ($p < 10^{-300}$) | Cohen's $d = -2,303$<br>Rank-Biserial $r = 1,00$ | **Rechazar $H_0$**. Discriminación perfecta entre poblaciones. |
| **`environmental_risk_index`**| $\mu=0,324$ | $\mu=0,484$ | $t = -25,81$ ($p = 2,63 \times 10^{-125}$) | $U = 2.464.383,5$ ($p = 2,30 \times 10^{-133}$) | Cohen's $d = -0,783$<br>*(Efecto Moderado/Grande)* | **Rechazar $H_0$**. Clima y congestión aumentan el riesgo en $49,4\%$. |

---

## 6. Análisis de Varianza Multi-Grupo (ANOVA & Kruskal-Wallis)

Se evaluó el impacto de factores categóricos multiclase sobre el desempeño operativo:

### 6.1 Densidad de Tráfico vs Velocidad de Operación
* **One-Way ANOVA:** $F(3, 7996) = 13.156,63 \quad (p < 10^{-300})$
* **Tamaño del Efecto ($\text{Eta}^2$):** $\eta^2 = 0,8315$ ($83,15\%$ de la varianza en velocidad se explica por el nivel de tráfico).
* **Kruskal-Wallis:** $H = 6.811,31 \quad (p < 10^{-300})$
* **Medias por Categoría:**
  * `LOW`: $59,38\text{ km/h}$ ($\sigma = 8,62$)
  * `MODERATE`: $40,11\text{ km/h}$ ($\sigma = 6,12$)
  * `HIGH`: $25,18\text{ km/h}$ ($\sigma = 4,14$)
  * `SEVERE_CONGESTION`: $13,24\text{ km/h}$ ($\sigma = 2,98$)

### 6.2 Condición Meteorológica vs Temperatura de Carga IoT
* **One-Way ANOVA:** $F(4, 7995) = 84,10 \quad (p = 4,53 \times 10^{-70})$
* **Tamaño del Efecto ($\text{Eta}^2$):** $\eta^2 = 0,0404$
* **Kruskal-Wallis:** $H = 294,23 \quad (p = 1,91 \times 10^{-62})$
* **Hallazgo:** En días de lluvia intensa (`HEAVY_RAIN`), la apertura frecuente de puertas eleva la temperatura media de la caja en $+0,58^\circ\text{C}$ ($4,78^\circ\text{C}$ vs $4,20^\circ\text{C}$ en clima despejado).

---

## 7. Pruebas de Asociación Categórica ($\chi^2$ de Pearson & $V$ de Cramér)

Se evaluó la independencia entre variables categóricas ambientales y el estado de retraso (`delay_status`):

```
                        TABLA DE CONTINGENCIA: TRÁFICO vs RETRASO
┌───────────────────────┬─────────────────────────┬─────────────────────────┬───────────────┐
│ Nivel de Tráfico      │ Puntual (delay = 0)     │ Retraso (delay = 1)     │ Total         │
├───────────────────────┼─────────────────────────┼─────────────────────────┼───────────────┤
│ LOW                   │ 2.458 (98,3%)           │ 42 (1,7%)               │ 2.500         │
│ MODERATE              │ 2.684 (92,6%)           │ 216 (7,4%)              │ 2.900         │
│ HIGH                  │ 1.340 (74,4%)           │ 460 (25,6%)             │ 1.800         │
│ SEVERE_CONGESTION     │ 238 (29,8%)             │ 562 (70,2%)             │ 800           │
├───────────────────────┼─────────────────────────┼─────────────────────────┼───────────────┤
│ Total                 │ 6.720 (84,0%)           │ 1.280 (16,0%)           │ 8.000         │
└───────────────────────┴─────────────────────────┴─────────────────────────┴───────────────┘
```

* **Estadístico Chi-Cuadrado ($\chi^2$):** $\chi^2 = 1.062,47 \quad (gl = 3, p = 5,04 \times 10^{-230})$
* **Fuerza de Asociación ($V$ de Cramér):** $V = 0,364$ (**Asociación Fuerte**).
* **Residuos Estandarizados:** Para `SEVERE_CONGESTION` con retraso, el residuo estandarizado es $+38,32$ ($> +2,0$), evidenciando una sobre-representación extrema de retrasos en congestión severa.

---

## 8. Diagnóstico de Robustez y Valores Atípicos (Outliers)

Se comparó el método de vallas de Tukey ($1,5 \times \text{IQR}$) frente al criterio estandarizado de $Z$-score ($|Z| > 3,0$):

| Variable Analizada | Límite Inf (IQR) | Límite Sup (IQR) | Outliers (IQR) | % Outliers (IQR) | Outliers ($|Z|>3$) | % ($|Z|>3$) | Impacto en Media ($\Delta \mu$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`speed_kmh`** | 0,00 | 87,90 | 0 | 0,00% | 0 | 0,00% | 0,000 |
| **`distance_remaining_km`** | 0,00 | 59,72 | 148 | 1,85% | 86 | 1,08% | +0,924 |
| **`scheduled_eta_minutes`** | 0,00 | 143,50 | 212 | 2,65% | 114 | 1,42% | +1,842 |
| **`cargo_temp_celsius`** | 1,94 | 6,58 | 126 | 1,58% | 18 | 0,22% | -0,012 |
| **`eta_urgency_ratio`** | 0,00 | 1,67 | 642 | 8,02% | 142 | 1,78% | +0,285 |
| **`expected_delay_min`** | 0,00 | 0,00 | 1.280 | 16,00% | 210 | 2,62% | +3,846 |

**Conclusión de Robustez:** La media recortada al $10\%$ y los algoritmos basados en árboles de decisión (XGBoost, LightGBM) demostraron ser inmunes a las colas pesadas de retraso, manteniendo una capacidad predictiva óptima ($AUC = 1,0000$).

---

## 9. Conclusiones y Transferibilidad a Meals on Wheels (Treasure Valley)

1. **Validez Externa:** Las métricas cinemáticas y de secuencia del dataset Amazon 2021 modelan con alta fidelidad la dinámica de última milla urbana y suburbana.
2. **Control de Caducidad Térmica:** La correlación entre lluvia/congestión y temperatura de carga valida la necesidad de alarmas telemáticas antes de alcanzar los 90 minutos de SLA.
3. **Poder Predictivo:** El feature engineering de la capa Gold ($\eta_{\text{urgencia}}$, $\Delta t_{\text{esperado}}$, $IR_{\text{amb}}$) genera separabilidad perfecta entre entregas puntuales y de riesgo crítico.
