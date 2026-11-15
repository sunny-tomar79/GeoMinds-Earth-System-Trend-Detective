from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REGION_LABELS: dict[str, str] = {
    "mean_east_india": "East India",
    "mean_south_india": "South India",
    "mean_central_india": "Central India",
    "mean_west_india": "West India",
    "mean_north_india": "North India",
    "mean_GPM_3IMERGM_07_precipitation": "All India (GPM IMERG)",
}


def format_series_label(col_name: str) -> str:
    """Return a human-friendly label for a dataset column."""
    if col_name in REGION_LABELS:
        return REGION_LABELS[col_name]
    cleaned = col_name.strip().replace("mean_", "").replace("_", " ").title()
    return cleaned


def _detect_giovanni_header(lines: list[str]) -> tuple[int | None, dict[str, str]]:
    """Detect NASA Giovanni CSV metadata rows and locate the tabular header row."""
    meta: dict[str, str] = {}
    header_idx: int | None = None
    for idx, raw_line in enumerate(lines[:35]):
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("time,") or lower.startswith("date,"):
            header_idx = idx
            break
        if ":" in line and "," in line:
            key, val = line.split(",", 1)
            meta[key.strip().rstrip(":")] = val.strip().strip('"')
    return header_idx, meta


def load_csv_bytes(raw_bytes: bytes, filename: str = "uploaded.csv") -> tuple[pd.DataFrame, dict[str, Any]]:
    """Parse either a standard time-series CSV or a NASA Giovanni CSV export."""
    text = raw_bytes.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    header_idx, giovanni_meta = _detect_giovanni_header(lines)

    if header_idx is not None and header_idx > 0:
        csv_body = "\n".join(lines[header_idx:])
        df = pd.read_csv(io.StringIO(csv_body))
    else:
        df = pd.read_csv(io.StringIO(text))

    df.columns = [c.strip() for c in df.columns]

    date_col = None
    for candidate in df.columns:
        if candidate.lower() in {"date", "time", "timestamp", "datetime", "month"}:
            date_col = candidate
            break
    if date_col is None:
        date_col = df.columns[0]

    if date_col != "date":
        df = df.rename(columns={date_col: "date"})

    # Parse dates cleanly (supports DD/MM/YYYY from All_region_India.csv and ISO from Giovanni)
    sample_str = str(df["date"].dropna().iloc[0]) if not df["date"].dropna().empty else ""
    dayfirst = "/" in sample_str and not sample_str.startswith(("19", "20"))
    df["date"] = pd.to_datetime(df["date"], dayfirst=dayfirst, errors="coerce")

    raw_row_count = len(df)
    invalid_dates = int(df["date"].isna().sum())
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    value_cols = [c for c in df.columns if c != "date"]
    fill_values = [-9999.9, -9999, -999.9, 9999.9]
    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].replace(fill_values, np.nan)

    metadata: dict[str, Any] = {
        "filename": filename,
        "source_type": "NASA Giovanni Export" if giovanni_meta else "Standard CSV",
        "giovanni_meta": giovanni_meta,
        "raw_rows": raw_row_count,
        "invalid_dates": invalid_dates,
        "value_columns": value_cols,
        "variable_name": "Precipitation (GPM IMERG)" if "precipitation" in filename.lower() or "india" in filename.lower() else "Earth System Variable",
        "unit": "mm/hr",
    }
    return df, metadata


def load_builtin_dataset(choice: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load one of the pre-bundled NASA Space Apps datasets."""
    if choice == "All India (NASA Giovanni GPM IMERG)":
        path = DATA_DIR / "india_monthly_precipitation.csv"
    elif choice == "Combined (5 Indian Regions + All India)":
        df_reg, meta_reg = load_csv_bytes((DATA_DIR / "All_region_India.csv").read_bytes(), "All_region_India.csv")
        df_all, meta_all = load_csv_bytes((DATA_DIR / "india_monthly_precipitation.csv").read_bytes(), "india_monthly_precipitation.csv")
        merged = pd.merge(df_reg, df_all, on="date", how="inner").sort_values("date").reset_index(drop=True)
        meta_reg["filename"] = "All_region_India.csv + india_monthly_precipitation.csv"
        meta_reg["source_type"] = "Regional + NASA Giovanni Combined"
        meta_reg["giovanni_meta"] = meta_all.get("giovanni_meta", {})
        meta_reg["value_columns"] = [c for c in merged.columns if c != "date"]
        return merged, meta_reg
    else:
        path = DATA_DIR / "All_region_India.csv"

    return load_csv_bytes(path.read_bytes(), path.name)


def run_data_quality_audit(df: pd.DataFrame, value_cols: list[str], invalid_dates: int = 0) -> dict[str, Any]:
    """Perform comprehensive data quality checks matching the regional analysis notebook."""
    missing_by_col = {col: int(df[col].isna().sum()) for col in value_cols}
    total_missing = sum(missing_by_col.values())
    duplicate_rows = int(df.duplicated(subset=["date"]).sum())
    negative_by_col = {col: int((df[col] < 0).sum()) for col in value_cols}
    total_negatives = sum(negative_by_col.values())

    start_date = df["date"].min()
    end_date = df["date"].max()
    expected_months = pd.date_range(start=start_date, end=end_date, freq="MS")
    actual_months = pd.to_datetime(df["date"].dt.to_period("M").dt.to_timestamp().unique())
    missing_months = sorted(set(expected_months) - set(actual_months))

    return {
        "row_count": len(df),
        "start_date": start_date,
        "end_date": end_date,
        "invalid_dates": invalid_dates,
        "duplicate_rows": duplicate_rows,
        "missing_by_col": missing_by_col,
        "total_missing": total_missing,
        "negative_by_col": negative_by_col,
        "total_negatives": total_negatives,
        "expected_month_count": len(expected_months),
        "missing_month_count": len(missing_months),
        "is_clean": (invalid_dates == 0 and duplicate_rows == 0 and total_missing == 0 and total_negatives == 0 and len(missing_months) == 0),
    }
