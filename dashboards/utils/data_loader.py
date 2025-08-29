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

@st.cache_data(ttl=5) # Short TTL to refresh data frequently
def load_data():
    """Load main dataset with fallback options"""
    try:
        # Priority: Use local Parquet file first (most up-to-date after running pipeline)
        local_parquet = Path("data/merged_data.parquet")
        if local_parquet.exists():
            try:
                local_df = pd.read_parquet(local_parquet)
                local_latest = local_df['date'].max()
                
                # Check for negative values (safety check)
                neg_count = len(local_df[local_df['energy_consumption'] < 0])
                if neg_count > 0:
                    st.warning(f"⚠️ Found {neg_count} negative energy values in local data. Using filtered data.")
                    local_df = local_df[local_df['energy_consumption'] >= 0]
                
                st.success(f"✅ Using local data: {len(local_df):,} records up to {local_latest.strftime('%Y-%m-%d')}")
                return local_df
            except Exception as pq_error:
                st.warning(f"⚠️ Could not read local Parquet: {pq_error}")
        
        # Fallback: Try to load from GitHub if local fails
        github_df = pd.read_parquet(DATA_URL)
        
        # Safety check for negative values in GitHub data too
        neg_count = len(github_df[github_df['energy_consumption'] < 0])
        if neg_count > 0:
            st.warning(f"⚠️ Found {neg_count} negative energy values in GitHub data. Using filtered data.")
            github_df = github_df[github_df['energy_consumption'] >= 0]
        
        github_latest = github_df['date'].max()
        st.info(f"📡 Using GitHub data: {len(github_df):,} records up to {github_latest.strftime('%Y-%m-%d')}")
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
