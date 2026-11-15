from __future__ import annotations

import calendar
import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from matplotlib.path import Path

from src.stats_engine import TrendResult


PLOTLY_LAYOUT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(11, 22, 42, 0.0)",
    plot_bgcolor="rgba(6, 13, 26, 0.55)",
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    margin=dict(l=44, r=18, t=28, b=36),
    hovermode="x unified",
)
REGION_COORDS: dict[str, tuple[str, float, float]] = {
    "mean_north_india": ("North India", 30.5, 77.5),
    "mean_west_india": ("West India", 23.2, 71.2),
    "mean_central_india": ("Central India", 22.4, 79.2),
    "mean_east_india": ("East India", 24.5, 87.2),
    "mean_south_india": ("South India", 13.0, 77.8),
}


def plot_india_regional_map(df: pd.DataFrame, unit: str = "mm/hr") -> go.Figure:
    """Interactive India regional precipitation map using Plotly Scattergeo."""
    lats, lons, names, vals, texts = [], [], [], [], []
    for col, (label, lat, lon) in REGION_COORDS.items():
        if col in df.columns:
            mean_v = float(df[col].mean())
            lats.append(lat)
            lons.append(lon)
            names.append(label)
            vals.append(mean_v)
            texts.append(f"<b>{label}</b><br>Mean: {mean_v:.4f} {unit}")

    if not vals:
        numeric_cols = [c for c in df.columns if c != "date" and pd.api.types.is_numeric_dtype(df[c])]
        if numeric_cols:
            col = "mean_GPM_3IMERGM_07_precipitation" if "mean_GPM_3IMERGM_07_precipitation" in numeric_cols else numeric_cols[0]
            mean_v = float(df[col].mean())
            lats.append(22.5)
            lons.append(79.5)
            names.append("All India")
            vals.append(mean_v)
            texts.append(f"<b>All India</b><br>Mean: {mean_v:.4f} {unit}")

    fig = go.Figure()
    
    if vals:
        max_v = max(vals) if max(vals) > 0 else 1.0
        sizes = [12 + 12 * (v / max_v) for v in vals]
        fig.add_trace(
            go.Scattergeo(
                lat=lats,
                lon=lons,
                text=names,
                hovertext=texts,
                hoverinfo="text",
                mode="markers+text",
                textposition="top center",
                textfont=dict(color="#F8FAFC", size=11),
                marker=dict(
                    size=sizes,
                    color=vals,
                    colorscale=[[0.0, "#1D4ED8"], [0.45, "#06B6D4"], [0.8, "#10B981"], [1.0, "#FACC15"]],
                    colorbar=dict(
                        title=dict(text=unit, font=dict(size=11)),
                        thickness=12,
                        len=0.75,
                    ),
                    line=dict(width=1.4, color="#F8FAFC"),
                    opacity=0.92,
                ),
            )
        )

    fig.update_geos(
        scope="asia",
        center=dict(lat=21.8, lon=79.5),
        projection_scale=4.3,
        showland=True,
        landcolor="#0F2342",
        showocean=True,
        oceancolor="#060D1A",
        showcountries=True,
        countrycolor="rgba(56, 189, 248, 0.38)",
        showcoastlines=True,
        coastlinecolor="rgba(56, 189, 248, 0.45)",
        bgcolor="rgba(6, 13, 26, 0.0)",
    )
    fig.update_layout(
        paper_bgcolor="rgba(11, 22, 42, 0.0)",
        font=dict(family="Inter, sans-serif", color="#E2E8F0", size=11),
        margin=dict(l=4, r=4, t=6, b=4),
        height=295,
    )
    return fig


def plot_overview_series(
    df: pd.DataFrame,
    col: str,
    label: str,
    unit: str = "mm/hr",
) -> go.Figure:
    """Clean glowing cyan time series with dashed long-term mean for Overview Bento."""
    clean = df[["date", col]].dropna().sort_values("date")
    long_mean = float(clean[col].mean())

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=clean["date"],
            y=clean[col],
            mode="lines",
            name="Monthly Precipitation",
            line=dict(color="#22D3EE", width=1.8),
            fill="tozeroy",
            fillcolor="rgba(34, 211, 238, 0.08)",
        )
    )
    fig.add_hline(
        y=long_mean,
        line_dash="dash",
        line_color="#CBD5E1",
        line_width=1.4,
        annotation_text=f"Long-term Mean ({long_mean:.4f})",
        annotation_position="top right",
        annotation_font=dict(color="#CBD5E1", size=11),
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        xaxis_title="Year",
        yaxis_title=f"Precipitation ({unit})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=295,
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.10)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.12)")
    return fig


def plot_seasonal_profile_bars(
    climatology: pd.DataFrame,
    col: str,
    unit: str = "mm/hr",
) -> go.Figure:
    """Climatological monthly profile bar chart (Jan-Dec) for Overview Bento."""
    months = [calendar.month_abbr[m] for m in climatology.index]
    vals = climatology[col]

    fig = go.Figure(
        data=go.Bar(
            x=months,
            y=vals,
            marker=dict(
                color=vals,
                colorscale=[[0.0, "#0E7490"], [0.5, "#06B6D4"], [1.0, "#2DD4BF"]],
                line=dict(color="rgba(45, 212, 191, 0.5)", width=1),
            ),
            name="Monthly Mean",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        xaxis_title="",
        yaxis_title=f"Mean ({unit})",
        height=275,
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.06)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.12)")
    return fig


def plot_time_series(
    df: pd.DataFrame,
    col: str,
    result: TrendResult,
    ma_window: int = 12,
    unit: str = "mm/hr",
    trend_mode: str = "Both (Theil-Sen & OLS)",
) -> go.Figure:
    """Interactive time series with moving average and trend line(s)."""
    clean = df[["date", col]].dropna().sort_values("date").copy()
    clean["ma"] = clean[col].rolling(window=ma_window, min_periods=max(2, ma_window // 2)).mean()
    t_years = (clean["date"] - clean["date"].iloc[0]).dt.days.to_numpy(dtype=float) / 365.25

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=clean["date"],
            y=clean[col],
            mode="lines",
            name="Monthly Observation",
            line=dict(color="rgba(148, 163, 184, 0.55)", width=1.3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=clean["date"],
            y=clean["ma"],
            mode="lines",
            name=f"{ma_window}-Month Moving Avg",
            line=dict(color="#22D3EE", width=2.8),
        )
    )

    if trend_mode in ("Theil-Sen Robust", "Both (Theil-Sen & OLS)"):
        ts_y = result.theil_intercept + result.theil_slope_per_year * t_years
        fig.add_trace(
            go.Scatter(
                x=clean["date"],
                y=ts_y,
                mode="lines",
                name=f"Theil-Sen Trend ({result.theil_slope_per_decade:+.4f}/dec)",
                line=dict(color="#F59E0B", width=2.3, dash="dash"),
            )
        )

    if trend_mode in ("OLS Linear", "Both (Theil-Sen & OLS)"):
        ols_y = result.ols_intercept + result.ols_slope_per_year * t_years
        fig.add_trace(
            go.Scatter(
                x=clean["date"],
                y=ols_y,
                mode="lines",
                name=f"OLS Linear Trend ({result.ols_slope_per_decade:+.4f}/dec)",
                line=dict(color="#34D399", width=2.0, dash="dot"),
            )
        )

    fig.update_layout(
        **{**PLOTLY_LAYOUT_BASE, "margin": dict(l=44, r=18, t=78, b=36)},
        title=f"{result.label} — Monthly Time Series & Long-Term Trend",
        xaxis_title="Date",
        yaxis_title=f"Value ({unit})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=400,
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.12)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.12)")
    return fig


def plot_monthly_anomalies(
    anomaly_df: pd.DataFrame,
    col: str,
    label: str,
    unit: str = "mm/hr",
) -> go.Figure:
    """Interactive diverging bar chart of monthly anomalies relative to calendar-month mean."""
    vals = anomaly_df[col]
    colors = np.where(vals >= 0, "#22D3EE", "#FB7185")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=anomaly_df["date"],
            y=vals,
            marker_color=colors,
            name="Monthly Anomaly",
        )
    )
    fig.add_hline(y=0, line_width=1.2, line_color="#94A3B8")
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=f"{label} — Monthly Anomalies (Seasonal Cycle Removed)",
        xaxis_title="Date",
        yaxis_title=f"Anomaly ({unit})",
        height=350,
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.10)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.12)")
    return fig


def plot_seasonal_climatology(climatology: pd.DataFrame, cols: list[str], label_fn, unit: str = "mm/hr") -> go.Figure:
    """Plot 12-month seasonal cycle across selected regions."""
    months = [calendar.month_abbr[m] for m in climatology.index]
    palette = ["#22D3EE", "#F59E0B", "#34D399", "#A78BFA", "#FB7185", "#FBBF24"]

    fig = go.Figure()
    for idx, col in enumerate(cols):
        fig.add_trace(
            go.Scatter(
                x=months,
                y=climatology[col],
                mode="lines+markers",
                name=label_fn(col),
                line=dict(width=2.5, color=palette[idx % len(palette)]),
                marker=dict(size=6),
            )
        )
    fig.update_layout(
        **{**PLOTLY_LAYOUT_BASE, "margin": dict(l=44, r=18, t=78, b=36)},
        title="Seasonal Cycle (Calendar-Month Climatology)",
        xaxis_title="Month",
        yaxis_title=f"Mean ({unit})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=380,
    )
    return fig


def plot_anomaly_heatmap(
    anomaly_df: pd.DataFrame,
    col: str,
    label: str,
    unit: str = "mm/hr",
    compact: bool = False,
) -> go.Figure:
    """Year x Month heatmap of monthly anomalies."""
    temp = anomaly_df[["date", col]].copy()
    temp["year"] = temp["date"].dt.year
    temp["month"] = temp["date"].dt.month
    pivot = temp.pivot(index="year", columns="month", values=col).sort_index()
    month_labels = [calendar.month_abbr[m] for m in pivot.columns]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=month_labels,
            y=pivot.index.astype(str),
            colorscale="RdBu",
            zmid=0,
            colorbar=dict(title=unit, thickness=12),
        )
    )
    fig.update_layout(
        **{**PLOTLY_LAYOUT_BASE, "hovermode": "closest"},
        title=None if compact else f"{label} — Year × Month Anomaly Heatmap",
        xaxis_title="" if compact else "Month",
        yaxis_title="" if compact else "Year",
        height=275 if compact else 430,
    )
    return fig


def plot_annual_anomalies(annual_anom: pd.DataFrame, col: str, label: str, unit: str = "mm/hr") -> go.Figure:
    """Bar chart of complete-calendar-year anomalies."""
    vals = annual_anom[col]
    colors = np.where(vals >= 0, "#34D399", "#F97316")
    fig = go.Figure(
        data=go.Bar(
            x=annual_anom.index.astype(str),
            y=vals,
            marker_color=colors,
            name="Annual Anomaly",
        )
    )
    fig.add_hline(y=0, line_width=1.2, line_color="#94A3B8")
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=f"{label} — Complete-Year Annual Anomalies",
        xaxis_title="Calendar Year (12 Complete Months)",
        yaxis_title=f"Annual Anomaly ({unit})",
        height=350,
        showlegend=False,
    )
    return fig


def plot_regional_slope_comparison(comp_df: pd.DataFrame) -> go.Figure:
    """Compare Theil-Sen decade slopes across regions colored by significance."""
    sorted_df = comp_df.sort_values("Theil-Sen (/decade)")
    sig_col = [c for c in sorted_df.columns if c.startswith("Significant")][0]
    colors = np.where(sorted_df[sig_col] == "Yes", "#22D3EE", "#60A5FA")

    fig = go.Figure(
        data=go.Bar(
            x=sorted_df["Theil-Sen (/decade)"],
            y=sorted_df["Region / Series"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(147, 197, 253, 0.7)", width=1),
            ),
            text=[f"{v:+.5f}" for v in sorted_df["Theil-Sen (/decade)"]],
            textposition="outside",
        )
    )
    fig.add_vline(x=0, line_width=1.2, line_color="#94A3B8")
    fig.update_layout(
        **{
            **PLOTLY_LAYOUT_BASE,
            "hovermode": "closest",
            "margin": dict(l=44, r=70, t=42, b=36),
        },
        title="Cross-Region Theil-Sen Trend Rate (per Decade) — Cyan = Significant | Light Blue = Not Significant",
        xaxis_title="Rate of Change per Decade",
        yaxis_title="",
        height=360,
    )
    return fig


def export_highres_timeseries_png(
    df: pd.DataFrame,
    col: str,
    result: TrendResult,
    ma_window: int = 12,
    unit: str = "mm/hr",
) -> bytes:
    """Generate a 300 DPI publication-ready Matplotlib figure using Object-Oriented API."""
    clean = df[["date", col]].dropna().sort_values("date").copy()
    clean["ma"] = clean[col].rolling(window=ma_window, min_periods=max(2, ma_window // 2)).mean()
    t_years = (clean["date"] - clean["date"].iloc[0]).dt.days.to_numpy(dtype=float) / 365.25
    ts_y = result.theil_intercept + result.theil_slope_per_year * t_years

    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=300)
    ax.plot(clean["date"], clean[col], color="#64748b", linewidth=1.0, alpha=0.65, label="Monthly Observation")
    ax.plot(clean["date"], clean["ma"], color="#2b5c8f", linewidth=2.2, label=f"{ma_window}-Month Moving Avg")
    ax.plot(
        clean["date"],
        ts_y,
        color="#d95f02",
        linestyle="--",
        linewidth=2.0,
        label=f"Theil-Sen Trend ({result.theil_slope_per_decade:+.5f} {unit}/decade)",
    )

    sig_txt = "Statistically Significant" if result.is_significant else "Not Statistically Significant"
    ax.set_title(
        f"{result.label} — {sig_txt} (Seasonal MK p = {result.smk_p_value:.4f})",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel(f"Value ({unit})", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(frameon=True, loc="upper left")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
