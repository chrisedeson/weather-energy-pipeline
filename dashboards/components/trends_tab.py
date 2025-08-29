"""
Trends & Analysis Tab Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.data_loader import get_filtered_data

def render_trends_tab(df, selected_cities):
    """Render the Trends & Analysis tab"""
    st.header("📊 Trends & Analysis")

    filtered = get_filtered_data(df, selected_cities)

    if filtered.empty:
        st.warning("No data available for selected cities.")
        return

    # Section 1: Basic Trends
    st.subheader("📈 Basic Trends Overview")

    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(
            data=filtered.groupby("date")[["avg_temp_f", "energy_consumption"]].mean(),
            use_container_width=True
        )

    with col2:
        st.bar_chart(
            data=filtered.groupby("city")["energy_consumption"].mean().sort_values(),
            use_container_width=True
        )

    # Section 2: Historical Trends
    st.subheader("📊 Detailed Historical Analysis")

    hist_col1, hist_col2 = st.columns([1, 2])
    with hist_col1:
        city = st.selectbox("Select City", df['city'].unique(), key="hist_city")
        days = st.selectbox("Select Time Range", [7, 30, 90], key="hist_days")

    with hist_col2:
        city_data = df[df["city"] == city].copy()
        city_data["date"] = pd.to_datetime(city_data["date"])
        latest_date = city_data["date"].max()
        start_date = latest_date - pd.Timedelta(days=days)
        city_data = city_data[city_data["date"] >= start_date]

        fig = px.line(city_data, x="date", y=["avg_temp_f", "energy_consumption"],
                      labels={"value": "Metric", "variable": "Type"},
                      title=f"{city} Trends - Last {days} Days")
        st.plotly_chart(fig, use_container_width=True)

    # Section 3: Correlation Analysis
    st.subheader("📈 Temperature vs Energy Correlation")

    corr_df = filtered.copy()

    # Create scatter plot with regression lines
    fig = px.scatter(
        corr_df,
        x="avg_temp_f",
        y="energy_consumption",
        color="city",
        title="Temperature vs Energy Consumption by City",
        labels={
            "avg_temp_f": "Average Temperature (°F)",
            "energy_consumption": "Energy Consumption (MWh)"
        }
    )

    # Add regression line manually using numpy
    for city_name in corr_df["city"].unique():
        city_data = corr_df[corr_df["city"] == city_name]
        if len(city_data) > 5:
            x = city_data["avg_temp_f"]
            y = city_data["energy_consumption"]
            coeffs = np.polyfit(x, y, 1)
            line_x = np.linspace(x.min(), x.max(), 100)
            line_y = coeffs[0] * line_x + coeffs[1]
            fig.add_trace(px.line(x=line_x, y=line_y).data[0])

    st.plotly_chart(fig, use_container_width=True)

    # Section 4: Pattern Analysis
    st.subheader("🔍 Consumption Patterns")

    # Temperature ranges and day of week analysis
    pattern_df = filtered.copy()
    pattern_df["date"] = pd.to_datetime(pattern_df["date"])
    pattern_df["day_of_week"] = pattern_df["date"].dt.day_name()

    # Create temperature ranges
    pattern_df["temp_range"] = pd.cut(
        pattern_df["avg_temp_f"],
        bins=[-50, 32, 50, 70, 90, 130],
        labels=["Freezing (<32°F)", "Cold (32-50°F)", "Cool (50-70°F)", "Warm (70-90°F)", "Hot (>90°F)"]
    )

    # Heatmap data
    heatmap_df = pattern_df.groupby(["temp_range", "day_of_week"])["energy_consumption"].mean().reset_index()

    pivot_data = heatmap_df.pivot_table(
        values="energy_consumption",
        index="temp_range",
        columns="day_of_week",
        aggfunc="mean"
    )

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_data = pivot_data.reindex(columns=day_order)

    fig = px.imshow(
        pivot_data,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale="YlOrRd",
        title="Energy Consumption Patterns by Temperature & Day",
        labels=dict(x="Day of Week", y="Temperature Range", color="Energy (MWh)")
    )

    fig.update_xaxes(side="bottom")
    st.plotly_chart(fig, use_container_width=True)

    # Download button
    st.download_button(
        "⬇️ Download Filtered CSV",
        data=filtered.to_csv(index=False).encode(),
        file_name="filtered_data.csv",
        mime="text/csv"
    )
