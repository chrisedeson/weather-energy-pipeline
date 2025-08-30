"""
Trends & Analysis Tab Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.data_loader import get_filtered_data

def render_trends_tab(df, selected_cities):
    """Render the Trends & Analysis tab"""
    st.header("📊 Trends & Analysis")

    filtered = get_filtered_data(df, selected_cities)

    if filtered.empty:
        st.warning("No data available for selected cities.")
        return

    # Section 1: Basic Trends - Removed duplicate charts
    # Keeping the section header for navigation purposes but removing duplicate charts
    # st.subheader("📈 Basic Trends Overview")

    # Section 2: Historical Trends
    st.subheader("Detailed Historical Analysis")

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

        # Create dual y-axis chart for better visualization
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add temperature trace (primary y-axis)
        fig.add_trace(
            go.Scatter(
                x=city_data["date"],
                y=city_data["avg_temp_f"],
                name="Avg Temperature (°F)",
                line=dict(color="orange", width=2)
            ),
            secondary_y=False
        )

        # Add energy consumption trace (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=city_data["date"],
                y=city_data["energy_consumption"],
                name="Energy Consumption (MWh)",
                line=dict(color="blue", width=2)
            ),
            secondary_y=True
        )

        # Update layout with proper titles and axis labels
        fig.update_layout(
            title_text=f"{city} – Avg Temperature (°F) vs. Energy Consumption (MWh), Last {days} Days",
            title_x=0.5,
            height=500,  # Give the chart more vertical space
            margin=dict(l=50, r=50, t=80, b=120),  # Add margins for better spacing
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",
                y=-0.25,  # Position below the chart
                xanchor="center",
                x=0.5  # Center the legend
            )
        )

        # Update y-axes titles
        fig.update_yaxes(title_text="Temperature (°F)", secondary_y=False)
        fig.update_yaxes(title_text="Energy Consumption (MWh)", secondary_y=True)

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
