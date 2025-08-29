"""
Forecasting Tab Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
from utils.data_loader import get_filtered_data

def render_forecasting_tab(df, selected_cities):
    """Render the Forecasting tab"""
    st.header("🔮 Energy Forecasting")

    filtered = get_filtered_data(df, selected_cities)

    if filtered.empty:
        st.warning("No data available for selected cities.")
        return

    # Controls
    col1, col2 = st.columns([1, 1])
    with col1:
        city = st.selectbox("Select City", df["city"].unique(), key="forecast_city")
    with col2:
        days = st.slider("Days to Forecast", 7, 30, 14)

    # Get city data
    city_df = df[df["city"] == city].copy()
    city_df["date"] = pd.to_datetime(city_df["date"])
    city_df = city_df.sort_values("date")
    city_df = city_df[["date", "energy_consumption"]].dropna()

    if len(city_df) < 10:
        st.warning("⚠️ Not enough data for reliable forecasting. Need at least 10 data points.")
        return

    # Prepare data for modeling
    city_df["days_since_start"] = (city_df["date"] - city_df["date"].min()).dt.days

    # Train model
    X = city_df[["days_since_start"]]
    y = city_df["energy_consumption"]

    model = LinearRegression()
    model.fit(X, y)

    # Generate forecast
    last_date = city_df["date"].max()
    last_days = city_df["days_since_start"].max()

    forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                   periods=days, freq='D')
    forecast_days = np.arange(last_days + 1, last_days + days + 1)

    forecast_values = model.predict(forecast_days.reshape(-1, 1))

    # Create forecast dataframe
    forecast_df = pd.DataFrame({
        "date": forecast_dates,
        "energy_consumption": forecast_values,
        "type": "Forecast"
    })

    # Combine historical and forecast
    historical_df = city_df[["date", "energy_consumption"]].copy()
    historical_df["type"] = "Historical"

    combined_df = pd.concat([historical_df, forecast_df])

    # Plot
    fig = px.line(combined_df, x="date", y="energy_consumption", color="type",
                  title=f"{city} Energy Consumption Forecast",
                  labels={"energy_consumption": "Energy Consumption (MWh)", "date": "Date"})

    # Add confidence interval (simple approximation)
    std_dev = np.std(y)
    upper_bound = forecast_values + 1.96 * std_dev
    lower_bound = forecast_values - 1.96 * std_dev

    fig.add_trace(px.line(x=forecast_dates, y=upper_bound).data[0].update(line=dict(dash='dash', color='lightgray')))
    fig.add_trace(px.line(x=forecast_dates, y=lower_bound).data[0].update(line=dict(dash='dash', color='lightgray')))

    st.plotly_chart(fig, use_container_width=True)

    # Forecast metrics
    col1, col2, col3 = st.columns(3)

    avg_forecast = np.mean(forecast_values)
    trend = (forecast_values[-1] - forecast_values[0]) / days

    with col1:
        st.metric("Avg Daily Forecast", f"{avg_forecast:.1f} MWh")

    with col2:
        st.metric("Daily Trend", f"{trend:+.2f} MWh/day")

    with col3:
        st.metric("Forecast Period", f"{days} days")

    st.info(f"📈 **Forecast Summary for {city}:** Expected average daily consumption of {avg_forecast:.1f} MWh over the next {days} days with a {'positive' if trend > 0 else 'negative'} trend of {abs(trend):.2f} MWh per day.")

    # Forecast table
    st.subheader("📋 Forecast Details")
    forecast_table = forecast_df.copy()
    forecast_table["date"] = forecast_table["date"].dt.strftime("%Y-%m-%d")
    forecast_table["energy_consumption"] = forecast_table["energy_consumption"].round(1)
    st.dataframe(forecast_table, use_container_width=True)
