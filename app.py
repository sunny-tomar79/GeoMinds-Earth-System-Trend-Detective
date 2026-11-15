from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import (
    export_highres_timeseries_png,
    plot_annual_anomalies,
    plot_anomaly_heatmap,
    plot_india_regional_map,
    plot_monthly_anomalies,
    plot_overview_series,
    plot_regional_slope_comparison,
    plot_seasonal_climatology,
    plot_seasonal_profile_bars,
    plot_time_series,
)
from src.content import (
    DEMO_INVESTIGATIONS,
    NASA_PARTNER_RESOURCES,
    VARIABLE_GLOSSARY,
    get_next_investigation_prompts,
)
from src.data_loader import (
    format_series_label,
    load_builtin_dataset,
    load_csv_bytes,
    run_data_quality_audit,
)
from src.stats_engine import (
    analyze_series_trend,
    build_regional_comparison_table,
    compute_annual_summary,
    compute_descriptive_stats,
    compute_monthly_anomalies,
)

st.set_page_config(
    page_title="RainfallScope India | Regional Precipitation Trend Explorer",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# NASA Mission-Control Bento CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at 88% 8%, rgba(34, 211, 238, 0.10), transparent 35%),
                    radial-gradient(circle at 10% 90%, rgba(224, 49, 49, 0.08), transparent 32%),
                    #060D1A;
    }
    .block-container {
        padding-top: 1.15rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071122 0%, #050B16 100%);
        border-right: 1px solid rgba(56, 189, 248, 0.16);
    }
    .nasa-brand {
        border-left: 4px solid #E03131;
        padding-left: 0.75rem;
        margin-bottom: 1rem;
    }
    .nasa-brand-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .nasa-brand-sub {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 0.15rem;
    }
    .hero-wrap {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        background: linear-gradient(135deg, rgba(11, 22, 42, 0.92) 0%, rgba(12, 34, 64, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 12px;
        padding: 1.05rem 1.35rem;
        margin-bottom: 0.85rem;
    }
    .hero-h1 {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        color: #F8FAFC;
        margin: 0;
    }
    .hero-p {
        font-size: 0.88rem;
        color: #CBD5E1;
        margin: 0.2rem 0 0 0;
    }
    .mission-pill {
        white-space: nowrap;
        font-size: 0.78rem;
        font-weight: 600;
        color: #E0F2FE;
        background: rgba(14, 116, 144, 0.35);
        border: 1px solid rgba(34, 211, 238, 0.5);
        border-radius: 999px;
        padding: 0.4rem 0.9rem;
    }
    .kpi-tile {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        background: rgba(11, 22, 42, 0.88);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 12px;
        padding: 0.8rem 0.95rem;
    }
    .kpi-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        background: rgba(34, 211, 238, 0.12);
        border: 1px solid rgba(34, 211, 238, 0.3);
        flex-shrink: 0;
    }
    .kpi-meta-label {
        font-size: 0.74rem;
        color: #94A3B8;
        margin-bottom: 0.1rem;
    }
    .kpi-meta-val {
        font-size: 1.08rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .kpi-meta-sub {
        font-size: 0.72rem;
        color: #64748B;
    }
    .card-title-bar {
        border-left: 3px solid #E03131;
        padding-left: 0.55rem;
        font-size: 0.94rem;
        font-weight: 650;
        color: #F1F5F9;
        margin-bottom: 0.45rem;
    }
    .status-badge {
        border-radius: 8px;
        padding: 0.55rem 0.75rem;
        font-size: 0.84rem;
        font-weight: 600;
        margin: 0.45rem 0 0.7rem 0;
    }
    .status-pending {
        background: rgba(245, 158, 11, 0.14);
        border: 1px solid rgba(245, 158, 11, 0.45);
        color: #FDE68A;
    }
    .status-sig {
        background: rgba(34, 211, 238, 0.14);
        border: 1px solid rgba(34, 211, 238, 0.5);
        color: #A5F3FC;
    }
    .status-nonsig {
        background: rgba(148, 163, 184, 0.14);
        border: 1px solid rgba(148, 163, 184, 0.4);
        color: #E2E8F0;
    }
    .verdict-box {
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.75rem 0 1rem 0;
        border-left: 5px solid #F59E0B;
        background: rgba(245, 158, 11, 0.10);
        border-top: 1px solid rgba(245, 158, 11, 0.22);
        border-right: 1px solid rgba(245, 158, 11, 0.22);
        border-bottom: 1px solid rgba(245, 158, 11, 0.22);
    }
    .verdict-box.sig {
        border-left-color: #22D3EE;
        background: rgba(34, 211, 238, 0.10);
        border-top-color: rgba(34, 211, 238, 0.25);
        border-right-color: rgba(34, 211, 238, 0.25);
        border-bottom-color: rgba(34, 211, 238, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SEASON_MONTHS: dict[str, list[int]] = {
    "All Seasons": list(range(1, 13)),
    "Monsoon (Jun–Sep)": [6, 7, 8, 9],
    "Post-Monsoon (Oct–Nov)": [10, 11],
    "Winter (Dec–Feb)": [12, 1, 2],
    "Pre-Monsoon (Mar–May)": [3, 4, 5],
}

if "trend_analyzed" not in st.session_state:
    st.session_state.trend_analyzed = False
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Overview"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="nasa-brand">
            <div class="nasa-brand-title">RainfallScope India</div>
            <div class="nasa-brand-sub">Regional Precipitation Trend Explorer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "📈 Precipitation Trends",
            "📅 Seasonal Patterns",
            "⚠️ Anomalies",
            "📊 Trend Detection",
            "🗂️ Data & Methodology",
        ],
        key="nav_page",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Dataset Source**")
    dataset_choice = st.selectbox(
        "Built-in Datasets",
        [
            "Combined (5 Indian Regions + All India)",
            "All Indian Regions (Regional CSV)",
            "All India (NASA Giovanni GPM IMERG)",
        ],
        label_visibility="collapsed",
    )

    uploaded_file = st.file_uploader(
        "Upload CSV (Standard or Giovanni)",
        type=["csv"],
        help="Upload any regional time-series CSV or NASA Giovanni CSV export.",
    )

if uploaded_file is not None:
    df_raw, meta = load_csv_bytes(uploaded_file.getvalue(), uploaded_file.name)
else:
    df_raw, meta = load_builtin_dataset(dataset_choice)

value_cols: list[str] = meta["value_columns"]
if not value_cols:
    st.error("No numeric variable columns found in the selected CSV.")
    st.stop()

audit = run_data_quality_audit(df_raw, value_cols, meta.get("invalid_dates", 0))
unit_short = meta.get("unit", "mm/hr")

with st.sidebar:
    st.markdown("---")
    period_str = f"{audit['start_date'].strftime('%b %Y')} – {audit['end_date'].strftime('%b %Y')}"
    q_text = "Clean Series" if audit["is_clean"] else "Check Missing/Fill"
    st.caption(f"**Period:** {period_str}")
    st.caption(f"**Records:** {audit['row_count']} monthly obs • **Quality:** {q_text}")


# ---------------------------------------------------------------------------
# Top Hero Banner
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-wrap">
        <div>
            <div class="hero-h1">RAINFALLSCOPE INDIA</div>
            <p class="hero-p">Regional Precipitation Trend Explorer • <b>Explore Rainfall. Detect Trends. Understand Change.</b></p>
        </div>
        <div class="mission-pill">🛰️ NASA GPM IMERG Final V07</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Global Compact Filter Bar
# ---------------------------------------------------------------------------
min_yr = int(df_raw["date"].dt.year.min())
max_yr = int(df_raw["date"].dt.year.max())

default_col = "mean_GPM_3IMERGM_07_precipitation" if "mean_GPM_3IMERGM_07_precipitation" in value_cols else value_cols[0]

with st.container(border=True):
    f1, f2, f3, f4 = st.columns([1.4, 1.2, 1.3, 0.7])
    with f1:
        yr_range = st.slider("Date Range (Years)", min_value=min_yr, max_value=max_yr, value=(min_yr, max_yr))
    with f2:
        season_choice = st.selectbox("Season", list(SEASON_MONTHS.keys()), index=0)
    with f3:
        selected_col = st.selectbox(
            "Region / Series",
            options=value_cols,
            index=value_cols.index(default_col),
            format_func=format_series_label,
        )
    with f4:
        st.markdown("<div style='height: 1.65rem;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.trend_analyzed = False
            st.rerun()

df_filtered = df_raw[
    (df_raw["date"].dt.year >= yr_range[0])
    & (df_raw["date"].dt.year <= yr_range[1])
    & (df_raw["date"].dt.month.isin(SEASON_MONTHS[season_choice]))
].copy()

if len(df_filtered) < 6:
    st.warning("Selected filter has fewer than 6 observations. Expand the year range or season.")
    st.stop()

region_label = format_series_label(selected_col)
filter_period_str = f"{df_filtered['date'].min().strftime('%b %Y')} – {df_filtered['date'].max().strftime('%b %Y')}"

# ---------------------------------------------------------------------------
# 4-Column KPI Row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f"""
        <div class="kpi-tile">
            <div class="kpi-icon">📅</div>
            <div>
                <div class="kpi-meta-label">Study Period</div>
                <div class="kpi-meta-val">{filter_period_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
        <div class="kpi-tile">
            <div class="kpi-icon">🗄️</div>
            <div>
                <div class="kpi-meta-label">Data Points</div>
                <div class="kpi-meta-val">{len(df_filtered)}</div>
                <div class="kpi-meta-sub">Monthly Observations</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""
        <div class="kpi-tile">
            <div class="kpi-icon">📍</div>
            <div>
                <div class="kpi-meta-label">Region</div>
                <div class="kpi-meta-val">{region_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f"""
        <div class="kpi-tile">
            <div class="kpi-icon">⏱️</div>
            <div>
                <div class="kpi-meta-label">Temporal Resolution</div>
                <div class="kpi-meta-val">Monthly</div>
                <div class="kpi-meta-sub">{season_choice}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 0.65rem;'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# PAGE 1: OVERVIEW (BENTO MISSION CONTROL)
# ---------------------------------------------------------------------------
if page == "🏠 Overview":
    row1_left, row1_right = st.columns([1.05, 1.45])
    with row1_left:
        with st.container(border=True):
            st.markdown('<div class="card-title-bar">India: Mean Monthly Precipitation</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_india_regional_map(df_filtered, unit=unit_short), use_container_width=True)

    with row1_right:
        with st.container(border=True):
            st.markdown(
                f'<div class="card-title-bar">{region_label} Mean Precipitation (Monthly): {filter_period_str}</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(plot_overview_series(df_filtered, selected_col, region_label, unit=unit_short), use_container_width=True)

    climatology_all, anomaly_all = compute_monthly_anomalies(
        df_raw[(df_raw["date"].dt.year >= yr_range[0]) & (df_raw["date"].dt.year <= yr_range[1])],
        [selected_col],
    )
    res_preview = analyze_series_trend(df_filtered, selected_col, region_label, alpha=0.05)

    # Row 2: 50-50 Seasonal Pattern & Anomaly Heatmap
    row2_left, row2_right = st.columns(2)
    with row2_left:
        with st.container(border=True):
            st.markdown('<div class="card-title-bar">Seasonal Pattern: Climatological Monthly Profile</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_seasonal_profile_bars(climatology_all, selected_col, unit=unit_short), use_container_width=True)

    with row2_right:
        with st.container(border=True):
            st.markdown(f'<div class="card-title-bar">Precipitation Anomaly ({unit_short})</div>', unsafe_allow_html=True)
            st.plotly_chart(plot_anomaly_heatmap(anomaly_all, selected_col, region_label, unit=unit_short, compact=True), use_container_width=True)

    # Row 3: Full-width Trend Detective Card
    with st.container(border=True):
        st.markdown('<div class="card-title-bar">🔍 Trend Detective</div>', unsafe_allow_html=True)

        cb1, cb2, cb3, cb4 = st.columns(4)
        with cb1:
            chk_rate = st.checkbox("Compute long-term trend rate", value=False, key="chk_rate")
        with cb2:
            chk_sig = st.checkbox("Test statistical significance", value=False, key="chk_sig")
        with cb3:
            chk_var = st.checkbox("Analyze monthly & annual variability", value=False, key="chk_var")
        with cb4:
            chk_sum = st.checkbox("Summarize key findings", value=False, key="chk_sum")

        btn_col, status_col = st.columns([1.1, 2.9])
        with btn_col:
            run_clicked = st.button("▶ Run Trend Analysis", type="primary", use_container_width=True)
            if run_clicked:
                if not any([chk_rate, chk_sig, chk_var, chk_sum]):
                    st.session_state.trend_analyzed = False
                    st.warning("Please tick at least one analysis option above.")
                else:
                    st.session_state.trend_analyzed = True

        with status_col:
            if not st.session_state.trend_analyzed:
                st.markdown(
                    '<div class="status-badge status-pending" style="margin:0;">❓ Status: Analysis Pending — Tick options and click Run Trend Analysis</div>',
                    unsafe_allow_html=True,
                )
            elif chk_sig:
                if res_preview.is_significant:
                    st.markdown(
                        f'<div class="status-badge status-sig" style="margin:0;">✅ Statistically Significant ({res_preview.smk_direction})</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="status-badge status-nonsig" style="margin:0;">⚖️ {res_preview.smk_direction} (Not Significant at α=0.05)</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="status-badge status-sig" style="margin:0;">✅ Selected Analysis Complete</div>',
                    unsafe_allow_html=True,
                )

        if st.session_state.trend_analyzed:
            lines = []
            if chk_rate:
                lines.append(
                    f"- **Theil-Sen Rate:** `{res_preview.theil_slope_per_year:+.6f}` {unit_short}/yr (`{res_preview.theil_slope_per_decade:+.5f}` /dec) • **OLS Slope:** `{res_preview.ols_slope_per_year:+.6f}` {unit_short}/yr"
                )
            if chk_sig:
                lines.append(
                    f"- **Seasonal MK p-value:** `{res_preview.smk_p_value:.4f}` (Z = `{res_preview.smk_z:+.2f}`) • **OLS t-test p-value:** `{res_preview.ols_p_value:.4f}`"
                )
            if chk_var:
                lines.append(
                    f"- **Mean ± Std:** `{res_preview.mean_val:.4f}` ± `{res_preview.std_val:.4f}` {unit_short} • **Range:** `{res_preview.min_val:.4f}` – `{res_preview.max_val:.4f}` {unit_short}"
                )
            if chk_sum:
                sig_word = "statistically significant" if res_preview.is_significant else "not statistically significant"
                lines.append(
                    f"- **Summary:** **{region_label}** shows an **{res_preview.smk_direction.lower()}** tendency that is **{sig_word}** at α = 0.05."
                )

            if lines:
                st.markdown("\n".join(lines))


# ---------------------------------------------------------------------------
# PAGE 2: PRECIPITATION TRENDS
# ---------------------------------------------------------------------------
elif page == "📈 Precipitation Trends":
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.2, 1.2, 1.4])
        with c1:
            ma_window = st.select_slider("Moving Average (months)", options=[3, 6, 12, 24, 36], value=12)
        with c2:
            alpha = st.selectbox("Significance Level (α)", options=[0.01, 0.05, 0.10], index=1)
        with c3:
            trend_mode = st.selectbox("Trend Estimator", options=["Both (Theil-Sen & OLS)", "Theil-Sen Robust", "OLS Linear"])

    res = analyze_series_trend(df_filtered, selected_col, region_label, alpha=alpha)
    verdict_cls = "verdict-box sig" if res.is_significant else "verdict-box"
    sig_phrase = "statistically significant" if res.is_significant else "not statistically significant"
    st.markdown(
        f"""
        <div class="{verdict_cls}">
            <b>{region_label}</b> shows an <b>{res.smk_direction.lower()}</b> tendency over
            <b>{filter_period_str}</b>, and the monotonic trend is <b>{sig_phrase}</b> at α = {alpha:.2f}.<br>
            <b>Theil-Sen Rate:</b> {res.theil_slope_per_year:+.6f} {unit_short}/yr ({res.theil_slope_per_decade:+.5f} {unit_short}/decade) •
            <b>Seasonal MK p:</b> {res.smk_p_value:.4f} • <b>OLS p:</b> {res.ols_p_value:.4f}
        </div>
        """,
        unsafe_allow_html=True,
    )

    png_bytes = export_highres_timeseries_png(df_filtered, selected_col, res, ma_window=ma_window, unit=unit_short)
    st.download_button(
        label="⬇️ Download 300 DPI High-Res PNG",
        data=png_bytes,
        file_name=f"{selected_col}_trend_300dpi.png",
        mime="image/png",
    )
    st.plotly_chart(
        plot_time_series(df_filtered, selected_col, res, ma_window=ma_window, unit=unit_short, trend_mode=trend_mode),
        use_container_width=True,
    )


# ---------------------------------------------------------------------------
# PAGE 3: SEASONAL PATTERNS
# ---------------------------------------------------------------------------
elif page == "📅 Seasonal Patterns":
    climatology, _ = compute_monthly_anomalies(
        df_raw[(df_raw["date"].dt.year >= yr_range[0]) & (df_raw["date"].dt.year <= yr_range[1])],
        value_cols,
    )
    with st.container(border=True):
        st.markdown('<div class="card-title-bar">Multi-Region 12-Month Seasonal Climatology</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_seasonal_climatology(climatology, value_cols, format_series_label, unit=unit_short), use_container_width=True)

    with st.container(border=True):
        st.markdown(f'<div class="card-title-bar">{region_label} — Monthly Climatological Profile</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_seasonal_profile_bars(climatology, selected_col, unit=unit_short), use_container_width=True)


# ---------------------------------------------------------------------------
# PAGE 4: ANOMALIES
# ---------------------------------------------------------------------------
elif page == "⚠️ Anomalies":
    df_yr = df_raw[(df_raw["date"].dt.year >= yr_range[0]) & (df_raw["date"].dt.year <= yr_range[1])].copy()
    _, anomaly_df = compute_monthly_anomalies(df_yr, value_cols)
    _, annual_anom = compute_annual_summary(df_yr, value_cols)

    with st.container(border=True):
        st.plotly_chart(plot_monthly_anomalies(anomaly_df, selected_col, region_label, unit=unit_short), use_container_width=True)

    c_left, c_right = st.columns(2)
    with c_left:
        with st.container(border=True):
            st.plotly_chart(plot_anomaly_heatmap(anomaly_df, selected_col, region_label, unit=unit_short), use_container_width=True)
    with c_right:
        with st.container(border=True):
            st.plotly_chart(plot_annual_anomalies(annual_anom, selected_col, region_label, unit=unit_short), use_container_width=True)


# ---------------------------------------------------------------------------
# PAGE 5: TREND DETECTION
# ---------------------------------------------------------------------------
elif page == "📊 Trend Detection":
    alpha_comp = st.selectbox("Significance Threshold (α)", [0.01, 0.05, 0.10], index=1)
    comp_df = build_regional_comparison_table(df_filtered, value_cols, format_series_label, alpha=alpha_comp)

    with st.container(border=True):
        st.markdown('<div class="card-title-bar">Cross-Region Statistical Trend & Significance Summary</div>', unsafe_allow_html=True)
        st.dataframe(
            comp_df.style.format(
                {
                    "Theil-Sen (/yr)": "{:+.6f}",
                    "Theil-Sen (/decade)": "{:+.5f}",
                    "OLS Slope (/decade)": "{:+.5f}",
                    "OLS p-value": "{:.4f}",
                    "Seasonal MK Z": "{:+.2f}",
                    "Seasonal MK p-value": "{:.4f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with st.container(border=True):
        st.plotly_chart(plot_regional_slope_comparison(comp_df), use_container_width=True)

    res = analyze_series_trend(df_filtered, selected_col, region_label, alpha=alpha_comp)
    with st.container(border=True):
        st.markdown('<div class="card-title-bar">What Could We Investigate Next?</div>', unsafe_allow_html=True)
        for item in get_next_investigation_prompts(region_label, res.smk_direction, res.is_significant):
            st.markdown(f"- {item}")


# ---------------------------------------------------------------------------
# PAGE 6: DATA & METHODOLOGY
# ---------------------------------------------------------------------------
elif page == "🗂️ Data & Methodology":
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Total Observations", audit["row_count"])
    q2.metric("Missing Values", audit["total_missing"])
    q3.metric("Duplicate Dates", audit["duplicate_rows"])
    q4.metric("Missing Months", audit["missing_month_count"])

    with st.container(border=True):
        st.markdown('<div class="card-title-bar">Regional Descriptive Statistics</div>', unsafe_allow_html=True)
        desc_df = compute_descriptive_stats(df_raw, value_cols, format_series_label)
        st.dataframe(
            desc_df.style.format({"Mean": "{:.4f}", "Median": "{:.4f}", "Min": "{:.4f}", "Max": "{:.4f}", "Std Dev": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with st.container(border=True):
        st.markdown('<div class="card-title-bar">Plain-Language Variable Glossary</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(VARIABLE_GLOSSARY), use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.markdown('<div class="card-title-bar">NASA & Space Agency Partner Data Resources</div>', unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame(NASA_PARTNER_RESOURCES),
            use_container_width=True,
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("Portal Link")},
        )
        st.dataframe(pd.DataFrame(DEMO_INVESTIGATIONS), use_container_width=True, hide_index=True)