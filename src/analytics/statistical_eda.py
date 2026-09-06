"""
Motor Analítico de Estadística Descriptiva e Inferencial (EDA Engine)
Proporciona análisis paramétrico, no paramétrico, contraste de hipótesis,
pruebas de normalidad, tamaño del efecto (Cohen's d, Cramér's V) y diagnóstico de outliers.
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats

class StatisticalEDAEngine:
    """
    Motor estadístico para análisis exploratorio, descriptivo e inferencial en Logística 4.0.
    """

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha

    def compute_descriptive_metrics(
        self, 
        df: pd.DataFrame, 
        numeric_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calcula un conjunto exhaustivo de estadísticas descriptivas paramétricas y no paramétricas.
        """
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        metrics_list = []
        for col in numeric_cols:
            series = df[col].dropna()
            n = len(series)
            if n == 0:
                continue

            mean = series.mean()
            std = series.std(ddof=1) if n > 1 else 0.0
            variance = series.var(ddof=1) if n > 1 else 0.0
            median = series.median()
            trimmed_mean = stats.trim_mean(series, proportiontocut=0.10)
            
            q25 = series.quantile(0.25)
            q75 = series.quantile(0.75)
            iqr = q75 - q25
            
            min_val = series.min()
            max_val = series.max()
            val_range = max_val - min_val
            
            skewness = series.skew()
            kurtosis = series.kurtosis()
            cv = (std / mean * 100.0) if mean != 0 else np.nan

            # Intervalo de confianza del 95% para la media (t-Student)
            if n > 1 and std > 0:
                se = std / np.sqrt(n)
                ci_margin = stats.t.ppf(1 - self.alpha / 2, df=n - 1) * se
                ci_lower = mean - ci_margin
                ci_upper = mean + ci_margin
            else:
                ci_lower = mean
                ci_upper = mean

            metrics_list.append({
                "Variable": col,
                "Observaciones (N)": n,
                "Media (Mean)": round(mean, 3),
                "Media Recortada 10%": round(trimmed_mean, 3),
                "Mediana (Median)": round(median, 3),
                "Desv. Estándar (Std)": round(std, 3),
                "Varianza (Var)": round(variance, 3),
                "Rango Intercuartil (IQR)": round(iqr, 3),
                "Mínimo (Min)": round(min_val, 3),
                "Máximo (Max)": round(max_val, 3),
                "Rango": round(val_range, 3),
                "Asimetría (Skewness)": round(skewness, 3),
                "Curtosis (Kurtosis)": round(kurtosis, 3),
                "Coef. Variación (%)": round(cv, 2) if not np.isnan(cv) else "N/A",
                "IC 95% Media [Inferior]": round(ci_lower, 3),
                "IC 95% Media [Superior]": round(ci_upper, 3)
            })

        return pd.DataFrame(metrics_list)

    def test_normality(self, series: pd.Series) -> Dict[str, Any]:
        """
        Ejecuta pruebas de normalidad (Shapiro-Wilk, D'Agostino-Pearson y Kolmogorov-Smirnov).
        """
        clean_series = series.dropna()
        n = len(clean_series)
        
        results = {"sample_size": n, "tests": {}}

        if n < 3:
            results["is_normal"] = False
            results["conclusion"] = "Muestra insuficiente (N < 3)"
            return results

        # 1. Shapiro-Wilk (limitado a N<=5000 por restricción del algoritmo)
        sample_for_shapiro = clean_series if n <= 5000 else clean_series.sample(5000, random_state=42)
        shapiro_stat, shapiro_p = stats.shapiro(sample_for_shapiro)
        results["tests"]["Shapiro-Wilk"] = {
            "statistic": round(float(shapiro_stat), 4),
            "p_value": float(shapiro_p),
            "is_normal": bool(shapiro_p > self.alpha)
        }

        # 2. D'Agostino-Pearson (K^2)
        if n >= 8:
            k2_stat, k2_p = stats.normaltest(clean_series)
            results["tests"]["DAgostino-Pearson"] = {
                "statistic": round(float(k2_stat), 4),
                "p_value": float(k2_p),
                "is_normal": bool(k2_p > self.alpha)
            }

        # 3. Kolmogorov-Smirnov frente a Normal empírica
        mean, std = float(clean_series.mean()), float(clean_series.std())
        if std > 0:
            try:
                arr = np.asarray(clean_series, dtype=float)
                ks_stat, ks_p = stats.kstest(arr, stats.norm(loc=mean, scale=std).cdf)
                results["tests"]["Kolmogorov-Smirnov"] = {
                    "statistic": round(float(ks_stat), 4),
                    "p_value": float(ks_p),
                    "is_normal": bool(ks_p > self.alpha)
                }
            except Exception:
                try:
                    std_arr = (np.asarray(clean_series, dtype=float) - mean) / std
                    ks_stat, ks_p = stats.kstest(std_arr, 'norm')
                    results["tests"]["Kolmogorov-Smirnov"] = {
                        "statistic": round(float(ks_stat), 4),
                        "p_value": float(ks_p),
                        "is_normal": bool(ks_p > self.alpha)
                    }
                except Exception:
                    pass

        # Conclusión combinada (criterio de Shapiro-Wilk)
        is_normal = results["tests"]["Shapiro-Wilk"]["is_normal"]
        results["is_normal"] = is_normal
        results["conclusion"] = (
            f"Se asume distribución NORMAL (p = {shapiro_p:.4f} > {self.alpha})"
            if is_normal else
            f"Se RECHAZA normalidad (p = {shapiro_p:.4e} <= {self.alpha}). Usar métodos no paramétricos."
        )

        return results

    def test_two_groups_difference(
        self, 
        df: pd.DataFrame, 
        group_col: str, 
        value_col: str, 
        group_val1: Any = 0, 
        group_val2: Any = 1
    ) -> Dict[str, Any]:
        """
        Compara dos muestras independientes mediante Welch's t-test y Mann-Whitney U test,
        calculando los tamaños del efecto (Cohen's d y Rank-Biserial r).
        """
        g1 = df[df[group_col] == group_val1][value_col].dropna()
        g2 = df[df[group_col] == group_val2][value_col].dropna()

        n1, n2 = len(g1), len(g2)
        if n1 < 2 or n2 < 2:
            return {"error": "Muestra insuficiente en uno de los grupos."}

        mean1, mean2 = g1.mean(), g2.mean()
        std1, std2 = g1.std(ddof=1), g2.std(ddof=1)
        med1, med2 = g1.median(), g2.median()

        # 1. Welch's t-test (Varianzas heterogéneas)
        t_stat, t_pval = stats.ttest_ind(g1, g2, equal_var=False)

        # Cohen's d (Pooled Std)
        pooled_std = np.sqrt(((n1 - 1) * (std1**2) + (n2 - 1) * (std2**2)) / (n1 + n2 - 2)) if (n1 + n2 - 2) > 0 else 1.0
        cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0.0

        if abs(cohens_d) < 0.2:
            d_magnitude = "Efecto Insignificante"
        elif abs(cohens_d) < 0.5:
            d_magnitude = "Efecto Pequeño"
        elif abs(cohens_d) < 0.8:
            d_magnitude = "Efecto Moderado"
        else:
            d_magnitude = "Efecto Grande"

        # 2. Mann-Whitney U test (No paramétrico)
        u_stat, u_pval = stats.mannwhitneyu(g1, g2, alternative='two-sided')
        
        # Rank-Biserial Correlation r = 1 - (2U / (n1 * n2))
        rank_biserial_r = 1.0 - (2.0 * u_stat / (n1 * n2)) if (n1 * n2) > 0 else 0.0

        # Decisión formal
        reject_h0 = bool(u_pval < self.alpha)
        decision_text = (
            f"Diferencia ESTADÍSTICAMENTE SIGNIFICATIVA (p = {u_pval:.4e} < {self.alpha}). Se rechaza H0."
            if reject_h0 else
            f"No existe evidencia de diferencia significativa (p = {u_pval:.4f} >= {self.alpha}). Se mantiene H0."
        )

        return {
            "variable": value_col,
            "group_column": group_col,
            "group_1": {"label": str(group_val1), "n": n1, "mean": round(mean1, 3), "std": round(std1, 3), "median": round(med1, 3)},
            "group_2": {"label": str(group_val2), "n": n2, "mean": round(mean2, 3), "std": round(std2, 3), "median": round(med2, 3)},
            "welch_t_test": {
                "t_statistic": round(float(t_stat), 4),
                "p_value": float(t_pval),
                "cohens_d": round(float(cohens_d), 4),
                "effect_magnitude": d_magnitude
            },
            "mann_whitney_u_test": {
                "u_statistic": round(float(u_stat), 4),
                "p_value": float(u_pval),
                "rank_biserial_r": round(float(rank_biserial_r), 4)
            },
            "reject_null_hypothesis": reject_h0,
            "decision": decision_text
        }

    def test_multi_group_difference(
        self, 
        df: pd.DataFrame, 
        cat_col: str, 
        num_col: str
    ) -> Dict[str, Any]:
        """
        Evalúa diferencias entre múltiples grupos usando One-Way ANOVA y Kruskal-Wallis H-test.
        Calcula Eta-cuadrado (Eta^2) y Epsilon-cuadrado (Epsilon^2).
        """
        groups = [group[num_col].dropna().values for _, group in df.groupby(cat_col) if len(group[num_col].dropna()) > 0]
        group_names = [str(name) for name, group in df.groupby(cat_col) if len(group[num_col].dropna()) > 0]
        
        k = len(groups)
        total_n = sum(len(g) for g in groups)

        if k < 2 or total_n < 5:
            return {"error": "Número insuficiente de categorías o datos para prueba multi-grupo."}

        # 1. One-Way ANOVA
        f_stat, anova_p = stats.f_oneway(*groups)
        
        # Eta-squared (SS_between / SS_total)
        grand_mean = np.mean(np.concatenate(groups))
        ss_between = sum(len(g) * ((np.mean(g) - grand_mean)**2) for g in groups)
        ss_total = sum(np.sum((g - grand_mean)**2) for g in groups)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0.0

        # 2. Kruskal-Wallis H-Test
        h_stat, kw_p = stats.kruskal(*groups)
        
        # Epsilon-squared (H - k + 1) / (N - k)
        epsilon_squared = (h_stat - k + 1) / (total_n - k) if (total_n - k) > 0 else 0.0
        epsilon_squared = max(0.0, min(1.0, epsilon_squared))

        # Desglose de medias por grupo
        group_stats = []
        for name, g in zip(group_names, groups):
            group_stats.append({
                "Categoria": name,
                "N": len(g),
                "Media": round(float(np.mean(g)), 3),
                "Mediana": round(float(np.median(g)), 3),
                "Desv. Est": round(float(np.std(g, ddof=1)), 3)
            })

        reject_h0 = bool(kw_p < self.alpha)

        return {
            "categorical_column": cat_col,
            "numeric_column": num_col,
            "groups_count": k,
            "total_observations": total_n,
            "group_breakdown": pd.DataFrame(group_stats),
            "anova": {
                "f_statistic": round(float(f_stat), 4),
                "p_value": float(anova_p),
                "eta_squared": round(float(eta_squared), 4)
            },
            "kruskal_wallis": {
                "h_statistic": round(float(h_stat), 4),
                "p_value": float(kw_p),
                "epsilon_squared": round(float(epsilon_squared), 4)
            },
            "reject_null_hypothesis": reject_h0,
            "conclusion": (
                f"Existen diferencias estadísticamente significativas entre los niveles de {cat_col} (Kruskal-Wallis p = {kw_p:.4e} < {self.alpha})."
                if reject_h0 else
                f"No se detectan diferencias significativas entre las categorías de {cat_col} (p = {kw_p:.4f} >= {self.alpha})."
            )
        }

    def test_chi_square_association(
        self, 
        df: pd.DataFrame, 
        col1: str, 
        col2: str
    ) -> Dict[str, Any]:
        """
        Prueba Chi-cuadrado de Independencia para dos variables categóricas.
        Calcula la V de Cramér para medir la fuerza de asociación.
        """
        contingency_table = pd.crosstab(df[col1], df[col2])
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

        n = contingency_table.sum().sum()
        r, k = contingency_table.shape
        min_dim = min(r - 1, k - 1)
        
        # V de Cramér
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if (n * min_dim) > 0 else 0.0

        if cramers_v < 0.10:
            strength = "Asociación Débil / Nula"
        elif cramers_v < 0.30:
            strength = "Asociación Moderada"
        else:
            strength = "Asociación Fuerte"

        # Residuos Estandarizados (Obs - Exp) / sqrt(Exp)
        expected_df = pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns)
        residuals_df = (contingency_table - expected_df) / np.sqrt(expected_df)

        reject_h0 = bool(p_val < self.alpha)

        return {
            "variable_1": col1,
            "variable_2": col2,
            "observed_table": contingency_table,
            "expected_table": expected_df.round(2),
            "standardized_residuals": residuals_df.round(2),
            "chi2_statistic": round(float(chi2), 4),
            "degrees_of_freedom": int(dof),
            "p_value": float(p_val),
            "cramers_v": round(float(cramers_v), 4),
            "association_strength": strength,
            "reject_null_hypothesis": reject_h0,
            "conclusion": (
                f"Existe asociación estadísticamente significativa entre {col1} y {col2} (Chi^2 = {chi2:.2f}, p = {p_val:.4e}, V = {cramers_v:.3f} [{strength}])."
                if reject_h0 else
                f"Las variables {col1} y {col2} son independientes (Chi^2 = {chi2:.2f}, p = {p_val:.4f} >= {self.alpha})."
            )
        }

    def compute_correlation_with_pvalues(
        self, 
        df: pd.DataFrame, 
        numeric_cols: Optional[List[str]] = None, 
        method: str = "pearson"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calcula la matriz de correlación (Pearson, Spearman o Kendall) junto con su matriz de p-valores.
        """
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        n_vars = len(numeric_cols)
        corr_matrix = np.zeros((n_vars, n_vars))
        pval_matrix = np.zeros((n_vars, n_vars))

        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i == j:
                    corr_matrix[i, j] = 1.0
                    pval_matrix[i, j] = 0.0
                else:
                    s1 = df[col1].dropna()
                    s2 = df[col2].dropna()
                    idx = s1.index.intersection(s2.index)
                    
                    if len(idx) > 2:
                        if method == "spearman":
                            r, p = stats.spearmanr(s1[idx], s2[idx])
                        elif method == "kendall":
                            r, p = stats.kendalltau(s1[idx], s2[idx])
                        else:
                            r, p = stats.pearsonr(s1[idx], s2[idx])
                            
                        corr_matrix[i, j] = round(float(r), 4)
                        pval_matrix[i, j] = float(p)
                    else:
                        corr_matrix[i, j] = np.nan
                        pval_matrix[i, j] = np.nan

        df_corr = pd.DataFrame(corr_matrix, index=numeric_cols, columns=numeric_cols)
        df_pval = pd.DataFrame(pval_matrix, index=numeric_cols, columns=numeric_cols)
        return df_corr, df_pval

    def detect_outliers(
        self, 
        df: pd.DataFrame, 
        numeric_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Diagnostica observaciones atípicas mediante el método de Tukey (IQR) y Z-Score (|Z| > 3.0).
        """
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        outlier_records = []
        for col in numeric_cols:
            series = df[col].dropna()
            n = len(series)
            if n == 0:
                continue

            # Método IQR
            q25 = series.quantile(0.25)
            q75 = series.quantile(0.75)
            iqr = q75 - q25
            lower_fence = q25 - (1.5 * iqr)
            upper_fence = q75 + (1.5 * iqr)
            
            iqr_outliers = series[(series < lower_fence) | (series > upper_fence)]
            iqr_count = len(iqr_outliers)
            iqr_pct = (iqr_count / n) * 100.0

            # Método Z-Score
            mean, std = series.mean(), series.std(ddof=1)
            if std > 0:
                z_scores = np.abs((series - mean) / std)
                z_outliers = series[z_scores > 3.0]
                z_count = len(z_outliers)
                z_pct = (z_count / n) * 100.0
            else:
                z_count, z_pct = 0, 0.0

            # Impacto en la media al remover outliers IQR
            mean_without_outliers = series[(series >= lower_fence) & (series <= upper_fence)].mean()
            delta_mean = mean - mean_without_outliers if not np.isnan(mean_without_outliers) else 0.0

            outlier_records.append({
                "Variable": col,
                "Límite Inf (IQR)": round(lower_fence, 2),
                "Límite Sup (IQR)": round(upper_fence, 2),
                "Outliers (IQR)": iqr_count,
                "% Outliers (IQR)": round(iqr_pct, 2),
                "Outliers (|Z| > 3)": z_count,
                "% Outliers (Z-Score)": round(z_pct, 2),
                "Media Original": round(mean, 2),
                "Media sin Outliers": round(mean_without_outliers, 2) if not np.isnan(mean_without_outliers) else "N/A",
                "Impacto en Media (Δμ)": round(delta_mean, 3)
            })

        return pd.DataFrame(outlier_records)

    def bootstrap_mean_ci(
        self, 
        series: pd.Series, 
        n_iterations: int = 2000, 
        ci: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Calcula el intervalo de confianza de la media mediante Bootstrap no paramétrico empírico.
        """
        clean = series.dropna().values
        n = len(clean)
        if n == 0:
            return 0.0, 0.0, 0.0

        np.random.seed(42)
        bootstrap_means = np.empty(n_iterations)
        for i in range(n_iterations):
            sample = np.random.choice(clean, size=n, replace=True)
            bootstrap_means[i] = np.mean(sample)

        alpha_half = (1.0 - ci) / 2.0
        lower = float(np.percentile(bootstrap_means, alpha_half * 100.0))
        upper = float(np.percentile(bootstrap_means, (1.0 - alpha_half) * 100.0))
        point_estimate = float(np.mean(clean))

        return round(point_estimate, 3), round(lower, 3), round(upper, 3)

if __name__ == "__main__":
    engine = StatisticalEDAEngine()
    test_df = pd.DataFrame({
        "speed": np.random.normal(50, 15, 200),
        "delay_min": np.random.exponential(10, 200),
        "status": np.random.choice([0, 1], p=[0.7, 0.3], size=200),
        "weather": np.random.choice(["CLEAR", "RAIN", "SNOW"], size=200)
    })
    desc = engine.compute_descriptive_metrics(test_df)
    print("--- Métricas Descriptivas ---")
    print(desc[["Variable", "Media (Mean)", "Mediana (Median)", "Desv. Estándar (Std)", "Asimetría (Skewness)"]])
    
    ttest_res = engine.test_two_groups_difference(test_df, "status", "speed", 0, 1)
    print("\n--- Welch's & Mann-Whitney Test ---")
    print(ttest_res["decision"])
