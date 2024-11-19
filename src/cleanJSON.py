import json
import csv
import os
import sys
from datetime import datetime


modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
input_file = os.path.join(modpath, '../data/BRK-B.json')
csv_file_path = os.path.join(modpath, '../data/BRK-B.csv')  # Replace with the desired output CSV file path

with open(input_file, "r") as f:
    data = json.load(f)

# Navigate through the JSON structure
results = data.get("chart", {}).get("result", [])

# Prepare the CSV data
csv_data = []
csv_data.append(["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"])  # Header

for result in results:
    timestamps = result.get("timestamp", [])
    quotes = result.get("indicators", {}).get("quote", [{}])[0]
    adjcloses = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])

    opens = quotes.get("open", [])
    highs = quotes.get("high", [])
    lows = quotes.get("low", [])
    closes = quotes.get("close", [])
    volumes = quotes.get("volume", [])
    
    # Iterate through the data
    for i, timestamp in enumerate(timestamps):
        # Convert timestamp to date
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        
        # Extract values (handle missing data gracefully)
        open_price = opens[i] if i < len(opens) else None
        high_price = highs[i] if i < len(highs) else None
        low_price = lows[i] if i < len(lows) else None
        close_price = closes[i] if i < len(closes) else None
        adj_close = adjcloses[i] if i < len(adjcloses) else None
        volume = volumes[i] if i < len(volumes) else None
        
        # Append to CSV data
        csv_data.append([date, open_price, high_price, low_price, close_price, adj_close, volume])

# Write to CSV
with open(csv_file_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_data)

print(f"Data successfully written to {csv_file_path}")