# src/anomaly_detection.py

import pandas as pd
from sklearn.ensemble import IsolationForest
from pathlib import Path

INPUT_PATH = Path("data/merged_data.csv")
OUTPUT_PATH = Path("data/anomalies.csv")

def detect_anomalies(df):
    model = IsolationForest(contamination=0.02, random_state=42)
    df = df.copy()
    df["anomaly"] = model.fit_predict(df[["avg_temp_f", "temp_delta_f", "energy_consumption"]])
    anomalies = df[df["anomaly"] == -1]
    return anomalies.drop(columns=["anomaly"])

def main():
    df = pd.read_csv(INPUT_PATH)
    df["date"] = pd.to_datetime(df["date"])
    anomalies = detect_anomalies(df)
    anomalies.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Saved {len(anomalies)} anomalies to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
