import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sqlalchemy import create_engine
import os

# ── SETUP ─────────────────────────────────────────────────────
os.makedirs('screenshots', exist_ok=True)

engine = create_engine("postgresql://postgres:Abhi%4010@localhost:5432/marketing_attribution")

df       = pd.read_csv('data/customer_journeys.csv', parse_dates=['Interaction_Timestamp'])
ch_perf  = pd.read_csv('data/channel_performance.csv')
monthly  = pd.read_csv('data/monthly_trend.csv')
paths    = pd.read_csv('data/top_conversion_paths.csv')
attr     = pd.read_sql('SELECT * FROM channel_attribution_summary', engine)

# ── STYLE ─────────────────────────────────────────────────────
CHANNEL_COLORS = {
    'Google Ads': '#4285F4',
    'Email':      '#F4A261',
    'YouTube':    '#FF0000',
    'Facebook':   '#1877F2',
    'Instagram':  '#E1306C',
    'Website':    '#2ECC71',
}

plt.rcParams.update({
    'figure.facecolor':  '#0F1117',
    'axes.facecolor':    '#1A1D27',
    'axes.edgecolor':    '#2E3348',
    'axes.labelcolor':   '#E0E6F0',
    'xtick.color':       '#A0AABB',
    'ytick.color':       '#A0AABB',
    'text.color':        '#E0E6F0',
    'grid.color':        '#2E3348',
    'grid.linewidth':    0.8,
    'font.family':       'DejaVu Sans',
})

CHANNELS = ch_perf['Marketing_Channel'].tolist()
COLORS   = [CHANNEL_COLORS[c] for c in CHANNELS]

print("Generating charts...")

# ══════════════════════════════════════════════════════════════
# CHART 1 — REVENUE BY CHANNEL
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0F1117')
sorted_ch = ch_perf.sort_values('Revenue', ascending=True)
colors = [CHANNEL_COLORS[c] for c in sorted_ch['Marketing_Channel']]

bars = ax.barh(sorted_ch['Marketing_Channel'],
               sorted_ch['Revenue'],
               color=colors, height=0.6, edgecolor='none')

for bar, val in zip(bars, sorted_ch['Revenue']):
    ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
            f'${val:,.0f}', va='center', fontsize=10)

ax.set_title('Total Revenue by Marketing Channel', fontsize=14,
             fontweight='bold', color='white', pad=15)
ax.set_xlabel('Revenue ($)')
ax.grid(axis='x', alpha=0.3)
ax.spines[['top','right','left','bottom']].set_visible(False)
plt.tight_layout()
plt.savefig('screenshots/01_revenue_by_channel.png', dpi=150,
            bbox_inches='tight', facecolor='#0F1117')
plt.close()
print("  ✅ 01_revenue_by_channel.png")

# ══════════════════════════════════════════════════════════════
# CHART 2 — CONVERSION RATE BY CHANNEL
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0F1117')
sorted_cv = ch_perf.sort_values('Conversion_Rate_%', ascending=True)
colors = [CHANNEL_COLORS[c] for c in sorted_cv['Marketing_Channel']]

bars = ax.barh(sorted_cv['Marketing_Channel'],
               sorted_cv['Conversion_Rate_%'],
               color=colors, height=0.6, edgecolor='none')

for bar, val in zip(bars, sorted_cv['Conversion_Rate_%']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=10)

ax.set_title('Conversion Rate by Channel', fontsize=14,
             fontweight='bold', color='white', pad=15)
ax.set_xlabel('Conversion Rate (%)')
ax.grid(axis='x', alpha=0.3)
ax.spines[['top','right','left','bottom']].set_visible(False)
plt.tight_layout()
plt.savefig('screenshots/02_conversion_rate_by_channel.png', dpi=150,
            bbox_inches='tight', facecolor='#0F1117')
plt.close()
print("  ✅ 02_conversion_rate_by_channel.png")

# ══════════════════════════════════════════════════════════════
# CHART 3 — ATTRIBUTION MODEL COMPARISON
# ══════════════════════════════════════════════════════════════
models     = ['First_Touch_Revenue','Last_Touch_Revenue','Linear_Revenue',
              'Time_Decay_Revenue','Position_Based_Revenue']
model_labels = ['First Touch','Last Touch','Linear','Time Decay','Position Based']
model_colors = ['#E74C3C','#3498DB','#2ECC71','#F39C12','#9B59B6']

fig, axes = plt.subplots(1, 5, figsize=(22, 7), facecolor='#0F1117')
fig.suptitle('Attribution Model Comparison — Revenue by Channel',
             fontsize=15, fontweight='bold', color='white', y=1.02)

for ax, model, label, mcolor in zip(axes, models, model_labels, model_colors):
    if model not in attr.columns:
        ax.set_visible(False)
        continue

    data = attr[['Marketing_Channel', model]].sort_values(model, ascending=False)
    colors = [CHANNEL_COLORS[c] for c in data['Marketing_Channel']]

    bars = ax.bar(range(len(data)), data[model] / 1000,
                  color=colors, edgecolor='none', width=0.65)

    for bar, val in zip(bars, data[model]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'${val/1000:.1f}K', ha='center', fontsize=8)

    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(
        [c.replace(' Ads','').replace(' Search','') for c in data['Marketing_Channel']],
        rotation=25, ha='right', fontsize=8)
    ax.set_title(label, color=mcolor, fontweight='bold', pad=8)
    ax.set_ylabel('Revenue ($K)' if ax == axes[0] else '')
    ax.grid(axis='y', alpha=0.3)
    ax.spines[['top','right']].set_visible(False)

plt.tight_layout()
plt.savefig('screenshots/03_attribution_model_comparison.png', dpi=150,
            bbox_inches='tight', facecolor='#0F1117')
plt.close()
print("  ✅ 03_attribution_model_comparison.png")

# ══════════════════════════════════════════════════════════════
# CHART 4 — CONTRIBUTION HEATMAP
# ══════════════════════════════════════════════════════════════
pct_cols = [c for c in attr.columns if c.endswith('_Pct')]

if pct_cols:
    pivot = attr.set_index('Marketing_Channel')[pct_cols]
    pivot.columns = [c.replace('_Pct','').replace('_',' ') for c in pct_cols]

    fig, ax = plt.subplots(figsize=(13, 6), facecolor='#0F1117')
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd',
                linewidths=0.5, linecolor='#0F1117', ax=ax,
                annot_kws={'size': 12, 'weight': 'bold'},
                cbar_kws={'label': 'Revenue Contribution %'})
    ax.set_title('Channel Revenue Contribution % by Attribution Model',
                 fontsize=14, fontweight='bold', color='white', pad=15)
    ax.tick_params(colors='#E0E6F0')
    plt.tight_layout()
    plt.savefig('screenshots/04_contribution_heatmap.png', dpi=150,
                bbox_inches='tight', facecolor='#0F1117')
    plt.close()
    print("  ✅ 04_contribution_heatmap.png")

# ══════════════════════════════════════════════════════════════
# CHART 5 — MONTHLY REVENUE TREND
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 6), facecolor='#0F1117')
month_names = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']
monthly['Month_Label'] = monthly['Month'].apply(
    lambda x: month_names[int(x)-1])

ax.fill_between(monthly['Month'], monthly['Revenue'],
                alpha=0.2, color='#4ADE80')
ax.plot(monthly['Month'], monthly['Revenue'],
        color='#4ADE80', linewidth=2.5, marker='o', markersize=6)

for _, row in monthly.iterrows():
    ax.text(row['Month'], row['Revenue'] + 200,
            f"${row['Revenue']:,.0f}", ha='center', fontsize=8)

ax.set_xticks(monthly['Month'])
ax.set_xticklabels(monthly['Month_Label'])
ax.set_title('Monthly Revenue Trend 2021', fontsize=14,
             fontweight='bold', color='white', pad=15)
ax.set_xlabel('Month')
ax.set_ylabel('Revenue ($)')
ax.grid(alpha=0.3)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('screenshots/05_monthly_revenue_trend.png', dpi=150,
            bbox_inches='tight', facecolor='#0F1117')
plt.close()
print("  ✅ 05_monthly_revenue_trend.png")

# ══════════════════════════════════════════════════════════════
# CHART 6 — CONVERSION FUNNEL
# ══════════════════════════════════════════════════════════════
total_journeys     = df['Journey_ID'].nunique()
multi_touch        = df[df['Total_Touchpoints'] >= 2]['Journey_ID'].nunique() \
    if 'Total_Touchpoints' in df.columns else \
    df.groupby('Journey_ID').size()[df.groupby('Journey_ID').size() >= 2].count()
converted = df[df['Conversion_Flag'] == 1]['Journey_ID'].nunique()

funnel_stages  = ['All Journeys', 'Multi-Touch\n(2+ touches)', 'Converted']
funnel_values  = [total_journeys, multi_touch, converted]
funnel_colors  = ['#4285F4', '#F4A261', '#2ECC71']

fig, ax = plt.subplots(figsize=(11, 6), facecolor='#0F1117')
bar_widths = [0.85, 0.65, 0.45]

for i, (stage, val, bw, col) in enumerate(
        zip(funnel_stages, funnel_values, bar_widths, funnel_colors)):
    ax.barh(i, val, color=col, alpha=0.85, height=bw, edgecolor='none')
    pct = val / total_journeys * 100
    ax.text(val + 100, i, f'{val:,}  ({pct:.1f}%)',
            va='center', fontsize=11)

ax.set_yticks(range(len(funnel_stages)))
ax.set_yticklabels(funnel_stages, fontsize=11)
ax.set_title('Customer Journey Conversion Funnel', fontsize=14,
             fontweight='bold', color='white', pad=15)
ax.set_xlabel('Number of Journeys')
ax.grid(axis='x', alpha=0.3)
ax.spines[['top','right','left','bottom']].set_visible(False)
plt.tight_layout()
plt.savefig('screenshots/06_conversion_funnel.png', dpi=150,
            bbox_inches='tight', facecolor='#0F1117')
plt.close()
print("  ✅ 06_conversion_funnel.png")

# ══════════════════════════════════════════════════════════════
# CHART 7 — TOP CONVERSION PATHS
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 7), facecolor='#0F1117')
top8 = paths.head(8).sort_values('Count', ascending=True)

bars = ax.barh(top8['Path'], top8['Count'],
               color='#4285F4', height=0.6, edgecolor='none')

for bar, val in zip(bars, top8['Count']):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            str(val), va='center', fontsize=10)

ax.set_title('Top Conversion Paths (First → Last Touch)',
             fontsize=14, fontweight='bold', color='white', pad=15)
ax.set_xlabel('Number of Conversions')
ax.grid(axis='x', alpha=0.3)
ax.spines[['top','right','left','bottom']].set_visible(False)
plt.tight_layout()
plt.savefig('screenshots/07_top_conversion_paths.png', dpi=150,
            bbox_inches='tight', facecolor='#0F1117')
plt.close()
print("  ✅ 07_top_conversion_paths.png")

# ══════════════════════════════════════════════════════════════
# CHART 8 — TOUCHPOINTS DISTRIBUTION
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0F1117')
tp_dist = df.groupby('Journey_ID').size().value_counts().sort_index()
bar_colors = ['#4285F4','#1877F2','#2ECC71','#F4A261']

bars = ax.bar(tp_dist.index, tp_dist.values,
              color=bar_colors[:len(tp_dist)],
              edgecolor='none', width=0.6)

for bar, val in zip(bars, tp_dist.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
            f'{val:,}', ha='center', fontsize=11)

ax.set_xticks(tp_dist.index)
ax.set_xticklabels([f'{i} touch' for i in tp_dist.index])
ax.set_title('Journey Length Distribution', fontsize=14,
             fontweight='bold', color='white', pad=15)
ax.set_ylabel('Number of Journeys')
ax.grid(axis='y', alpha=0.3)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('screenshots/08_touchpoints_distribution.png', dpi=150,
            bbox_inches='tight', facecolor='#0F1117')
plt.close()
print("  ✅ 08_touchpoints_distribution.png")

print("\n✅ All 8 charts saved to screenshots/")