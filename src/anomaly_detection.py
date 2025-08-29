# src/anomaly_detection.py

import pandas as pd
from sklearn.ensemble import IsolationForest
from pathlib import Path

INPUT_PATH = Path("data/merged_data.parquet")
OUTPUT_PATH = Path("data/anomalies.csv")

def detect_anomalies(df):
    """
    Detect anomalies in the dataset using Isolation Forest.
    This version groups by city first to find anomalies within each city's patterns,
    which provides more realistic and varied results.
    """
    all_anomalies = []
    
    # Process each city separately to find city-specific anomalies
    for city, city_df in df.groupby("city"):
        if len(city_df) < 10:  # Skip cities with too few data points
            continue
            
        model = IsolationForest(contamination=0.02, random_state=42)
        city_df = city_df.copy()
        
        # Detect anomalies based on patterns within this city
        city_df["anomaly"] = model.fit_predict(city_df[["avg_temp_f", "temp_delta_f", "energy_consumption"]])
        city_anomalies = city_df[city_df["anomaly"] == -1]
        
        # Add to our collection
        all_anomalies.append(city_anomalies)
    
    # Combine results from all cities
    if all_anomalies:
        result = pd.concat(all_anomalies)
        return result.drop(columns=["anomaly"])
    else:
        return pd.DataFrame(columns=df.columns)

def main():
    df = pd.read_parquet(INPUT_PATH)
    df["date"] = pd.to_datetime(df["date"])
    anomalies = detect_anomalies(df)
    anomalies.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Saved {len(anomalies)} anomalies to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
