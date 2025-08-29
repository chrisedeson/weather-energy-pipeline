# src/transform.py

import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
MERGED_DIR = Path("data")
MERGED_DIR.mkdir(parents=True, exist_ok=True)


def clean_weather_data():
    weather_df = pd.read_csv(RAW_DIR / "weather_all.csv")
    weather_df["date"] = pd.to_datetime(weather_df["date"])
    weather_df["avg_temp_f"] = (weather_df["TMAX_F"] + weather_df["TMIN_F"]) / 2
    weather_df["temp_delta_f"] = weather_df["TMAX_F"] - weather_df["TMIN_F"]
    return weather_df[["date", "city", "avg_temp_f", "temp_delta_f"]]


def clean_energy_data():
    energy_df = pd.read_csv(RAW_DIR / "energy_all.csv")
    energy_df["date"] = pd.to_datetime(energy_df["date"])
    return energy_df[["date", "city", "energy_mwh"]].rename(columns={"energy_mwh": "energy_consumption"})


def merge_data():
    logger.info("Cleaning weather data...")
    weather_df = clean_weather_data()

    logger.info("Cleaning energy data...")
    energy_df = clean_energy_data()

    logger.info("Merging datasets...")
    merged_df = pd.merge(weather_df, energy_df, on=["date", "city"], how="inner")

    merged_df.sort_values(by=["city", "date"], inplace=True)
    output_file = MERGED_DIR / "merged_data.parquet"
    merged_df.to_parquet(output_file, index=False)
    logger.info(f"Merged data saved to {output_file}")


if __name__ == "__main__":
    merge_data()
