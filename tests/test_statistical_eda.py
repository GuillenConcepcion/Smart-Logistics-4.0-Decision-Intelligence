import pytest
import numpy as np
import pandas as pd
from src.analytics.statistical_eda import StatisticalEDAEngine

@pytest.fixture
def eda_engine():
    return StatisticalEDAEngine(alpha=0.05)

@pytest.fixture
def sample_statistical_df():
    np.random.seed(42)
    n = 300
    speed_ontime = np.random.normal(65.0, 10.0, 200)
    speed_delayed = np.random.normal(35.0, 12.0, 100)
    
    speeds = np.concatenate([speed_ontime, speed_delayed])
    status = np.array([0] * 200 + [1] * 100)
    
    # Clima con asociación intencional a retraso
    weather = []
    for s in status:
        if s == 0:
            weather.append(np.random.choice(["CLEAR", "FOG", "RAIN"], p=[0.7, 0.2, 0.1]))
        else:
            weather.append(np.random.choice(["CLEAR", "FOG", "RAIN"], p=[0.2, 0.3, 0.5]))
            
    df = pd.DataFrame({
        "speed_kmh": speeds,
        "delay_status": status,
        "weather_condition": weather,
        "distance_km": np.random.uniform(10, 150, n),
        "expected_delay_min": np.where(status == 1, np.random.exponential(25, n), 0.0)
    })
    return df

def test_compute_descriptive_metrics(eda_engine, sample_statistical_df):
    metrics_df = eda_engine.compute_descriptive_metrics(sample_statistical_df, ["speed_kmh", "distance_km"])
    assert len(metrics_df) == 2
    assert "Media (Mean)" in metrics_df.columns
    assert "Mediana (Median)" in metrics_df.columns
    assert "Rango Intercuartil (IQR)" in metrics_df.columns
    assert "IC 95% Media [Inferior]" in metrics_df.columns
    assert "IC 95% Media [Superior]" in metrics_df.columns
    
    speed_row = metrics_df[metrics_df["Variable"] == "speed_kmh"].iloc[0]
    assert 50.0 <= speed_row["Media (Mean)"] <= 60.0
    assert speed_row["IC 95% Media [Inferior]"] < speed_row["Media (Mean)"] < speed_row["IC 95% Media [Superior]"]

def test_normality_tests(eda_engine):
    np.random.seed(42)
    normal_data = pd.Series(np.random.normal(100, 15, 500))
    res_normal = eda_engine.test_normality(normal_data)
    assert res_normal["is_normal"] is True

    skewed_data = pd.Series(np.random.exponential(5, 500))
    res_skewed = eda_engine.test_normality(skewed_data)
    assert res_skewed["is_normal"] is False

def test_two_groups_difference(eda_engine, sample_statistical_df):
    res = eda_engine.test_two_groups_difference(sample_statistical_df, "delay_status", "speed_kmh", 0, 1)
    assert res["reject_null_hypothesis"] is True
    assert res["welch_t_test"]["p_value"] < 0.001
    assert res["mann_whitney_u_test"]["p_value"] < 0.001
    assert abs(res["welch_t_test"]["cohens_d"]) > 0.8  # Efecto grande
    assert res["welch_t_test"]["effect_magnitude"] == "Efecto Grande"

def test_multi_group_difference(eda_engine, sample_statistical_df):
    res = eda_engine.test_multi_group_difference(sample_statistical_df, "weather_condition", "speed_kmh")
    assert res["groups_count"] == 3
    assert "anova" in res
    assert "kruskal_wallis" in res
    assert "group_breakdown" in res
    assert len(res["group_breakdown"]) == 3

def test_chi_square_association(eda_engine, sample_statistical_df):
    res = eda_engine.test_chi_square_association(sample_statistical_df, "weather_condition", "delay_status")
    assert res["reject_null_hypothesis"] is True
    assert res["p_value"] < 0.05
    assert res["cramers_v"] > 0.10
    assert "observed_table" in res
    assert "expected_table" in res
    assert "standardized_residuals" in res

def test_correlation_with_pvalues(eda_engine, sample_statistical_df):
    cols = ["speed_kmh", "distance_km", "expected_delay_min"]
    df_corr, df_pval = eda_engine.compute_correlation_with_pvalues(sample_statistical_df, cols, method="pearson")
    assert df_corr.shape == (3, 3)
    assert df_pval.shape == (3, 3)
    assert np.allclose(np.diag(df_corr), 1.0)
    assert np.allclose(np.diag(df_pval), 0.0)

def test_detect_outliers(eda_engine):
    data = [10.0] * 100 + [9999.0, -9999.0]
    df = pd.DataFrame({"val": data})
    outliers_df = eda_engine.detect_outliers(df, ["val"])
    assert len(outliers_df) == 1
    assert outliers_df.iloc[0]["Outliers (IQR)"] == 2
    assert outliers_df.iloc[0]["% Outliers (IQR)"] > 0.0

def test_bootstrap_mean_ci(eda_engine):
    np.random.seed(42)
    series = pd.Series(np.random.normal(50.0, 10.0, 200))
    pt, low, high = eda_engine.bootstrap_mean_ci(series, n_iterations=1000, ci=0.95)
    assert low < pt < high
    assert 45.0 <= low <= 55.0
