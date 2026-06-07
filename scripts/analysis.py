import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# ── CONNECT & LOAD ────────────────────────────────────────────
print("Loading data...")
engine = create_engine("postgresql://postgres:Abhi%4010@localhost:5432/marketing_attribution")

df = pd.read_csv('data/customer_journeys.csv', parse_dates=['Interaction_Timestamp'])
attr = pd.read_sql('SELECT * FROM channel_attribution_summary', engine)

print(f"Loaded {len(df):,} touchpoints | {df['Journey_ID'].nunique():,} journeys | {df['Customer_ID'].nunique():,} customers")

# ── PREP ──────────────────────────────────────────────────────
df = df.sort_values(['Journey_ID', 'Interaction_Timestamp'])
df['Total_Touchpoints'] = df.groupby('Journey_ID')['Interaction_Timestamp'].transform('count')
df['Touchpoint_Position'] = df.groupby('Journey_ID')['Interaction_Timestamp'].rank(method='first')
df['Month'] = df['Interaction_Timestamp'].dt.month
df['Month_Name'] = df['Interaction_Timestamp'].dt.strftime('%b')

# ── KPI SUMMARY ───────────────────────────────────────────────
print("\n" + "="*55)
print("  KEY PERFORMANCE INDICATORS")
print("="*55)

total_journeys    = df['Journey_ID'].nunique()
total_customers   = df['Customer_ID'].nunique()
converted_journeys= df[df['Conversion_Flag'] == 1]['Journey_ID'].nunique()
total_revenue     = df['Revenue_Amount'].sum()
avg_order_value   = df[df['Revenue_Amount'] > 0]['Revenue_Amount'].mean()
conversion_rate   = converted_journeys / total_journeys * 100
avg_touchpoints   = df.groupby('Journey_ID').size().mean()

print(f"  Total Customers       : {total_customers:,}")
print(f"  Total Journeys        : {total_journeys:,}")
print(f"  Converted Journeys    : {converted_journeys:,}")
print(f"  Conversion Rate       : {conversion_rate:.1f}%")
print(f"  Total Revenue         : ${total_revenue:,.2f}")
print(f"  Avg Order Value       : ${avg_order_value:.2f}")
print(f"  Avg Touchpoints/Journey: {avg_touchpoints:.2f}")

# ── ANALYSIS 1: CHANNEL PERFORMANCE ──────────────────────────
print("\n" + "="*55)
print("  CHANNEL PERFORMANCE")
print("="*55)

channel_stats = df.groupby('Marketing_Channel').agg(
    Total_Touchpoints = ('Journey_ID', 'count'),
    Unique_Journeys   = ('Journey_ID', 'nunique'),
    Conversions       = ('Conversion_Flag', 'sum'),
    Revenue           = ('Revenue_Amount', 'sum'),
).reset_index()

channel_stats['Conversion_Rate_%'] = (
    channel_stats['Conversions'] / channel_stats['Unique_Journeys'] * 100
).round(2)

channel_stats['Avg_Revenue'] = (
    channel_stats['Revenue'] / channel_stats['Conversions']
).round(2)

channel_stats['Revenue_%'] = (
    channel_stats['Revenue'] / channel_stats['Revenue'].sum() * 100
).round(2)

channel_stats = channel_stats.sort_values('Revenue', ascending=False)
print(channel_stats.to_string(index=False))

# ── ANALYSIS 2: JOURNEY LENGTH vs CONVERSION ─────────────────
print("\n" + "="*55)
print("  JOURNEY LENGTH vs CONVERSION RATE")
print("="*55)

journey_summary = df.drop_duplicates('Journey_ID')[['Journey_ID','Total_Touchpoints','Conversion_Flag','Revenue_Amount']]
length_analysis = journey_summary.groupby('Total_Touchpoints').agg(
    Total_Journeys = ('Journey_ID', 'count'),
    Conversions    = ('Conversion_Flag', 'sum'),
    Total_Revenue  = ('Revenue_Amount', 'sum'),
).reset_index()

length_analysis['Conversion_Rate_%'] = (
    length_analysis['Conversions'] / length_analysis['Total_Journeys'] * 100
).round(2)

length_analysis['Avg_Revenue'] = (
    length_analysis['Total_Revenue'] / length_analysis['Conversions'].replace(0, np.nan)
).round(2)

print(length_analysis.to_string(index=False))

# ── ANALYSIS 3: MONTHLY TREND ─────────────────────────────────
print("\n" + "="*55)
print("  MONTHLY PERFORMANCE TREND")
print("="*55)

monthly = df.groupby(['Month', 'Month_Name']).agg(
    Touchpoints   = ('Journey_ID', 'count'),
    Conversions   = ('Conversion_Flag', 'sum'),
    Revenue       = ('Revenue_Amount', 'sum'),
).reset_index().sort_values('Month')

monthly['Conversion_Rate_%'] = (
    monthly['Conversions'] / monthly['Touchpoints'] * 100
).round(2)

print(monthly[['Month_Name','Touchpoints','Conversions','Revenue','Conversion_Rate_%']].to_string(index=False))

# ── ANALYSIS 4: FIRST TOUCH CHANNEL ANALYSIS ─────────────────
print("\n" + "="*55)
print("  FIRST TOUCH — BEST DISCOVERY CHANNELS")
print("="*55)

first_touches = df[df['Touchpoint_Position'] == 1].copy()
first_touch_conv = first_touches.merge(
    df.drop_duplicates('Journey_ID')[['Journey_ID','Conversion_Flag','Revenue_Amount']],
    on='Journey_ID'
)
ft_summary = first_touch_conv.groupby('Marketing_Channel').agg(
    Times_First_Touch = ('Journey_ID', 'count'),
    Led_To_Conversion = ('Conversion_Flag_y', 'sum'),
    Revenue_Driven    = ('Revenue_Amount_y', 'sum'),
).reset_index()

ft_summary['Discovery_Conv_Rate_%'] = (
    ft_summary['Led_To_Conversion'] / ft_summary['Times_First_Touch'] * 100
).round(2)

ft_summary = ft_summary.sort_values('Revenue_Driven', ascending=False)
print(ft_summary.to_string(index=False))

# ── ANALYSIS 5: LAST TOUCH CHANNEL ANALYSIS ──────────────────
print("\n" + "="*55)
print("  LAST TOUCH — BEST CLOSING CHANNELS")
print("="*55)

last_touches = df[df['Touchpoint_Position'] == df['Total_Touchpoints']].copy()
last_touch_conv = last_touches[last_touches['Conversion_Flag'] == 1]

lt_summary = last_touch_conv.groupby('Marketing_Channel').agg(
    Times_Closed  = ('Journey_ID', 'count'),
    Revenue_Closed= ('Revenue_Amount', 'sum'),
).reset_index()

lt_summary['Avg_Close_Revenue'] = (
    lt_summary['Revenue_Closed'] / lt_summary['Times_Closed']
).round(2)

lt_summary = lt_summary.sort_values('Revenue_Closed', ascending=False)
print(lt_summary.to_string(index=False))

# ── ANALYSIS 6: TOP CONVERSION PATHS ─────────────────────────
print("\n" + "="*55)
print("  TOP 10 CONVERSION PATHS")
print("="*55)

converted_df = df[df['Conversion_Flag'] == 1]
paths = converted_df.sort_values(['Journey_ID','Touchpoint_Position'])\
    .groupby('Journey_ID')['Marketing_Channel']\
    .apply(lambda x: ' → '.join(x))\
    .reset_index()
paths.columns = ['Journey_ID', 'Path']

path_revenue = converted_df.drop_duplicates('Journey_ID')[['Journey_ID','Revenue_Amount']]
paths = paths.merge(path_revenue, on='Journey_ID')

path_summary = paths.groupby('Path').agg(
    Count          = ('Journey_ID', 'count'),
    Total_Revenue  = ('Revenue_Amount', 'sum'),
    Avg_Revenue    = ('Revenue_Amount', 'mean'),
).reset_index().nlargest(10, 'Count')

path_summary['Total_Revenue'] = path_summary['Total_Revenue'].round(2)
path_summary['Avg_Revenue']   = path_summary['Avg_Revenue'].round(2)
print(path_summary.to_string(index=False))

# ── ANALYSIS 7: ATTRIBUTION MODEL COMPARISON ─────────────────
print("\n" + "="*55)
print("  ATTRIBUTION MODEL COMPARISON")
print("="*55)

models = ['First_Touch_Revenue','Last_Touch_Revenue','Linear_Revenue',
          'Time_Decay_Revenue','Position_Based_Revenue']

if all(col in attr.columns for col in models):
    for model in models:
        attr[model.replace('_Revenue','_%')] = (
            attr[model] / attr[model].sum() * 100
        ).round(2)

    pct_cols = ['Marketing_Channel'] + [m.replace('_Revenue','_%') for m in models]
    print(attr[pct_cols].to_string(index=False))
else:
    print("  Run calculate_attribution.py first to see this section.")

# ── SAVE ANALYSIS OUTPUTS ─────────────────────────────────────
print("\nSaving analysis outputs...")
channel_stats.to_csv('data/channel_performance.csv', index=False)
monthly.to_csv('data/monthly_trend.csv', index=False)
path_summary.to_csv('data/top_conversion_paths.csv', index=False)

print("Saved:")
print("  data/channel_performance.csv")
print("  data/monthly_trend.csv")
print("  data/top_conversion_paths.csv")
print("\n✅ Analysis complete. Ready for visualizations.")