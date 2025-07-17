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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trends", 
    "🚨 Data Quality", 
    "📄 Raw Data", 
    "📊 Historical Trends",
    "🔮 Forecast"
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

# --- Tab 5: Forecasting
with tab5:
    st.header("🔮 Forecasting Energy Usage")

    # Select city and forecast window
    city = st.selectbox("Select City", df["city"].unique(), key="forecast_city")
    days = st.slider("Days to Forecast", 7, 30, 14)

    # Filter + prepare data
    city_df = df[df["city"] == city].copy()
    city_df["date"] = pd.to_datetime(city_df["date"])
    city_df = city_df.sort_values("date")
    city_df = city_df[["date", "energy_consumption"]].dropna()

    # Create numeric date for regression
    city_df["days_since"] = (city_df["date"] - city_df["date"].min()).dt.days

    # Fit linear regression
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(city_df[["days_since"]], city_df["energy_consumption"])

    # Forecast future
    future_days = pd.DataFrame({
        "days_since": range(city_df["days_since"].max() + 1, city_df["days_since"].max() + days + 1)
    })
    future_days["date"] = city_df["date"].max() + pd.to_timedelta(
        future_days["days_since"] - city_df["days_since"].max(), unit='d'
    )
    future_days["forecast"] = model.predict(future_days[["days_since"]])

    # Plot
    st.subheader(f"{city} Forecast for Next {days} Days")
    fig = px.line()
    fig.add_scatter(x=city_df["date"], y=city_df["energy_consumption"], name="Historical")
    fig.add_scatter(x=future_days["date"], y=future_days["forecast"], name="Forecast")
    st.plotly_chart(fig, use_container_width=True)
