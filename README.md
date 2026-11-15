# 🌍 RainfallScope India
### NASA Space Apps Challenge 2026 — Earth System Trend Detective

**Team GeoMinds**

## 🚀 Live Demo

<https://geominds-earth-system-trend-detective-l28lrkyrwseju3dz9uhh.streamlit.app/>

**[Launch RainfallScope India Dashboard](https://geominds-earth-system-trend-detective-l28lrkyrwseju3dz9uhh.streamlit.app/)**

Explore the interactive dashboard to investigate precipitation patterns, detect long-term trends and understand changes across India.

---

RainfallScope India is an interactive data exploration and statistical analysis dashboard developed for the NASA Space Apps Challenge 2026. It helps users investigate long-term precipitation patterns across India and understand **what is changing, where it is changing, how much it is changing, and whether the observed trends are statistically significant.**

## ✨ Key Features

- **Interactive Investigation Dashboard:** Explore precipitation data by region, variable, time period, moving-average window and significance level.
- **Statistical Trend Analysis:**
  - Ordinary Least Squares (OLS) Linear Regression
  - Student's t-test, p-value, R² and 95% confidence interval
  - Theil–Sen robust slope estimation
  - Seasonal Mann–Kendall trend test
- **Seasonality and Anomaly Analysis:** Monthly climatology, precipitation anomalies, Year × Month heatmaps and annual aggregations.
- **Regional Analysis:** Explore and compare precipitation patterns across different Indian regions.
- **NASA Giovanni Data Support:** Includes NASA Giovanni GPM IMERG precipitation data and regional India datasets.
- **Custom CSV Upload:** Upload compatible CSV datasets for further exploration.
- **High-Resolution Chart Export:** Export publication-quality visualizations at 300 DPI.

## 📊 Datasets

The project includes the following datasets:

| Dataset | Description |
|---|---|
| `india_monthly_precipitation.csv` | All-India monthly precipitation dataset from NASA Giovanni |
| `All_region_India.csv` | Regional precipitation dataset for India |

The analysis covers October 2005 to September 2025, as defined by the project datasets.

## 🛠️ Technology Stack

- Python
- Streamlit
- Pandas and NumPy
- SciPy
- Plotly
- Matplotlib
- Seaborn
- Statistical Trend Analysis

## 🚀 Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/sunny-tomar79/GeoMinds-Earth-System-Trend-Detective.git
   ```

2. Open the project folder:

   ```bash
   cd GeoMinds-Earth-System-Trend-Detective
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the Streamlit application:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL displayed in your terminal.

## ☁️ Deploy on Streamlit Community Cloud

1. Open [Streamlit Community Cloud](https://share.streamlit.io/).
2. Sign in using your GitHub account.
3. Select **Create app**.
4. Choose the repository: `sunny-tomar79/GeoMinds-Earth-System-Trend-Detective`.
5. Select the deployment branch (usually `main`).
6. Set the main file path to `app.py`.
7. Click **Deploy**.

Make sure the repository contains `requirements.txt`, `app.py`, the `src/` package and the required datasets before deployment.

## 📁 Project Structure

```text
GeoMinds-Earth-System-Trend-Detective/
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── All_region_India.csv
│   └── india_monthly_precipitation.csv
│
├── src/
│   ├── __init__.py
│   ├── charts.py
│   ├── content.py
│   ├── data_loader.py
│   └── stats_engine.py
│
├── notebooks/
│   ├── Earth_System_Trend_Detective_Final.ipynb
│   └── Region_Wise_Professional_Reviewed.ipynb
│
├── presentation/
│   └── Earth_System_Trend_Detective_Presentation.pptx
│
├── app.py
├── requirements.txt
└── README.md
```

## 🎯 Project Objective

The primary objective is to investigate long-term precipitation trends across India using Earth observation data and statistical methods. The dashboard aims to make climate data exploration more accessible, transparent and interactive.

## 👥 Team

**Team GeoMinds**  
NASA Space Apps Challenge 2026

---

*Turning Earth observation data into meaningful insights through data science and statistical analysis.*
