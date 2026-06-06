import pandas as pd
from sqlalchemy import create_engine

print("Reading your generated customer journeys...")
df = pd.read_csv('data/customer_journeys.csv')

# 2. Connect to your local PostgreSQL database
# REPLACE 'postgres' with your actual username, 'your_password' with your real password,
# and 'localhost' or port numbers if you changed them during PostgreSQL installation.
username = 'postgres'
password = 'Abhi@10'
host = 'localhost'
port = '5432'
database_name = 'marketing_attribution'

# This line builds the connection bridge
connection_string = f"postgresql://postgres:Abhi%4010@localhost:5432/marketing_attribution"
print(connection_string)
engine = create_engine(connection_string)

print("Uploading data to PostgreSQL... This takes just a few seconds.")
# 3. Push the entire dataframe into a new table named 'raw_customer_journeys'
# 'if_exists=replace' means if the table is already there, it clears it out and starts fresh
df.to_sql('raw_customer_journeys', engine, if_exists='replace', index=False)

print("\nSuccess! The 'raw_customer_journeys' table has been created in PostgreSQL.")