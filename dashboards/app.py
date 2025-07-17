import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="US Weather + Energy Dashboard", layout="wide")

DATA_PATH = Path("data/merged_data.csv")
REPORT_PATH = Path("data/quality_report.json")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df

@st.cache_data
def load_quality_report():
    if REPORT_PATH.exists():
        with open(REPORT_PATH) as f:
            return json.load(f)
    return {}

# Load
st.title("🔌 US Weather + Energy Dashboard")
df = load_data()
report = load_quality_report()

# Sidebar
st.sidebar.header("Filter")
cities = df["city"].unique().tolist()
selected_cities = st.sidebar.multiselect("Cities", cities, default=cities)

filtered = df[df["city"].isin(selected_cities)]

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Trends", "🚨 Data Quality", "📄 Raw Data"])

# --- Tab 1: Trends
with tab1:
    st.subheader("Energy vs. Temperature")

    st.line_chart(
        data=filtered.groupby("date")[["avg_temp_f", "energy_consumption"]].mean(),
        use_container_width=True
    )

    st.bar_chart(
        data=filtered.groupby("city")["energy_consumption"].mean().sort_values(),
        use_container_width=True
    )

# --- Tab 2: Data Quality
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

        st.json(report["missing_values"], expanded=False)
    else:
        st.warning("No quality report found.")

# --- Tab 3: Raw Data
with tab3:
    st.subheader("📄 Data Table")
    st.dataframe(filtered, use_container_width=True)
