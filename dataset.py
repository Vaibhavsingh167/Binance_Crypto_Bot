import sqlite3
import pandas as pd

# Connect to your database
conn = sqlite3.connect("trading_bot.db")

# Read the table
df = pd.read_sql_query("SELECT * FROM market_data", conn)

# Save to CSV
df.to_csv("market_data.csv", index=False)

conn.close()

print("CSV file created successfully!")