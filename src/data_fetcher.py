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

def fetch_energy_data(city_config, start_date, end_date):
    region_code = city_config["eia_region_code"]
    city_name = city_config["name"]

    logger.info(f"Fetching energy data for {city_name} ({region_code})")

    url = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/"
    params = {
        "api_key": api_keys["EIA"],
        "data[]": "value",
        "facets[respondent][]": region_code,
        "start": start_date,
        "end": end_date,
        "frequency": "daily"
    }

    retries = 3
    data = []

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()["response"]["data"]
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for {city_name} energy: {e}")
            time.sleep(2 * (attempt + 1))

    if not data:
        logger.error(f"Failed to fetch energy data for {city_name}")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["period"] = pd.to_datetime(df["period"].str[:10])
    df = df.rename(columns={"period": "date", "value": "energy_mwh"})
    df["city"] = city_name

    # 🔧 FIX: Filter to only use "Demand" data type (actual consumption, always positive)
    demand_data = df[df["type-name"] == "Demand"].copy()

    if len(demand_data) == 0:
        logger.warning(f"No demand data found for {city_name}, using all data")
        return df

    logger.info(f"Filtered to {len(demand_data)} demand records for {city_name} (removed interchange/net generation data)")
    return demand_data
