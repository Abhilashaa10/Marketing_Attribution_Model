import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 1. READ THE ORIGINAL DATA 
print("Loading original dataset from 'data' folder...")

original_data = pd.read_csv('data/marketing_campaign_dataset.csv')

channels_list = original_data['Channel_Used'].unique().tolist()
print("Channels found:", channels_list)

# 2. CONFIGURATION
total_journeys = 20000  
all_rows = []            

print("Generating customer journeys... Please wait a moment.")

# 3. GENERATION LOOP
for i in range(total_journeys):
    journey_id = f"JRN_{100000 + i}"
    customer_id = f"CUST_{20000 + random.randint(1, 15000)}"
    
    converted = random.choice([1, 0, 0, 0, 0, 0, 0]) 
    
    if converted == 1:
        revenue = round(random.uniform(50.0, 500.0), 2)
    else:
        revenue = 0.0
        
    start_date = datetime(2021, 1, 1) + timedelta(days=random.randint(0, 300))
    
    # Number of steps in their journey (1 to 4 marketing clicks)
    number_of_clicks = random.randint(1, 4)
    
    for step in range(number_of_clicks):
        chosen_channel = random.choice(channels_list)
        
        click_time = start_date + timedelta(days=step * random.randint(1, 3))
        
        row_dictionary = {
            'Customer_ID': customer_id,
            'Journey_ID': journey_id,
            'Marketing_Channel': chosen_channel,
            'Interaction_Timestamp': click_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Conversion_Flag': converted,
            'Revenue_Amount': revenue
        }
        all_rows.append(row_dictionary)

# 4. CONVERT TO DATAFRAME AND SAVE TO THE DATA FOLDER
new_dataset = pd.DataFrame(all_rows)

new_dataset = new_dataset.sort_values(by=['Journey_ID', 'Interaction_Timestamp'])

new_dataset.to_csv('data/customer_journeys.csv', index=False)

print("\nSuccess! 'customer_journeys.csv' has been created inside the 'data' folder.")
print("Preview of your new data:")
print(new_dataset.head(8))