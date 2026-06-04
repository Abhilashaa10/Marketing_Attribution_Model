"""
src/data_loader.py
------------------
Loads and cleans the raw marketing campaign dataset.
Run this file directly to test: python src/data_loader.py
"""

import pandas as pd
import numpy as np
import os


# ─────────────────────────────────────────────
# 1. LOAD
# ─────────────────────────────────────────────

def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load raw CSV from disk."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[LOAD] {df.shape[0]:,} rows x {df.shape[1]} columns loaded.")
    return df


# ─────────────────────────────────────────────
# 2. CLEAN — individual steps
# ─────────────────────────────────────────────

def clean_acquisition_cost(df: pd.DataFrame) -> pd.DataFrame:
    """'$16,174.00'  →  16174.0  (float)"""
    df["Acquisition_Cost"] = (
        df["Acquisition_Cost"]
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )
    return df


def clean_duration(df: pd.DataFrame) -> pd.DataFrame:
    """'30 days'  →  30  (int)  stored in Duration_Days"""
    df["Duration_Days"] = (
        df["Duration"].str.extract(r"(\d+)").astype(int)
    )
    df.drop(columns=["Duration"], inplace=True)
    return df


def clean_date(df: pd.DataFrame) -> pd.DataFrame:
    """Parse Date string, add Month / Quarter / Month_Name columns."""
    df["Date"]       = pd.to_datetime(df["Date"])
    df["Month"]      = df["Date"].dt.month
    df["Quarter"]    = df["Date"].dt.quarter
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    New columns derived from existing ones:
      Conversions      = Conversion_Rate * Clicks
      CTR              = Clicks / Impressions
      Cost_Per_Click   = Acquisition_Cost / Clicks
      Revenue_Estimate = ROI * Acquisition_Cost  (proxy)
    """
    df["Conversions"]      = (df["Conversion_Rate"] * df["Clicks"]).round().astype(int)
    df["CTR"]              = (df["Clicks"] / df["Impressions"]).round(4)
    df["Cost_Per_Click"]   = (df["Acquisition_Cost"] / df["Clicks"]).round(2)
    df["Revenue_Estimate"] = (df["ROI"] * df["Acquisition_Cost"]).round(2)
    return df


# ─────────────────────────────────────────────
# 3. MASTER PIPELINE
# ─────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Run all cleaning steps and return a clean DataFrame."""
    print("[CLEAN] Starting cleaning pipeline...")
    df = df.copy()

    df = clean_acquisition_cost(df)
    df = clean_duration(df)
    df = clean_date(df)

    # Standardise text columns
    text_cols = ["Company", "Campaign_Type", "Target_Audience",
                "Channel_Used", "Location", "Language", "Customer_Segment"]
    for col in text_cols:
        df[col] = df[col].str.strip()

    df = add_derived_columns(df)

    # Report nulls
    nulls = df.isnull().sum()
    if nulls.any():
        print("[WARN] Nulls found:\n", nulls[nulls > 0])
    else:
        print("[OK]   No null values.")

    # Report duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        df.drop_duplicates(inplace=True)
        print(f"[WARN] Dropped {dupes} duplicate rows.")
    else:
        print("[OK]   No duplicate rows.")

    print(f"[CLEAN] Done. Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


# ─────────────────────────────────────────────
# 4. SAVE / LOAD
# ─────────────────────────────────────────────

def save_cleaned_data(df: pd.DataFrame, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"[SAVE] Cleaned data saved → {filepath}")


def load_cleaned_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["Date"])
    print(f"[LOAD] Cleaned data loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


# ─────────────────────────────────────────────
# QUICK TEST — run: python src/data_loader.py
# ─────────────────────────────────────────────

if __name__ == "__main__":
    RAW   = "data/raw/marketing_campaign_dataset.csv"
    CLEAN = "data/processed/cleaned_data.csv"

    df_raw   = load_raw_data(RAW)
    df_clean = clean_data(df_raw)
    save_cleaned_data(df_clean, CLEAN)

    print("\n--- Sample cleaned rows ---")
    print(df_clean[["Campaign_ID", "Channel_Used", "Acquisition_Cost",
                    "Duration_Days", "Conversions", "CTR",
                    "Revenue_Estimate"]].head(5).to_string(index=False))