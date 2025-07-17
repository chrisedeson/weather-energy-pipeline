import pandas as pd
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = Path("data/merged_data.csv")
REPORT_PATH = Path("data/quality_report.json")

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Merged data file not found at {DATA_PATH}")
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

def check_missing_values(df):
    missing_report = df.isnull().sum().to_dict()
    total_missing = sum(missing_report.values())
    logger.info(f"Total missing values: {total_missing}")
    return missing_report

def check_outliers(df):
    outlier_report = {}

    # Temperature outliers
    temp_outliers = df[(df["avg_temp_f"] > 130) | (df["avg_temp_f"] < -50)]
    outlier_report["temperature_outliers"] = len(temp_outliers)

    # Energy outliers (e.g., negative or unrealistic usage)
    energy_outliers = df[df["energy_consumption"] < 0]
    outlier_report["negative_energy_readings"] = len(energy_outliers)

    logger.info(f"Outliers found: {outlier_report}")
    return outlier_report

def check_freshness(df):
    latest_date = df["date"].max()
    freshness = pd.Timestamp.now().normalize() - latest_date
    is_fresh = freshness.days <= 1
    logger.info(f"Latest data date: {latest_date.date()}, Fresh: {is_fresh}")
    return {
        "latest_date": str(latest_date.date()),
        "is_fresh": is_fresh,
        "days_old": freshness.days
    }

def run_checks():
    logger.info("Running data quality checks...")
    df = load_data()

    report = {
        "missing_values": check_missing_values(df),
        "outliers": check_outliers(df),
        "freshness": check_freshness(df)
    }

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Quality report saved to {REPORT_PATH}")

if __name__ == "__main__":
    run_checks()
