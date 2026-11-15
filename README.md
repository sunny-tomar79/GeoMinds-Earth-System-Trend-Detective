# 🌍 Earth System Trend Detective
**NASA Space Apps Challenge — Interactive Time-Series & Statistical Trend Analysis Dashboard**

An interactive Streamlit application designed to help students, researchers, and citizen scientists act as **Earth System Data Detectives** — exploring **what** is changing, **where** it is changing, **how much** it is changing, and **whether the trend is statistically significant**.

## ✨ Key Features
- **Guided Investigation Panel**: Select variable, region, time window, moving-average window, and significance level ($\alpha$).
- **Statistical Trend Engine**:
  - **OLS Linear Regression** with Student's *t*-test, $p$-value, $R^2$, and 95% confidence interval.
  - **Theil–Sen Robust Median Slope** with 95% confidence interval.
  - **Seasonal Mann–Kendall Test** (Hirsch, Slack & Smith 1982) for monotonic trends in seasonal monthly data.
- **Seasonality & Anomaly Analysis**: Calendar-month climatology, monthly anomaly bars, Year × Month diverging heatmaps, and complete-12-month annual aggregations.
- **Universal CSV & NASA Giovanni Support**: Pre-loaded with your **Regional India (`All_region_India.csv`)** and **All-India NASA Giovanni GPM IMERG (`india_monthly_precipitation.csv`)** datasets, plus sidebar upload for any custom or NASA Giovanni CSV export.
- **300 DPI High-Res Chart Export**: Download publication-ready Matplotlib/Seaborn PNG figures directly from the dashboard.

## 🚀 How to Run in Visual Studio Code

1. **Extract** this ZIP folder and open the `earth_system_trend_detective` folder in **VS Code** (`File -> Open Folder...`).
2. **Open the VS Code Terminal** (`Ctrl + ~` or `Terminal -> New Terminal`).
3. *(Recommended)* Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```
   *(Or press **F5** in VS Code using the included `.vscode/launch.json` configuration!)*

## 📁 Project Structure
```text
earth_system_trend_detective/
├── .streamlit/
│   └── config.toml          # NASA Mission-Control dark theme
├── .vscode/
│   ├── launch.json          # Press F5 to run/debug in VS Code
│   └── settings.json        # Workspace Python settings
├── data/
│   ├── All_region_India.csv
│   └── india_monthly_precipitation.csv
├── src/
│   ├── data_loader.py       # Standard & NASA Giovanni CSV parser + quality audit
│   ├── stats_engine.py      # OLS, Theil-Sen, Seasonal Mann-Kendall, anomalies
│   ├── charts.py            # Interactive Plotly + 300 DPI Matplotlib figures
│   └── content.py           # Variable glossary, methods guide, NASA/CSA resources
├── app.py                   # Main Streamlit application
├── requirements.txt
└── README.md
```
