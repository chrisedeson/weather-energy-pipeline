import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="US Weather + Energy Dashboard", layout="wide")

# ---- Paths
DATA_PATH = Path("data/merged_data.csv")
REPORT_PATH = Path("data/quality_report.json")

# ---- Loaders
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

@st.cache_data
def load_quality_report():
    if REPORT_PATH.exists():
        with open(REPORT_PATH) as f:
            return json.load(f)
    return {}

# ---- Load
st.title("🔌 US Weather + Energy Dashboard")
df = load_data()
report = load_quality_report()

# ---- Sidebar Filter
st.sidebar.header("Filter")
cities = df["city"].unique().tolist()
selected_cities = st.sidebar.multiselect("Cities", cities, default=cities)
filtered = df[df["city"].isin(selected_cities)]

# ---- Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Trends", "📊 Historical Trends", "🔮 Forecast", "🚨 Data Quality", "🔍 Anomalies", "📄 Raw Data"
])

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

    st.download_button(
        "⬇️ Download Filtered CSV", 
        data=filtered.to_csv(index=False).encode(),
        file_name="filtered_data.csv",
        mime="text/csv"
    )

# --- Tab 2: Historical Trends
with tab2:
    st.header("📊 Historical Trends")

    city = st.selectbox("Select City", df['city'].unique(), key="hist_city")
    days = st.selectbox("Select Time Range", [7, 30, 90], key="hist_days")

    city_data = df[df["city"] == city].copy()
    city_data["date"] = pd.to_datetime(city_data["date"])
    latest_date = city_data["date"].max()
    start_date = latest_date - pd.Timedelta(days=days)
    city_data = city_data[city_data["date"] >= start_date]

    st.subheader(f"Avg Temp & Energy Usage - Last {days} Days in {city}")
    fig = px.line(city_data, x="date", y=["avg_temp_f", "energy_consumption"],
                  labels={"value": "Metric", "variable": "Type"},
                  title=f"{city} Trends")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: Forecast
with tab3:
    st.header("🔮 Forecasting Energy Usage")

    city = st.selectbox("Select City", df["city"].unique(), key="forecast_city")
    days = st.slider("Days to Forecast", 7, 30, 14)

    city_df = df[df["city"] == city].copy()
    city_df["date"] = pd.to_datetime(city_df["date"])
    city_df = city_df.sort_values("date")
    city_df = city_df[["date", "energy_consumption"]].dropna()

    city_df["days_since"] = (city_df["date"] - city_df["date"].min()).dt.days
    model = LinearRegression()
    model.fit(city_df[["days_since"]], city_df["energy_consumption"])

    future_days = pd.DataFrame({
        "days_since": range(
            city_df["days_since"].max() + 1,
            city_df["days_since"].max() + days + 1
        )
    })
    future_days["date"] = city_df["date"].max() + pd.to_timedelta(
        future_days["days_since"] - city_df["days_since"].max(), unit='d'
    )
    future_days["forecast"] = model.predict(future_days[["days_since"]])

    st.subheader(f"{city} Forecast for Next {days} Days")
    fig = px.line()
    fig.add_scatter(x=city_df["date"], y=city_df["energy_consumption"], name="Historical")
    fig.add_scatter(x=future_days["date"], y=future_days["forecast"], name="Forecast")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 4: Data Quality
with tab4:
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

# --- Tab 5: Anomalies
with tab5:
    st.header("🔍 Anomaly Detection")

    df_anomalies = df[
        (df["energy_consumption"] < 0) |
        (df["avg_temp_f"] < -50) | (df["avg_temp_f"] > 130)
    ]

    if df_anomalies.empty:
        st.success("✅ No anomalies detected in temperature or energy values.")
    else:
        st.error(f"⚠️ {len(df_anomalies)} anomaly rows detected.")
        st.dataframe(df_anomalies, use_container_width=True)
        st.download_button(
            "⬇️ Download Anomalies CSV", 
            data=df_anomalies.to_csv(index=False).encode(),
            file_name="anomalies.csv",
            mime="text/csv"
        )

# --- Tab 6: Raw Data
with tab6:
    st.subheader("📄 Full Data Table")
    st.dataframe(filtered, use_container_width=True)
