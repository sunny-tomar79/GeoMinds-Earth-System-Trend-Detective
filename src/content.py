from __future__ import annotations

VARIABLE_GLOSSARY = [
    {
        "Variable": "Precipitation (GPM IMERG)",
        "Unit": "mm/hr or mm/day",
        "Plain-Language Meaning": "Rate at which rain or snow falls over a region, estimated by combining satellite microwave/infrared sensors with rain gauges.",
        "Why It Matters": "Reveals shifting monsoon patterns, drought risk, and extreme rainfall events.",
    },
    {
        "Variable": "Surface Air Temperature (MERRA-2 / AIRS)",
        "Unit": "°C or K",
        "Plain-Language Meaning": "Warmth of the air near Earth's surface or across atmospheric layers.",
        "Why It Matters": "Tracks regional warming, heatwave frequency, and urban heat islands.",
    },
    {
        "Variable": "Soil Moisture (GLDAS / SMAP)",
        "Unit": "m³/m³ or kg/m²",
        "Plain-Language Meaning": "Amount of water stored in the upper layers of soil.",
        "Why It Matters": "Connects rainfall changes to agricultural drought and flood runoff.",
    },
    {
        "Variable": "Vegetation Greenness / NDVI (MODIS)",
        "Unit": "Index (-1 to +1)",
        "Plain-Language Meaning": "Measures how dense and healthy green plants are from space.",
        "Why It Matters": "Shows deforestation, crop cycles, or greening in response to rainfall/warming.",
    },
    {
        "Variable": "Chlorophyll-a (SeaWiFS / MODIS)",
        "Unit": "mg/m³",
        "Plain-Language Meaning": "Concentration of microscopic marine algae (phytoplankton) in surface ocean or coastal waters.",
        "Why It Matters": "Indicates river nutrient runoff and ocean ecosystem productivity.",
    },
    {
        "Variable": "Surface Water Elevation (SWOT)",
        "Unit": "meters (m)",
        "Plain-Language Meaning": "Height of lakes, rivers, and reservoirs measured by wide-swath radar interferometry.",
        "Why It Matters": "Monitors freshwater storage changes and flood dynamics globally.",
    },
]

DEMO_INVESTIGATIONS = [
    {
        "name": "East India Monsoon Check",
        "dataset": "All Indian Regions (Regional CSV)",
        "region": "mean_east_india",
        "question": "Is East India's rainfall changing significantly over 2005–2025?",
    },
    {
        "name": "Central India Drying vs Wetting",
        "dataset": "All Indian Regions (Regional CSV)",
        "region": "mean_central_india",
        "question": "How strong is the long-term trend in Central India's heartland?",
    },
    {
        "name": "All-India GPM IMERG Baseline",
        "dataset": "All India (NASA Giovanni GPM IMERG)",
        "region": "mean_GPM_3IMERGM_07_precipitation",
        "question": "Does the national India average hide contrasting regional trends?",
    },
]

NASA_PARTNER_RESOURCES = [
    {
        "Agency": "NASA",
        "Resource": "Giovanni (GES DISC)",
        "What It Does": "Interactive web tool to explore, visualize, and download time-series CSVs for satellite variables like GPM IMERG, MODIS, OMI, AIRS, and MERRA-2.",
        "URL": "https://giovanni.gsfc.nasa.gov/giovanni/",
    },
    {
        "Agency": "NASA",
        "Resource": "AppEEARS",
        "What It Does": "Extracts and transforms geospatial subsets and time series from NASA Earthdata archives.",
        "URL": "https://appeears.earthdatacloud.nasa.gov/",
    },
    {
        "Agency": "NOAA",
        "Resource": "Climate Data Online (CDO)",
        "What It Does": "Free archive of global historical weather, climate observations, and station history with mapping tools.",
        "URL": "https://www.ncei.noaa.gov/cdo-web/",
    },
    {
        "Agency": "KNMI",
        "Resource": "KNMI Climate Explorer",
        "What It Does": "Web-based climate analysis platform for exploring, correlating, and testing statistical trends across climate datasets.",
        "URL": "https://climexp.knmi.nl/",
    },
    {
        "Agency": "NASA / CNES / CSA",
        "Resource": "SWOT Mission",
        "What It Does": "Surveys 90% of Earth's surface water to measure changing water elevation in lakes, rivers, reservoirs, and oceans.",
        "URL": "https://swot.jpl.nasa.gov/",
    },
    {
        "Agency": "CSA",
        "Resource": "RADARSAT Constellation Mission (RCM) & Geo.ca",
        "What It Does": "All-weather SAR Earth observation for maritime surveillance, disaster management, and ecosystem monitoring.",
        "URL": "https://www.asc-csa.gc.ca/eng/satellites/radarsat/",
    },
]


def get_next_investigation_prompts(region_label: str, direction: str, is_significant: bool) -> list[str]:
    """Generate science-grounded follow-up hypotheses without claiming causality."""
    prompts = [
        f"Compare **{region_label}** against neighboring regions in the **Regional Comparison** tab — a variable can trend one way in one region and the opposite way in another.",
        "Switch to **Monthly Anomalies** or **Year × Month Heatmap** to check whether changes are concentrated in monsoon months (June–September) or dry-season months.",
    ]
    if not is_significant:
        prompts.append(
            "A **non-significant** trend over 20 years does not mean nothing is happening: strong year-to-year monsoon variability (such as El Niño / La Niña) or extreme-rain events can mask slow shifts in monthly averages."
        )
    else:
        prompts.append(
            f"Because **{region_label}** shows a statistically significant **{direction.lower()}** trend, test whether a longer time window or nearby hydrological variables (soil moisture, streamflow) show a matching signal."
        )
    return prompts
