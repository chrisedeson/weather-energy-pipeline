"""
Data loading utilities for the Weather-Energy Dashboard
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import requests

# ---- Configuration
DATA_URL = "https://raw.githubusercontent.com/chrisedeson/weather-energy-pipeline/master/data/merged_data.parquet"
REPORT_URL = "https://raw.githubusercontent.com/chrisedeson/weather-energy-pipeline/master/data/quality_report.json"
ANOMALIES_URL = "https://raw.githubusercontent.com/chrisedeson/weather-energy-pipeline/master/data/anomalies.csv"

@st.cache_data
def load_data():
    """Load main dataset with fallback options"""
    try:
        # Try to load from GitHub first
        return pd.read_parquet(DATA_URL)
    except Exception as e:
        st.warning("⚠️ Could not load data from GitHub. Using local data if available.")
        # Fallback to local data
        local_path = Path("data/merged_data.parquet")
        if local_path.exists():
            return pd.read_parquet(local_path)
        else:
            # Try CSV as last resort
            csv_path = Path("data/merged_data.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path, parse_dates=["date"])
                st.info("📄 Using local CSV data. Run pipeline to generate parquet file.")
                return df
            else:
                st.error("❌ No data files found. Please run the data pipeline first.")
                return pd.DataFrame()

@st.cache_data
def load_quality_report():
    """Load data quality report with fallback options"""
    try:
        # Read JSON from GitHub
        response = requests.get(REPORT_URL)
        response.raise_for_status()
        return response.json()
    except:
        # Fallback to local file
        local_path = Path("data/quality_report.json")
        if local_path.exists():
            with open(local_path) as f:
                return json.load(f)
        return {}

@st.cache_data
def load_anomalies():
    """Load anomalies data with fallback options"""
    try:
        return pd.read_csv(ANOMALIES_URL, parse_dates=["date"])
    except:
        # Fallback to local file
        local_path = Path("data/anomalies.csv")
        if local_path.exists():
            return pd.read_csv(local_path, parse_dates=["date"])
        return pd.DataFrame()

def get_filtered_data(df, selected_cities):
    """Filter dataframe by selected cities"""
    if not selected_cities:
        return df
    return df[df["city"].isin(selected_cities)]
