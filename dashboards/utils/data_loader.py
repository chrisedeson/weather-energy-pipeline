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
        github_df = pd.read_parquet(DATA_URL)
        github_latest = github_df['date'].max()
        st.info(f"📡 GitHub data: {len(github_df):,} records up to {github_latest.strftime('%Y-%m-%d')}")

        # Check if local Parquet is fresher
        local_parquet = Path("data/merged_data.parquet")
        if local_parquet.exists():
            try:
                local_df = pd.read_parquet(local_parquet)
                local_latest = local_df['date'].max()
                st.info(f"💾 Local data: {len(local_df):,} records up to {local_latest.strftime('%Y-%m-%d')}")

                # Use local data if it's fresher
                if local_latest > github_latest:
                    st.success(f"✅ Using fresher local data ({local_latest.strftime('%Y-%m-%d')} vs {github_latest.strftime('%Y-%m-%d')})")
                    return local_df
                else:
                    st.info("✅ Using GitHub data (up to date)")
                    return github_df
            except Exception as pq_error:
                st.warning(f"⚠️ Could not read local Parquet: {pq_error}")

        # If no local data, use GitHub
        return github_df

    except Exception as e:
        st.warning(f"⚠️ Could not load data from GitHub: {e}. Using local data if available.")

        # Fallback to local data
        local_parquet = Path("data/merged_data.parquet")
        local_csv = Path("data/merged_data.csv")

        # Try Parquet first
        if local_parquet.exists():
            try:
                df = pd.read_parquet(local_parquet)
                st.info(f"✅ Loaded fresh data from Parquet: {len(df):,} records up to {df['date'].max().strftime('%Y-%m-%d')}")
                return df
            except Exception as pq_error:
                st.warning(f"⚠️ Could not read Parquet file: {pq_error}")

        # Fallback to CSV
        if local_csv.exists():
            try:
                df = pd.read_csv(local_csv, parse_dates=["date"])
                st.info(f"📄 Loaded data from CSV: {len(df):,} records up to {df['date'].max().strftime('%Y-%m-%d')}")
                return df
            except Exception as csv_error:
                st.error(f"❌ Could not read CSV file: {csv_error}")
                return pd.DataFrame()
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
