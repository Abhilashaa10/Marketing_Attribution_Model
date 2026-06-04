"""
src/attribution_models.py
--------------------------
Implements all 5 marketing attribution models:
  1. First Touch
  2. Last Touch
  3. Linear
  4. Time Decay
  5. Position-Based (U-Shaped)

Each model works on the cleaned dataset and returns a DataFrame showing
how much Revenue and how many Conversions each channel is credited with.

Run standalone:  python src/attribution_models.py
Import in other files:
    from src.attribution_models import run_all_models
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
# HELPER — build "journeys" from the flat campaign-level data
# ─────────────────────────────────────────────────────────────────────────────

def build_journeys(df: pd.DataFrame) -> pd.DataFrame:
    """
    The dataset has one row per campaign (channel + date).
    We treat each Customer_Segment × Month combination as a unique "journey"
    and sort touchpoints by Date within that journey.

    Returns a DataFrame with columns:
        journey_id, Channel_Used, Date, Revenue_Estimate, Conversions, touchpoint_order
    """
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    # Create a journey_id: Customer_Segment + Month
    df["journey_id"] = df["Customer_Segment"] + "_" + df["Month"].astype(str)

    # Sort by journey, then by date (chronological touchpoint order)
    df = df.sort_values(["journey_id", "Date"]).reset_index(drop=True)

    # Touchpoint position within each journey
    df["touchpoint_order"] = df.groupby("journey_id").cumcount() + 1
    df["journey_length"]   = df.groupby("journey_id")["journey_id"].transform("count")

    return df[["journey_id", "Channel_Used", "Date",
               "Revenue_Estimate", "Conversions",
               "touchpoint_order", "journey_length"]]


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 1 — FIRST TOUCH
# ─────────────────────────────────────────────────────────────────────────────

def first_touch_attribution(journeys: pd.DataFrame) -> pd.DataFrame:
    """
    100% of credit goes to the FIRST touchpoint in each journey.
    """
    first = journeys[journeys["touchpoint_order"] == 1].copy()
    result = (
        first.groupby("Channel_Used")[["Revenue_Estimate", "Conversions"]]
        .sum()
        .reset_index()
        .rename(columns={"Revenue_Estimate": "Revenue", "Conversions": "Conversions"})
    )
    result["Model"] = "First Touch"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 2 — LAST TOUCH
# ─────────────────────────────────────────────────────────────────────────────

def last_touch_attribution(journeys: pd.DataFrame) -> pd.DataFrame:
    """
    100% of credit goes to the LAST touchpoint in each journey.
    """
    last = journeys[journeys["touchpoint_order"] == journeys["journey_length"]].copy()
    result = (
        last.groupby("Channel_Used")[["Revenue_Estimate", "Conversions"]]
        .sum()
        .reset_index()
        .rename(columns={"Revenue_Estimate": "Revenue", "Conversions": "Conversions"})
    )
    result["Model"] = "Last Touch"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 3 — LINEAR
# ─────────────────────────────────────────────────────────────────────────────

def linear_attribution(journeys: pd.DataFrame) -> pd.DataFrame:
    """
    Credit is split EQUALLY across all touchpoints in a journey.
    Each touchpoint gets:  revenue / journey_length
    """
    j = journeys.copy()
    j["Credit_Revenue"]     = j["Revenue_Estimate"] / j["journey_length"]
    j["Credit_Conversions"] = j["Conversions"]      / j["journey_length"]

    result = (
        j.groupby("Channel_Used")[["Credit_Revenue", "Credit_Conversions"]]
        .sum()
        .reset_index()
        .rename(columns={"Credit_Revenue": "Revenue", "Credit_Conversions": "Conversions"})
    )
    result["Model"] = "Linear"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 4 — TIME DECAY
# ─────────────────────────────────────────────────────────────────────────────

def time_decay_attribution(journeys: pd.DataFrame, decay_rate: float = 0.5) -> pd.DataFrame:
    """
    Touchpoints closer to conversion get MORE credit.
    Weight for touchpoint at position i (from end):
        weight = decay_rate ^ (journey_length - touchpoint_order)
    Weights are normalised to sum to 1 within each journey.

    decay_rate: 0.5 means each earlier step gets half the credit of the next.
    """
    j = journeys.copy()

    # Distance from the end (last touchpoint = 0, second-to-last = 1, …)
    j["dist_from_end"] = j["journey_length"] - j["touchpoint_order"]
    j["raw_weight"]    = decay_rate ** j["dist_from_end"]

    # Normalise weights within each journey so they sum to 1
    journey_weight_sum  = j.groupby("journey_id")["raw_weight"].transform("sum")
    j["norm_weight"]    = j["raw_weight"] / journey_weight_sum

    j["Credit_Revenue"]     = j["Revenue_Estimate"] * j["norm_weight"]
    j["Credit_Conversions"] = j["Conversions"]      * j["norm_weight"]

    result = (
        j.groupby("Channel_Used")[["Credit_Revenue", "Credit_Conversions"]]
        .sum()
        .reset_index()
        .rename(columns={"Credit_Revenue": "Revenue", "Credit_Conversions": "Conversions"})
    )
    result["Model"] = "Time Decay"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 5 — POSITION-BASED (U-SHAPED)
# ─────────────────────────────────────────────────────────────────────────────

def position_based_attribution(journeys: pd.DataFrame,
                                first_weight: float = 0.40,
                                last_weight:  float = 0.40) -> pd.DataFrame:
    """
    U-Shaped model:
        First touchpoint  → first_weight  (default 40%)
        Last  touchpoint  → last_weight   (default 40%)
        Middle touchpoints → remaining 20% split equally

    For single-touchpoint journeys: 100% to that touchpoint.
    For two-touchpoint journeys:    50% each (first + last only).
    """
    middle_weight = 1.0 - first_weight - last_weight
    j = journeys.copy()

    def assign_weight(row):
        L = row["journey_length"]
        pos = row["touchpoint_order"]
        if L == 1:
            return 1.0
        if L == 2:
            return 0.5
        if pos == 1:
            return first_weight
        if pos == L:
            return last_weight
        # middle positions share the remaining weight equally
        n_middle = L - 2
        return middle_weight / n_middle

    j["weight"] = j.apply(assign_weight, axis=1)

    j["Credit_Revenue"]     = j["Revenue_Estimate"] * j["weight"]
    j["Credit_Conversions"] = j["Conversions"]      * j["weight"]

    result = (
        j.groupby("Channel_Used")[["Credit_Revenue", "Credit_Conversions"]]
        .sum()
        .reset_index()
        .rename(columns={"Credit_Revenue": "Revenue", "Credit_Conversions": "Conversions"})
    )
    result["Model"] = "Position-Based"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MASTER FUNCTION — run all 5 models and combine
# ─────────────────────────────────────────────────────────────────────────────

def run_all_models(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds journeys then runs all 5 attribution models.
    Returns a single combined DataFrame with columns:
        Channel_Used | Revenue | Conversions | Model
    """
    print("[ATTRIBUTION] Building customer journeys...")
    journeys = build_journeys(df)
    print(f"[ATTRIBUTION] {journeys['journey_id'].nunique():,} unique journeys built.")

    print("[ATTRIBUTION] Running models...")
    results = pd.concat([
        first_touch_attribution(journeys),
        last_touch_attribution(journeys),
        linear_attribution(journeys),
        time_decay_attribution(journeys),
        position_based_attribution(journeys),
    ], ignore_index=True)

    # Add contribution % within each model
    results["Revenue_Pct"] = (
        results.groupby("Model")["Revenue"]
        .transform(lambda x: (x / x.sum() * 100).round(2))
    )

    results["Revenue"]     = results["Revenue"].round(2)
    results["Conversions"] = results["Conversions"].round(0).astype(int)

    print("[ATTRIBUTION] All 5 models complete.")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# SAVE RESULTS
# ─────────────────────────────────────────────────────────────────────────────

def save_attribution_results(results: pd.DataFrame, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    results.to_csv(filepath, index=False)
    print(f"[SAVE] Attribution results saved → {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE RUN — python src/attribution_models.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    CLEAN_PATH  = "data/processed/cleaned_data.csv"
    OUTPUT_PATH = "data/outputs/attribution_results.csv"

    df = load_cleaned_data(CLEAN_PATH)
    results = run_all_models(df)

    # Print comparison table per model
    print("\n" + "=" * 65)
    print("  ATTRIBUTION RESULTS — REVENUE BY CHANNEL PER MODEL")
    print("=" * 65)
    for model in results["Model"].unique():
        subset = results[results["Model"] == model].sort_values("Revenue", ascending=False)
        print(f"\n── {model} ──")
        print(subset[["Channel_Used", "Revenue", "Revenue_Pct", "Conversions"]]
              .to_string(index=False))

    # Pivot table: channels as rows, models as columns
    print("\n" + "=" * 65)
    print("  PIVOT — REVENUE CONTRIBUTION % BY MODEL")
    print("=" * 65)
    pivot = results.pivot_table(
        index="Channel_Used",
        columns="Model",
        values="Revenue_Pct"
    ).round(2)
    print(pivot.to_string())

    save_attribution_results(results, OUTPUT_PATH)
    print("\n[DONE] Attribution complete.")
    print("       Next step → run: python src/metrics.py")