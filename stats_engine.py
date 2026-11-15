from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import linregress, norm, t as student_t, theilslopes


@dataclass
class TrendResult:
    column: str
    label: str
    n_obs: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    mean_val: float
    median_val: float
    std_val: float
    min_val: float
    max_val: float
    ols_slope_per_year: float
    ols_slope_per_decade: float
    ols_intercept: float
    ols_r2: float
    ols_t_stat: float
    ols_p_value: float
    ols_ci_low_per_year: float
    ols_ci_high_per_year: float
    theil_slope_per_year: float
    theil_slope_per_decade: float
    theil_intercept: float
    theil_ci_low_per_year: float
    theil_ci_high_per_year: float
    smk_s: float
    smk_z: float
    smk_p_value: float
    smk_direction: str
    is_significant: bool
    alpha: float
    pct_change_total: float


def compute_descriptive_stats(df: pd.DataFrame, cols: list[str], label_fn) -> pd.DataFrame:
    """Compute regional descriptive statistics table."""
    rows = []
    for col in cols:
        series = df[col].dropna()
        rows.append(
            {
                "Region / Series": label_fn(col),
                "Mean": float(series.mean()),
                "Median": float(series.median()),
                "Min": float(series.min()),
                "Max": float(series.max()),
                "Std Dev": float(series.std(ddof=1)),
                "Observations": int(series.count()),
            }
        )
    return pd.DataFrame(rows)


def compute_monthly_anomalies(df: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute calendar-month climatology and monthly anomalies (value - month mean)."""
    work = df.copy()
    work["month"] = work["date"].dt.month
    climatology = work.groupby("month")[cols].mean()

    anomaly_df = work[["date", "month"]].copy()
    for col in cols:
        clim_series = work.groupby("month")[col].transform("mean")
        anomaly_df[col] = work[col] - clim_series
    return climatology, anomaly_df


def compute_annual_summary(df: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate annual means and annual anomalies strictly for complete 12-month years."""
    work = df.copy()
    work["year"] = work["date"].dt.year
    counts = work.groupby("year")["date"].count()
    complete_years = counts[counts == 12].index.tolist()
    complete_df = work[work["year"].isin(complete_years)]

    annual_mean = complete_df.groupby("year")[cols].mean()
    annual_anom = annual_mean - annual_mean.mean()
    return annual_mean, annual_anom


def seasonal_mann_kendall(dates: pd.Series, values: pd.Series) -> tuple[float, float, float, str]:
    """
    Hirsch, Slack & Smith (1982) Seasonal Mann-Kendall test for monthly data.
    Handles ties in each calendar month season cleanly without external dependencies.
    """
    temp = pd.DataFrame({"date": dates, "val": values}).dropna().sort_values("date")
    temp["month"] = temp["date"].dt.month

    total_s = 0.0
    total_var_s = 0.0

    for m in range(1, 13):
        x = temp.loc[temp["month"] == m, "val"].to_numpy(dtype=float)
        n = len(x)
        if n < 2:
            continue

        # Pairwise sign sum for season m
        s_m = 0.0
        for i in range(n - 1):
            diffs = x[i + 1 :] - x[i]
            s_m += float(np.sum(np.sign(diffs)))
        total_s += s_m

        # Variance with tie correction
        _, tie_counts = np.unique(x, return_counts=True)
        tie_term = float(np.sum(tie_counts * (tie_counts - 1) * (2 * tie_counts + 5)))
        var_m = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0
        total_var_s += var_m

    if total_var_s <= 0:
        return total_s, 0.0, 1.0, "No trend"

    if total_s > 0:
        z = (total_s - 1.0) / np.sqrt(total_var_s)
        direction = "Increasing"
    elif total_s < 0:
        z = (total_s + 1.0) / np.sqrt(total_var_s)
        direction = "Decreasing"
    else:
        z = 0.0
        direction = "No trend"

    p_val = float(2.0 * (1.0 - norm.cdf(abs(z))))
    return float(total_s), float(z), p_val, direction


def analyze_series_trend(
    df: pd.DataFrame,
    col: str,
    label: str,
    alpha: float = 0.05,
) -> TrendResult:
    """Run full statistical trend & significance analysis for one series."""
    clean = df[["date", col]].dropna().sort_values("date").reset_index(drop=True)
    dates = clean["date"]
    y = clean[col].to_numpy(dtype=float)
    n = len(y)

    # Time axis in fractional years from start
    t_years = (dates - dates.iloc[0]).dt.days.to_numpy(dtype=float) / 365.25

    # 1. OLS Linear Regression + Student's t-test + 95% CI
    reg = linregress(t_years, y)
    df_dof = max(n - 2, 1)
    t_crit = float(student_t.ppf(1.0 - alpha / 2.0, df_dof))
    ols_t_stat = float(reg.slope / reg.stderr) if reg.stderr > 0 else 0.0
    ci_half = t_crit * float(reg.stderr)

    # 2. Theil-Sen Robust Median Slope + 95% CI
    ts_res = theilslopes(y, t_years, alpha=1.0 - alpha)

    # 3. Seasonal Mann-Kendall Test
    smk_s, smk_z, smk_p, smk_dir = seasonal_mann_kendall(dates, clean[col])

    is_sig = smk_p < alpha
    span_years = max(float(t_years[-1] - t_years[0]), 1e-6)
    mean_v = float(np.mean(y))
    pct_change = (float(ts_res.slope) * span_years / mean_v * 100.0) if abs(mean_v) > 1e-12 else 0.0

    return TrendResult(
        column=col,
        label=label,
        n_obs=n,
        start_date=dates.iloc[0],
        end_date=dates.iloc[-1],
        mean_val=mean_v,
        median_val=float(np.median(y)),
        std_val=float(np.std(y, ddof=1)),
        min_val=float(np.min(y)),
        max_val=float(np.max(y)),
        ols_slope_per_year=float(reg.slope),
        ols_slope_per_decade=float(reg.slope * 10.0),
        ols_intercept=float(reg.intercept),
        ols_r2=float(reg.rvalue ** 2),
        ols_t_stat=ols_t_stat,
        ols_p_value=float(reg.pvalue),
        ols_ci_low_per_year=float(reg.slope - ci_half),
        ols_ci_high_per_year=float(reg.slope + ci_half),
        theil_slope_per_year=float(ts_res.slope),
        theil_slope_per_decade=float(ts_res.slope * 10.0),
        theil_intercept=float(ts_res.intercept),
        theil_ci_low_per_year=float(ts_res.low_slope),
        theil_ci_high_per_year=float(ts_res.high_slope),
        smk_s=smk_s,
        smk_z=smk_z,
        smk_p_value=smk_p,
        smk_direction=smk_dir,
        is_significant=is_sig,
        alpha=alpha,
        pct_change_total=pct_change,
    )


def build_regional_comparison_table(
    df: pd.DataFrame,
    cols: list[str],
    label_fn,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Compile a cross-region statistical comparison table."""
    records: list[dict[str, Any]] = []
    for col in cols:
        res = analyze_series_trend(df, col, label_fn(col), alpha=alpha)
        records.append(
            {
                "Region / Series": res.label,
                "Direction": res.smk_direction,
                "Theil-Sen (/yr)": res.theil_slope_per_year,
                "Theil-Sen (/decade)": res.theil_slope_per_decade,
                "OLS Slope (/decade)": res.ols_slope_per_decade,
                "OLS p-value": res.ols_p_value,
                "Seasonal MK Z": res.smk_z,
                "Seasonal MK p-value": res.smk_p_value,
                f"Significant (α={alpha:.2f})": "Yes" if res.is_significant else "No",
            }
        )
    return pd.DataFrame(records)
