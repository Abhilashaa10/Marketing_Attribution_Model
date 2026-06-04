"""
src/eda.py
----------
Exploratory Data Analysis on the RAW dataset.
Prints summaries and saves charts to reports/charts/

Run: python src/eda.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────────────────
RAW_PATH    = "data/raw/marketing_campaign_dataset.csv"
CHARTS_DIR  = "reports/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120, "figure.figsize": (12, 5)})

# ── Load ──────────────────────────────────────────────────────────────────────
print("=" * 55)
print("  MARKETING ATTRIBUTION — EXPLORATORY DATA ANALYSIS")
print("=" * 55)

df = pd.read_csv(RAW_PATH)
print(f"\n[1] Shape          : {df.shape[0]:,} rows  x  {df.shape[1]} columns")
print(f"[1] Duplicate rows : {df.duplicated().sum()}")
print(f"[1] Null values    : {df.isnull().sum().sum()}")

# ── Column types ──────────────────────────────────────────────────────────────
print("\n[2] COLUMN TYPES")
print("-" * 35)
print(df.dtypes.to_string())

# ── Unique values in categoricals ─────────────────────────────────────────────
cat_cols = ["Campaign_Type", "Channel_Used", "Target_Audience",
            "Location", "Language", "Customer_Segment", "Duration"]
print("\n[3] UNIQUE VALUES IN CATEGORICAL COLUMNS")
print("-" * 45)
for col in cat_cols:
    print(f"  {col:<20}: {df[col].unique().tolist()}")

# ── Numeric summary ───────────────────────────────────────────────────────────
print("\n[4] NUMERIC SUMMARY")
print("-" * 45)
num_cols = ["Conversion_Rate", "ROI", "Clicks", "Impressions", "Engagement_Score"]
print(df[num_cols].describe().round(3).to_string())

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Numeric Distributions
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 5, figsize=(22, 4))
for ax, col in zip(axes, num_cols):
    sns.histplot(df[col], ax=ax, kde=True, color="steelblue", bins=30)
    ax.set_title(col, fontsize=11)
    ax.set_xlabel("")
plt.suptitle("Numeric Column Distributions (Raw Data)", fontsize=13, y=1.02)
plt.tight_layout()
path = f"{CHARTS_DIR}/01_numeric_distributions.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"\n[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Campaign count per channel
# ─────────────────────────────────────────────────────────────────────────────
counts = df["Channel_Used"].value_counts()
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(counts.index, counts.values,
              color=sns.color_palette("viridis", len(counts)))
ax.set_title("Number of Campaigns per Channel", fontsize=13)
ax.set_xlabel("Channel")
ax.set_ylabel("Campaign Count")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 100,
            f"{int(bar.get_height()):,}",
            ha="center", fontsize=9)
plt.tight_layout()
path = f"{CHARTS_DIR}/02_campaigns_per_channel.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Avg ROI and Conversion Rate by Channel
# ─────────────────────────────────────────────────────────────────────────────
channel_avg = df.groupby("Channel_Used")[["ROI", "Conversion_Rate"]].mean().round(3)
print("\n[5] AVG ROI & CONVERSION RATE BY CHANNEL")
print(channel_avg.to_string())

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
channel_avg["ROI"].sort_values().plot(kind="barh", ax=axes[0], color="teal")
axes[0].set_title("Avg ROI by Channel")
axes[0].set_xlabel("ROI")

channel_avg["Conversion_Rate"].sort_values().plot(kind="barh", ax=axes[1], color="coral")
axes[1].set_title("Avg Conversion Rate by Channel")
axes[1].set_xlabel("Conversion Rate")

plt.suptitle("Channel Performance (Raw)", fontsize=13)
plt.tight_layout()
path = f"{CHARTS_DIR}/03_avg_roi_conversion_by_channel.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Correlation Heatmap
# ─────────────────────────────────────────────────────────────────────────────
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            square=True, linewidths=0.5, ax=ax)
ax.set_title("Correlation Heatmap", fontsize=13)
plt.tight_layout()
path = f"{CHARTS_DIR}/04_correlation_heatmap.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Campaign Type Pie
# ─────────────────────────────────────────────────────────────────────────────
ct_counts = df["Campaign_Type"].value_counts()
fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(ct_counts.values, labels=ct_counts.index,
       autopct="%1.1f%%", startangle=140,
       colors=sns.color_palette("pastel", len(ct_counts)))
ax.set_title("Campaign Type Distribution", fontsize=13)
plt.tight_layout()
path = f"{CHARTS_DIR}/05_campaign_type_pie.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 6 — Monthly Campaign Trend
# ─────────────────────────────────────────────────────────────────────────────
df["Date"]  = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M")
monthly     = df.groupby("Month").size().reset_index(name="Count")

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(monthly["Month"].astype(str), monthly["Count"],
        marker="o", color="purple", linewidth=2)
ax.set_title("Monthly Campaign Count — 2021", fontsize=13)
ax.set_xlabel("Month")
ax.set_ylabel("Campaigns")
plt.xticks(rotation=45)
plt.tight_layout()
path = f"{CHARTS_DIR}/06_monthly_trend.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 7 — Engagement Score by Customer Segment (boxplot)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
sns.boxplot(data=df, x="Customer_Segment", y="Engagement_Score",
            palette="Set2", ax=ax)
ax.set_title("Engagement Score by Customer Segment", fontsize=13)
ax.set_xlabel("Customer Segment")
ax.set_ylabel("Engagement Score")
plt.tight_layout()
path = f"{CHARTS_DIR}/07_engagement_by_segment.png"
plt.savefig(path, bbox_inches="tight")
plt.close()
print(f"[CHART] Saved → {path}")

print("\n[DONE] EDA complete. All charts saved to reports/charts/")
print("       Next step → run: python src/data_cleaner.py")