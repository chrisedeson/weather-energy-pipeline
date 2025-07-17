from datetime import datetime, timedelta
from config_loader import load_config
from data_fetcher import fetch_weather_data
import pandas as pd
import os

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

config = load_config()
cities = config["cities"]
days = config["general"]["fetch_days"]

end_date = datetime.today()
start_date = end_date - timedelta(days=days)

all_data = []

for city in cities:
    df = fetch_weather_data(city, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    if df is not None:
        all_data.append(df)
        # Save per city
        file_name = f"{RAW_DIR}/weather_{city['name'].replace(' ', '_')}.csv"
        df.to_csv(file_name, index=False)

# Optionally, save all combined
if all_data:
    combined = pd.concat(all_data)
    combined.to_csv(f"{RAW_DIR}/weather_all.csv", index=False)
