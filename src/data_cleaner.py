"""
src/data_cleaner.py
-------------------
Cleans the raw dataset and saves cleaned_data.csv to data/processed/.
Imports cleaning functions from src/data_loader.py.

Run: python src/data_cleaner.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import warnings
warnings.filterwarnings("ignore")

# Make sure src/ is on the path when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.data_loader import load_raw_data, clean_data, save_cleaned_data

# ── Config ────────────────────────────────────────────────────────────────────
RAW_PATH   = "data/raw/marketing_campaign_dataset.csv"
CLEAN_PATH = "data/processed/cleaned_data.csv"
CHARTS_DIR = "reports/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120})

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Load raw data
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 55)
print("         DATA CLEANING PIPELINE")
print("=" * 55)

df_raw = load_raw_data(RAW_PATH)
print("\nRaw columns  :", df_raw.columns.tolist())
print("Raw dtypes:\n", df_raw.dtypes.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Problems in raw data (print before/after examples)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[BEFORE CLEANING]")
print("  Acquisition_Cost sample :", df_raw["Acquisition_Cost"].head(3).tolist())
print("  Duration sample          :", df_raw["Duration"].head(3).tolist())
print("  Date sample              :", df_raw["Date"].head(3).tolist())

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Run the master cleaning pipeline
# ─────────────────────────────────────────────────────────────────────────────
df_clean = clean_data(df_raw)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Verify fixes
# ─────────────────────────────────────────────────────────────────────────────
print("\n[AFTER CLEANING]")
print("  Acquisition_Cost sample :", df_clean["Acquisition_Cost"].head(3).tolist())
print("  Duration_Days sample     :", df_clean["Duration_Days"].head(3).tolist())
print("  Date sample              :", df_clean["Date"].head(3).tolist())
print("  New derived columns      :", ["Conversions", "CTR", "Cost_Per_Click", "Revenue_Estimate"])

print("\n[COLUMN COMPARISON]")
raw_cols   = set(df_raw.columns)
clean_cols = set(df_clean.columns)
print("  Dropped  :", raw_cols - clean_cols)
print("  Added    :", clean_cols - raw_cols)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Summary stats on cleaned numeric columns
# ─────────────────────────────────────────────────────────────────────────────
print("\n[CLEANED DATA — SUMMARY STATS]")
stat_cols = ["Acquisition_Cost", "ROI", "Conversion_Rate",
             "Clicks", "Impressions", "Conversions",
             "CTR", "Cost_Per_Click", "Revenue_Estimate"]
print(df_clean[stat_cols].describe().round(3).to_string())

# ─────────────────────────────────────────────────────────────────────────────
# CHART 8 — Outlier boxplots on cleaned data
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, len(stat_cols), figsize=(26, 5))
for ax, col in zip(axes, stat_cols):
    sns.boxplot(y=df_clean[col], ax=ax, color="lightblue")
    ax.set_title(col, fontsize=9)
plt.suptitle("Outlier Check — Cleaned Data", fontsize=13, y=1.02)
plt.tight_layout()
path = f"{CHARTS_DIR}/08_outlier_boxplots_cleaned.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"\n[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 9 — Revenue Estimate by Channel (cleaned)
# ─────────────────────────────────────────────────────────────────────────────
rev_by_channel = df_clean.groupby("Channel_Used")["Revenue_Estimate"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(rev_by_channel.index, rev_by_channel.values,
              color=sns.color_palette("rocket", len(rev_by_channel)))
ax.set_title("Total Revenue Estimate by Channel", fontsize=13)
ax.set_ylabel("Revenue ($)")
ax.set_xlabel("Channel")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1e6,
            f"${bar.get_height()/1e6:.1f}M",
            ha="center", fontsize=9)
plt.tight_layout()
path = f"{CHARTS_DIR}/09_revenue_by_channel.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 10 — Conversions by Campaign Type
# ─────────────────────────────────────────────────────────────────────────────
conv_by_type = df_clean.groupby("Campaign_Type")["Conversions"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=conv_by_type.index, y=conv_by_type.values,
            palette="Blues_d", ax=ax)
ax.set_title("Total Conversions by Campaign Type", fontsize=13)
ax.set_xlabel("Campaign Type")
ax.set_ylabel("Total Conversions")
plt.tight_layout()
path = f"{CHARTS_DIR}/10_conversions_by_campaign_type.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — Save cleaned CSV
# ─────────────────────────────────────────────────────────────────────────────
save_cleaned_data(df_clean, CLEAN_PATH)

print("\n[DONE] Cleaning complete.")
print("       Next step → run: python src/attribution_models.py")