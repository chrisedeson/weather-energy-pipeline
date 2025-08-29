"""
Geographic Tab Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import get_filtered_data

# City coordinates for mapping
CITY_COORDS = {
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Seattle": {"lat": 47.6062, "lon": -122.3321}
}

def render_geographic_tab(df, selected_cities):
    """Render the Geographic tab"""
    st.header("🗺️ Geographic Analysis")

    filtered = get_filtered_data(df, selected_cities)

    if filtered.empty:
        st.warning("No data available for selected cities.")
        return

    # Add coordinates to dataframe
    filtered = filtered.copy()
    filtered["lat"] = filtered["city"].map(lambda x: CITY_COORDS.get(x, {}).get("lat"))
    filtered["lon"] = filtered["city"].map(lambda x: CITY_COORDS.get(x, {}).get("lon"))

    # Current metrics
    st.subheader("📍 Current City Metrics")

    # Get latest data for each city - ensure no negative values are included
    filtered_positive = filtered[filtered['energy_consumption'] >= 0].copy()
    latest_data = filtered_positive.sort_values("date").groupby("city").last().reset_index()
    
    # Safety check - if we somehow still have negative values, replace with absolute value
    latest_data['energy_consumption'] = latest_data['energy_consumption'].abs()

    # Create metrics cards
    cols = st.columns(len(latest_data))
    for i, (_, row) in enumerate(latest_data.iterrows()):
        with cols[i]:
            st.metric(
                f"{row['city']}",
                f"{row['avg_temp_f']:.1f}°F",
                f"{row['energy_consumption']:.0f} MWh"
            )

    # Map visualization
    st.subheader("🗺️ Interactive Map")

    # Prepare data for map
    map_data = latest_data.copy()
    # Ensure size values are non-negative and scaled appropriately
    map_data["size"] = (map_data["energy_consumption"].abs() / 100).clip(lower=0.1)

    fig = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon="lon",
        size="size",
        color="avg_temp_f",
        hover_name="city",
        hover_data={
            "avg_temp_f": ":.1f",
            "energy_consumption": ":,.0f",
            "lat": False,
            "lon": False,
            "size": False
        },
        color_continuous_scale="RdYlBu_r",
        size_max=30,
        zoom=3,
        center={"lat": 39.8283, "lon": -98.5795},  # Center of US
        title="US Cities: Temperature & Energy Consumption"
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":30,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

    # Regional comparison
    st.subheader("📊 Regional Comparison")

    # Temperature comparison
    fig_temp = px.bar(
        latest_data,
        x="city",
        y="avg_temp_f",
        title="Current Temperatures by City",
        labels={"avg_temp_f": "Temperature (°F)", "city": "City"},
        color="avg_temp_f",
        color_continuous_scale="RdYlBu_r"
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    # Energy consumption comparison
    fig_energy = px.bar(
        latest_data.sort_values('energy_consumption', ascending=False),
        x="city",
        y="energy_consumption",
        title="Current Energy Consumption by City (Demand Data)",
        labels={"energy_consumption": "Energy Consumption (MWh)", "city": "City"},
        color="energy_consumption",
        color_continuous_scale="Blues",
        text="energy_consumption"  # Add values as text labels
    )
    
    # Customize layout for better readability
    fig_energy.update_traces(
        texttemplate='%{text:,.0f} MWh',
        textposition='outside',
        marker_line_width=1,
        marker_line_color='rgba(255, 255, 255, 0.3)'
    )
    
    # Update layout
    fig_energy.update_layout(
        yaxis_title="Energy Consumption (MWh)",
        xaxis_title="City",
        xaxis={'categoryorder': 'total descending'},  # Sort by value
        hovermode='x unified',
        hoverlabel=dict(bgcolor="white", font_size=14),
        plot_bgcolor='rgba(0,0,0,0.1)',
        bargap=0.2
    )
    
    st.plotly_chart(fig_energy, use_container_width=True)

    # Summary statistics
    st.subheader("📈 Summary Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        hottest_city = latest_data.loc[latest_data["avg_temp_f"].idxmax(), "city"]
        st.metric("Hottest City", hottest_city, f"{latest_data['avg_temp_f'].max():.1f}°F")

    with col2:
        highest_consumption = latest_data.loc[latest_data["energy_consumption"].idxmax(), "city"]
        st.metric("Highest Consumption", highest_consumption, f"{latest_data['energy_consumption'].max():.0f} MWh")

    with col3:
        total_energy = latest_data["energy_consumption"].sum()
        st.metric("Total Daily Energy", f"{total_energy:,.0f} MWh")

    st.info(f"Overall, the monitored cities consume {total_energy:,.0f} MWh of energy daily, with {hottest_city} being the warmest at {latest_data['avg_temp_f'].max():.1f}°F.")
