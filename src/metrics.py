"""
src/metrics.py
--------------
Calculates all key business KPIs per channel:
  - Total Revenue, Total Conversions
  - Conversion Rate
  - Cost Per Acquisition (CPA)
  - Return on Investment (ROI)
  - Click-Through Rate (CTR)
  - Assisted Conversions
  - Channel Contribution %

Also computes model-level comparison metrics using attribution_results.csv.

Run standalone:  python src/metrics.py
Import in other files:
    from src.metrics import compute_channel_metrics, compute_model_comparison
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.data_loader import load_cleaned_data


# ─────────────────────────────────────────────────────────────────────────────
# 1. CHANNEL-LEVEL KPIs  (from cleaned data)
# ─────────────────────────────────────────────────────────────────────────────

def compute_channel_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates cleaned data by Channel_Used and computes:
        Total_Revenue, Total_Conversions, Total_Clicks, Total_Impressions,
        Total_Cost, Avg_ROI, Avg_Conversion_Rate, Avg_CTR,
        CPA, CTR_Pct, Revenue_Contribution_Pct, Conversion_Contribution_Pct
    """
    grp = df.groupby("Channel_Used").agg(
        Total_Revenue      = ("Revenue_Estimate",  "sum"),
        Total_Conversions  = ("Conversions",        "sum"),
        Total_Clicks       = ("Clicks",             "sum"),
        Total_Impressions  = ("Impressions",        "sum"),
        Total_Cost         = ("Acquisition_Cost",   "sum"),
        Avg_ROI            = ("ROI",                "mean"),
        Avg_Conversion_Rate= ("Conversion_Rate",    "mean"),
        Avg_CTR            = ("CTR",                "mean"),
        Campaign_Count     = ("Campaign_ID",        "count"),
    ).reset_index()

    # CPA = Total Cost / Total Conversions
    grp["CPA"] = (grp["Total_Cost"] / grp["Total_Conversions"]).round(2)

    # Revenue and Conversion contribution %
    grp["Revenue_Contribution_Pct"]    = (grp["Total_Revenue"]     / grp["Total_Revenue"].sum()     * 100).round(2)
    grp["Conversion_Contribution_Pct"] = (grp["Total_Conversions"] / grp["Total_Conversions"].sum() * 100).round(2)

    # Round for readability
    grp["Total_Revenue"]       = grp["Total_Revenue"].round(2)
    grp["Avg_ROI"]             = grp["Avg_ROI"].round(3)
    grp["Avg_Conversion_Rate"] = grp["Avg_Conversion_Rate"].round(4)
    grp["Avg_CTR"]             = grp["Avg_CTR"].round(4)

    return grp.sort_values("Total_Revenue", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# 2. ASSISTED CONVERSIONS
# ─────────────────────────────────────────────────────────────────────────────

def compute_assisted_conversions(df: pd.DataFrame) -> pd.DataFrame:
    """
    A channel ASSISTS a conversion if it appears in a journey but is NOT
    the last touchpoint.  We proxy journeys the same way attribution_models.py
    does (Customer_Segment × Month).

    Returns a DataFrame: Channel_Used | Assisted_Conversions | Direct_Conversions
    """
    d = df.copy()
    d["Date"]       = pd.to_datetime(d["Date"])
    d["journey_id"] = d["Customer_Segment"] + "_" + d["Month"].astype(str)
    d = d.sort_values(["journey_id", "Date"]).reset_index(drop=True)
    d["touchpoint_order"] = d.groupby("journey_id").cumcount() + 1
    d["journey_length"]   = d.groupby("journey_id")["journey_id"].transform("count")

    assisted = (
        d[d["touchpoint_order"] < d["journey_length"]]
        .groupby("Channel_Used")["Conversions"].sum()
        .reset_index()
        .rename(columns={"Conversions": "Assisted_Conversions"})
    )
    direct = (
        d[d["touchpoint_order"] == d["journey_length"]]
        .groupby("Channel_Used")["Conversions"].sum()
        .reset_index()
        .rename(columns={"Conversions": "Direct_Conversions"})
    )
    result = assisted.merge(direct, on="Channel_Used", how="outer").fillna(0)
    result["Assisted_Conversions"] = result["Assisted_Conversions"].astype(int)
    result["Direct_Conversions"]   = result["Direct_Conversions"].astype(int)
    result["Total_Conversions"]    = result["Assisted_Conversions"] + result["Direct_Conversions"]
    return result.sort_values("Assisted_Conversions", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. MODEL COMPARISON — which channel ranks where across models
# ─────────────────────────────────────────────────────────────────────────────

def compute_model_comparison(attribution_results: pd.DataFrame) -> pd.DataFrame:
    """
    Pivots the attribution_results to show Revenue_Pct for each channel
    across all 5 models side by side.  Also adds Avg_Pct and Rank columns.
    """
    pivot = attribution_results.pivot_table(
        index   = "Channel_Used",
        columns = "Model",
        values  = "Revenue_Pct"
    ).round(2).reset_index()

    # Average contribution across all models
    model_cols = [c for c in pivot.columns if c != "Channel_Used"]
    pivot["Avg_Contribution_Pct"] = pivot[model_cols].mean(axis=1).round(2)
    pivot["Rank_By_Avg"]          = pivot["Avg_Contribution_Pct"].rank(ascending=False).astype(int)

    return pivot.sort_values("Rank_By_Avg")


# ─────────────────────────────────────────────────────────────────────────────
# 4. QUARTERLY PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────

def compute_quarterly_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and conversions broken down by Channel × Quarter."""
    grp = df.groupby(["Channel_Used", "Quarter"]).agg(
        Revenue     = ("Revenue_Estimate", "sum"),
        Conversions = ("Conversions",       "sum"),
        Avg_ROI     = ("ROI",               "mean"),
    ).reset_index()
    grp["Revenue"] = grp["Revenue"].round(2)
    grp["Avg_ROI"] = grp["Avg_ROI"].round(3)
    return grp


# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────

def save_metrics(df: pd.DataFrame, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"[SAVE] Metrics saved → {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE RUN — python src/metrics.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    CLEAN_PATH       = "data/processed/cleaned_data.csv"
    ATTR_PATH        = "data/outputs/attribution_results.csv"
    METRICS_PATH     = "data/outputs/channel_metrics.csv"
    ASSISTED_PATH    = "data/outputs/assisted_conversions.csv"
    COMPARISON_PATH  = "data/outputs/model_comparison.csv"
    QUARTERLY_PATH   = "data/outputs/quarterly_performance.csv"

    df = load_cleaned_data(CLEAN_PATH)

    # ── 1. Channel KPIs ──────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  CHANNEL-LEVEL KPIs")
    print("=" * 65)
    channel_metrics = compute_channel_metrics(df)
    print(channel_metrics[[
        "Channel_Used", "Total_Revenue", "Total_Conversions",
        "Total_Cost", "CPA", "Avg_ROI",
        "Revenue_Contribution_Pct", "Conversion_Contribution_Pct"
    ]].to_string(index=False))
    save_metrics(channel_metrics, METRICS_PATH)

    # ── 2. Assisted Conversions ───────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  ASSISTED vs DIRECT CONVERSIONS BY CHANNEL")
    print("=" * 65)
    assisted = compute_assisted_conversions(df)
    print(assisted.to_string(index=False))
    save_metrics(assisted, ASSISTED_PATH)

    # ── 3. Model Comparison ───────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  MODEL COMPARISON — REVENUE CONTRIBUTION % ACROSS MODELS")
    print("=" * 65)
    if os.path.exists(ATTR_PATH):
        attr = pd.read_csv(ATTR_PATH)
        comparison = compute_model_comparison(attr)
        print(comparison.to_string(index=False))
        save_metrics(comparison, COMPARISON_PATH)
    else:
        print("[WARN] attribution_results.csv not found. Run attribution_models.py first.")

    # ── 4. Quarterly Performance ──────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  QUARTERLY PERFORMANCE BY CHANNEL")
    print("=" * 65)
    quarterly = compute_quarterly_performance(df)
    print(quarterly.to_string(index=False))
    save_metrics(quarterly, QUARTERLY_PATH)

    # ── 5. Executive Summary ──────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  EXECUTIVE SUMMARY")
    print("=" * 65)
    print(f"  Total Revenue       : ${df['Revenue_Estimate'].sum():>18,.2f}")
    print(f"  Total Conversions   : {df['Conversions'].sum():>19,}")
    print(f"  Total Marketing Cost: ${df['Acquisition_Cost'].sum():>18,.2f}")
    print(f"  Overall Avg ROI     : {df['ROI'].mean():>19.3f}")
    print(f"  Overall Avg CPA     : ${df['Acquisition_Cost'].sum()/df['Conversions'].sum():>18.2f}")
    print(f"  Overall Avg CTR     : {df['CTR'].mean():>19.4f}")
    print(f"  Campaigns Analysed  : {len(df):>19,}")
    top_channel = channel_metrics.iloc[0]["Channel_Used"]
    top_revenue = channel_metrics.iloc[0]["Total_Revenue"]
    print(f"  Top Channel (Rev)   : {top_channel} (${top_revenue:,.2f})")

    print("\n[DONE] Metrics complete.")
    print("       Next step → run: python src/visualizations.py")