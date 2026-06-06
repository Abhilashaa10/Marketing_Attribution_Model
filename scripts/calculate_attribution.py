import pandas as pd
from sqlalchemy import create_engine

print("Connecting to PostgreSQL...")
engine = create_engine("postgresql://postgres:Abhi%4010@localhost:5432/marketing_attribution")
df = pd.read_sql('SELECT * FROM raw_customer_journeys', engine)
print(f"Loaded {len(df):,} rows")

print("Sequencing touchpoints...")
df['Interaction_Timestamp'] = pd.to_datetime(df['Interaction_Timestamp'])
df = df.sort_values(['Journey_ID', 'Interaction_Timestamp'])

df['Total_Touchpoints'] = df.groupby('Journey_ID')['Interaction_Timestamp'].transform('count')
df['Touchpoint_Position'] = df.groupby('Journey_ID')['Interaction_Timestamp'].rank(method='first')

print("Calculating all 5 attribution models...")

#  MODEL 1: FIRST TOUCH
df['First_Touch'] = 0.0
df.loc[df['Touchpoint_Position'] == 1, 'First_Touch'] = df['Revenue_Amount']

#  MODEL 2: LAST TOUCH 
df['Last_Touch'] = 0.0
df.loc[df['Touchpoint_Position'] == df['Total_Touchpoints'], 'Last_Touch'] = df['Revenue_Amount']

#  MODEL 3: LINEAR 
df['Linear'] = df['Revenue_Amount'] / df['Total_Touchpoints']

#  MODEL 4: TIME DECAY 

journey_end = df.groupby('Journey_ID')['Interaction_Timestamp'].transform('max')
df['Days_Before_End'] = (journey_end - df['Interaction_Timestamp']).dt.total_seconds() / 86400

import numpy as np
df['Decay_Weight'] = np.exp(-0.1 * df['Days_Before_End'])

df['Weight_Sum'] = df.groupby('Journey_ID')['Decay_Weight'].transform('sum')
df['Time_Decay'] = df['Revenue_Amount'] * (df['Decay_Weight'] / df['Weight_Sum'])

#  MODEL 5: POSITION BASED (U-SHAPED) 
# First touch = 40%, Last touch = 40%, Middle touches share 20%
def position_credit(row):
    n = row['Total_Touchpoints']
    pos = row['Touchpoint_Position']
    rev = row['Revenue_Amount']

    if n == 1:
        return rev                          # only one touch, gets everything
    elif n == 2:
        return rev * 0.5                    # split evenly if only 2 touches
    else:
        if pos == 1:
            return rev * 0.40               # first touch
        elif pos == n:
            return rev * 0.40               # last touch
        else:
            return rev * 0.20 / (n - 2)    # middle touches share 20%

df['Position_Based'] = df.apply(position_credit, axis=1)

print("Summarizing by channel...")
summary = df.groupby('Marketing_Channel').agg(
    First_Touch_Revenue   = ('First_Touch',    'sum'),
    Last_Touch_Revenue    = ('Last_Touch',     'sum'),
    Linear_Revenue        = ('Linear',         'sum'),
    Time_Decay_Revenue    = ('Time_Decay',     'sum'),
    Position_Based_Revenue= ('Position_Based', 'sum'),
    Total_Conversions     = ('Converted',      'sum'),
    Total_Touchpoints     = ('Journey_ID',     'count'),
).round(2)

for col in ['First_Touch_Revenue','Last_Touch_Revenue','Linear_Revenue',
            'Time_Decay_Revenue','Position_Based_Revenue']:
    pct_col = col.replace('_Revenue', '_Pct')
    summary[pct_col] = (summary[col] / summary[col].sum() * 100).round(2)

print("\n=== ATTRIBUTION RESULTS ===")
print(summary.to_string())

print("\nSaving results...")
summary.to_sql('channel_attribution_summary', engine, if_exists='replace')
summary.to_csv('data/attribution_results.csv')
print("Done! Table 'channel_attribution_summary' saved to PostgreSQL.")
print("Done! 'data/attribution_results.csv' saved locally.")