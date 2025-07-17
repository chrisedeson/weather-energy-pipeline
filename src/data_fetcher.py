import requests
import pandas as pd
from datetime import datetime, timedelta
import time

from config_loader import load_config, get_api_keys
from logger import get_logger

logger = get_logger("weather_fetcher")
config = load_config()
api_keys = get_api_keys()

BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
HEADERS = {"token": api_keys["NOAA"]}


def fetch_weather_data(city_config, start_date, end_date):
    station_id = city_config["noaa_station_id"]
    city_name = city_config["name"]

    logger.info(f"Fetching weather data for {city_name} ({station_id})")

    params = {
        "datasetid": "GHCND",
        "stationid": station_id,
        "datatypeid": "TMAX,TMIN",
        "startdate": start_date,
        "enddate": end_date,
        "limit": 1000,
        "units": "standard"
    }

    all_results = []
    retries = 3

    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("results", [])
            all_results.extend(data)
            break  # Success!
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for {city_name}: {e}")
            time.sleep(2 * (attempt + 1))

    if not all_results:
        logger.error(f"Failed to fetch data for {city_name}")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(all_results)
    df["date"] = pd.to_datetime(df["date"])
    df = df.pivot_table(index="date", columns="datatype", values="value", aggfunc="first")
    df.columns.name = None

    # Convert temp from tenths of °C to °F
    df["TMAX_F"] = df["TMAX"] * 0.18 + 32 if "TMAX" in df else None
    df["TMIN_F"] = df["TMIN"] * 0.18 + 32 if "TMIN" in df else None

    df.reset_index(inplace=True)
    df["city"] = city_name

    return df
