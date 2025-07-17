import streamlit as st
import pandas as pd
import json
import plotly.express as px
from pathlib import Path

# Page setup
st.set_page_config(page_title="US Weather + Energy Dashboard", layout="wide")

# Paths
DATA_PATH = Path("data/merged_data.csv")
REPORT_PATH = Path("data/quality_report.json")

# --- Caching: Load data
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

@st.cache_data
def load_quality_report():
    if REPORT_PATH.exists():
        with open(REPORT_PATH) as f:
            return json.load(f)
    return {}

# --- Load Data
df = load_data()
report = load_quality_report()

# --- Sidebar filters
st.sidebar.header("🔎 Filter Data")
cities = df["city"].unique().tolist()
selected_cities = st.sidebar.multiselect("Select Cities", cities, default=cities)

# Filter based on sidebar
filtered = df[df["city"].isin(selected_cities)]

# --- Page Title
st.title("🔌 US Weather + Energy Dashboard")

# --- Define Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Trends", 
    "🚨 Data Quality", 
    "📄 Raw Data", 
    "📊 Historical Trends"
])

# --- Tab 1: Trends Overview
with tab1:
    st.subheader("Energy vs. Temperature (Averaged by Day)")

    st.line_chart(
        data=filtered.groupby("date")[["avg_temp_f", "energy_consumption"]].mean(),
        use_container_width=True
    )

    st.subheader("Average Energy Usage per City")
    st.bar_chart(
        data=filtered.groupby("city")["energy_consumption"].mean().sort_values(),
        use_container_width=True
    )

# --- Tab 2: Data Quality Report
with tab2:
    st.subheader("📋 Data Quality Report")

    if report:
        col1, col2 = st.columns(2)

        with col1:
            st.metric("📆 Latest Date", report["freshness"]["latest_date"])
            st.metric("📦 Is Fresh?", str(report["freshness"]["is_fresh"]))
            st.metric("📉 Days Old", report["freshness"]["days_old"])

        with col2:
            st.metric("❌ Temp Outliers", report["outliers"]["temperature_outliers"])
            st.metric("❌ Negative Energy", report["outliers"]["negative_energy_readings"])

        st.markdown("#### Missing Values")
        st.json(report["missing_values"], expanded=False)

    else:
        st.warning("No data quality report found.")

# --- Tab 3: Raw Data Table
with tab3:
    st.subheader("📄 Raw Merged Dataset")
    st.dataframe(filtered, use_container_width=True)

# --- Tab 4: Historical Trends (City Drilldown)
with tab4:
    st.header("📊 Historical Trends by City")

    city = st.selectbox("Choose a City", df["city"].unique())
    days = st.selectbox("Select Time Range", [7, 30, 90])

    city_data = df[df["city"] == city].copy()
    city_data["date"] = pd.to_datetime(city_data["date"])
    latest_date = city_data["date"].max()
    start_date = latest_date - pd.Timedelta(days=days)
    city_data = city_data[city_data["date"] >= start_date]

    st.subheader(f"{city}: Avg Temp & Energy over last {days} days")

    fig = px.line(
        city_data,
        x="date",
        y=["avg_temp_f", "energy_consumption"],
        labels={"value": "Metric", "variable": "Type"},
        title=f"{city} Trends (last {days} days)"
    )
    st.plotly_chart(fig, use_container_width=True)
