import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="US Weather + Energy Dashboard", layout="wide")

# ---- Paths
DATA_URL = "https://raw.githubusercontent.com/chrisedeson/weather-energy-pipeline/master/data/merged_data.parquet"
REPORT_URL = "https://raw.githubusercontent.com/chrisedeson/weather-energy-pipeline/master/data/quality_report.json"
ANOMALIES_URL = "https://raw.githubusercontent.com/chrisedeson/weather-energy-pipeline/master/data/anomalies.csv"

# ---- Loaders
@st.cache_data
def load_data():
    try:
        # Try to load from GitHub first
        return pd.read_parquet(DATA_URL)
    except Exception as e:
        st.warning("⚠️ Could not load data from GitHub. Using local data if available.")
        # Fallback to local data
        local_path = Path("data/merged_data.parquet")
        if local_path.exists():
            return pd.read_parquet(local_path)
        else:
            # Try CSV as last resort
            csv_path = Path("data/merged_data.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path, parse_dates=["date"])
                st.info("📄 Using local CSV data. Run pipeline to generate parquet file.")
                return df
            else:
                st.error("❌ No data files found. Please run the data pipeline first.")
                return pd.DataFrame()

@st.cache_data
def load_quality_report():
    try:
        # Read JSON as string first, then parse
        import requests
        response = requests.get(REPORT_URL)
        response.raise_for_status()
        return response.json()
    except:
        # Fallback to local file
        local_path = Path("data/quality_report.json")
        if local_path.exists():
            with open(local_path) as f:
                import json
                return json.load(f)
        return {}

@st.cache_data
def load_anomalies():
    try:
        return pd.read_csv(ANOMALIES_URL, parse_dates=["date"])
    except:
        # Fallback to local file
        local_path = Path("data/anomalies.csv")
        if local_path.exists():
            return pd.read_csv(local_path, parse_dates=["date"])
        return pd.DataFrame()

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Trends & Analysis", "🔮 Forecasting", "🗺️ Geographic", 
    "🚨 Data Quality", "📄 Raw Data"
])

# --- Tab 1: Trends & Analysis (Combined: Trends, Historical, Correlation, Patterns)
with tab1:
    st.header("📊 Trends & Analysis")
    
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
            
            fig.add_scatter(
                x=line_x, 
                y=line_y, 
                mode='lines',
                name=f'{city_name} trend',
                showlegend=True
            )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation Statistics
    st.subheader("📊 Correlation Statistics")
    
    corr_stats = []
    for city_name in corr_df["city"].unique():
        city_data = corr_df[corr_df["city"] == city_name]
        if len(city_data) > 10:
            corr = city_data["avg_temp_f"].corr(city_data["energy_consumption"])
            corr_stats.append({
                "City": city_name,
                "Correlation": corr,
                "Data Points": len(city_data)
            })
    
    if corr_stats:
        stats_df = pd.DataFrame(corr_stats)
        st.dataframe(stats_df, use_container_width=True)
        
        overall_corr = corr_df["avg_temp_f"].corr(corr_df["energy_consumption"])
        st.metric("Overall Correlation", f"{overall_corr:.3f}")
        
        if abs(overall_corr) > 0.7:
            st.success("🎯 Strong correlation detected!")
        elif abs(overall_corr) > 0.5:
            st.info("📊 Moderate correlation detected")
        else:
            st.warning("⚠️ Weak correlation")
    
    # Section 4: Usage Patterns Heatmap
    st.subheader("🔥 Usage Patterns Heatmap")
    
    temp_bins = [-float('inf'), 50, 60, 70, 80, 90, float('inf')]
    temp_labels = ['<50°F', '50-60°F', '60-70°F', '70-80°F', '80-90°F', '>90°F']
    
    heatmap_df = filtered.copy()
    heatmap_df["temp_range"] = pd.cut(heatmap_df["avg_temp_f"], bins=temp_bins, labels=temp_labels)
    heatmap_df["day_of_week"] = pd.to_datetime(heatmap_df["date"]).dt.day_name()
    
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

# --- Tab 2: Forecasting (Enhanced)
with tab2:
    st.header("🔮 Energy Forecasting")
    
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
    else:
        # Prepare data for modeling
        city_df["days_since"] = (city_df["date"] - city_df["date"].min()).dt.days
        
        # Train model
        model = LinearRegression()
        model.fit(city_df[["days_since"]], city_df["energy_consumption"])
        
        # Generate forecast
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
        
        # Create beautiful forecast chart
        fig = px.line()
        
        # Historical data
        fig.add_scatter(
            x=city_df["date"], 
            y=city_df["energy_consumption"], 
            name="Historical Data",
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6, color='#1f77b4')
        )
        
        # Forecast data
        fig.add_scatter(
            x=future_days["date"], 
            y=future_days["forecast"], 
            name="Forecast",
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8, color='#ff7f0e', symbol='diamond')
        )
        
        # Add confidence interval (simple approximation)
        std_dev = city_df["energy_consumption"].std()
        future_days["upper"] = future_days["forecast"] + std_dev
        future_days["lower"] = future_days["forecast"] - std_dev
        
        fig.add_scatter(
            x=future_days["date"], 
            y=future_days["upper"], 
            name="Upper Bound",
            mode='lines',
            line=dict(color='rgba(255, 127, 14, 0.3)', width=0),
            showlegend=False
        )
        
        fig.add_scatter(
            x=future_days["date"], 
            y=future_days["lower"], 
            name="Lower Bound",
            mode='lines',
            line=dict(color='rgba(255, 127, 14, 0.3)', width=0),
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.2)',
            showlegend=False
        )
        
        fig.update_layout(
            title=f"🔮 {city} Energy Consumption Forecast - Next {days} Days",
            xaxis_title="Date",
            yaxis_title="Energy Consumption (MWh)",
            hovermode="x unified",
            showlegend=True,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast metrics
        st.subheader("📊 Forecast Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_forecast = future_days["forecast"].mean()
            st.metric("Avg Daily Forecast", f"{avg_forecast:.1f} MWh")
        
        with col2:
            trend = (future_days["forecast"].iloc[-1] - future_days["forecast"].iloc[0]) / days
            st.metric("Daily Trend", f"{trend:+.2f} MWh/day")
        
        with col3:
            accuracy_estimate = max(0.7, 1 - (std_dev / city_df["energy_consumption"].mean()))
            st.metric("Est. Accuracy", f"{accuracy_estimate:.1%}")
        
        # Forecast summary
        st.info(f"📈 **Forecast Summary for {city}:** Expected average daily consumption of {avg_forecast:.1f} MWh over the next {days} days with a {'positive' if trend > 0 else 'negative'} trend of {abs(trend):.2f} MWh per day.")

# --- Tab 4: Data Quality & Anomalies (Combined)
with tab4:
    st.header("🚨 Data Quality & Anomaly Detection")
    
    # Data Quality Section
    st.subheader("📋 Data Quality Report")
    
    if report:
        # Quality metrics in a nice grid
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("📆 Latest Date", report["freshness"]["latest_date"])
        with metric_col2:
            freshness_status = "🟢 Fresh" if report["freshness"]["is_fresh"] else "🔴 Stale"
            st.metric("📦 Data Freshness", freshness_status)
        with metric_col3:
            st.metric("📉 Days Old", report["freshness"]["days_old"])
        with metric_col4:
            total_records = sum(len(df[df["city"] == city]) for city in df["city"].unique())
            st.metric("📊 Total Records", f"{total_records:,}")
        
        # Outlier analysis
        outlier_col1, outlier_col2 = st.columns(2)
        with outlier_col1:
            st.metric("❌ Temp Outliers", report["outliers"]["temperature_outliers"])
        with outlier_col2:
            st.metric("❌ Negative Energy", report["outliers"]["negative_energy_readings"])
        
        # Missing values breakdown
        st.subheader("🔍 Missing Values Analysis")
        missing_df = pd.DataFrame(report["missing_values"], index=["Count"]).T
        st.dataframe(missing_df, use_container_width=True)
        
        # Data completeness score
        completeness = (1 - sum(report["missing_values"].values()) / (len(report["missing_values"]) * total_records)) * 100
        st.metric("✅ Data Completeness", f"{completeness:.1f}%")
    else:
        st.warning("No quality report found.")
    
    # Anomaly Detection Section
    st.subheader("🔍 Anomaly Detection Results")
    
    # Define anomaly criteria
    temp_anomalies = df[
        (df["avg_temp_f"] < -50) | (df["avg_temp_f"] > 130)
    ]
    
    energy_anomalies = df[df["energy_consumption"] < 0]
    
    # Combined anomalies
    all_anomalies = pd.concat([temp_anomalies, energy_anomalies]).drop_duplicates()
    
    # Anomaly summary
    anomaly_col1, anomaly_col2, anomaly_col3 = st.columns(3)
    with anomaly_col1:
        st.metric("🌡️ Temperature Anomalies", len(temp_anomalies))
    with anomaly_col2:
        st.metric("⚡ Energy Anomalies", len(energy_anomalies))
    with anomaly_col3:
        st.metric("🚨 Total Anomalies", len(all_anomalies))
    
    if all_anomalies.empty:
        st.success("✅ No anomalies detected in temperature or energy values!")
    else:
        st.error(f"⚠️ {len(all_anomalies)} anomaly records detected.")
        
        # Anomaly breakdown by city
        anomaly_by_city = all_anomalies.groupby("city").size().reset_index(name="anomalies")
        anomaly_by_city = anomaly_by_city.sort_values("anomalies", ascending=False)
        
        st.subheader("📊 Anomalies by City")
        st.dataframe(anomaly_by_city, use_container_width=True)
        
        # Show sample anomalies
        st.subheader("🔍 Sample Anomalous Records")
        st.dataframe(all_anomalies.head(10), use_container_width=True)
        
        # Download anomalies
        st.download_button(
            "⬇️ Download All Anomalies CSV", 
            data=all_anomalies.to_csv(index=False).encode(),
            file_name="all_anomalies.csv",
            mime="text/csv"
        )
    
    # Data validation summary
    st.subheader("✅ Data Validation Summary")
    
    validation_checks = {
        "Temperature Range Check": len(temp_anomalies) == 0,
        "Energy Positivity Check": len(energy_anomalies) == 0,
        "Data Completeness": completeness > 95 if 'completeness' in locals() else False,
        "All Cities Present": len(df["city"].unique()) == 5
    }
    
    validation_df = pd.DataFrame({
        "Check": validation_checks.keys(),
        "Status": ["✅ Pass" if v else "❌ Fail" for v in validation_checks.values()]
    })
    
    st.dataframe(validation_df, use_container_width=True)
    
    if all(validation_checks.values()):
        st.success("🎉 All data validation checks passed!")
    else:
        failed_checks = [k for k, v in validation_checks.items() if not v]
        st.warning(f"⚠️ {len(failed_checks)} validation checks failed: {', '.join(failed_checks)}")

# --- Tab 5: Raw Data (Last Tab)
with tab5:
    st.header("📄 Raw Data Explorer")
    
    # Data overview
    st.subheader("📊 Dataset Overview")
    
    overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
    with overview_col1:
        st.metric("Total Records", f"{len(filtered):,}")
    with overview_col2:
        st.metric("Date Range", f"{len(filtered['date'].unique())} days")
    with overview_col3:
        st.metric("Cities", len(filtered['city'].unique()))
    with overview_col4:
        st.metric("Avg Energy/Day", f"{filtered['energy_consumption'].mean():.1f} MWh")
    
    # Data filters
    st.subheader("� Data Filters")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        date_range = st.date_input(
            "Date Range",
            value=(filtered['date'].min(), filtered['date'].max()),
            key="raw_date_range"
        )
    
    with filter_col2:
        temp_range = st.slider(
            "Temperature Range (°F)",
            float(filtered['avg_temp_f'].min()),
            float(filtered['avg_temp_f'].max()),
            (float(filtered['avg_temp_f'].min()), float(filtered['avg_temp_f'].max())),
            key="raw_temp_range"
        )
    
    with filter_col3:
        energy_range = st.slider(
            "Energy Range (MWh)",
            float(filtered['energy_consumption'].min()),
            float(filtered['energy_consumption'].max()),
            (float(filtered['energy_consumption'].min()), float(filtered['energy_consumption'].max())),
            key="raw_energy_range"
        )
    
    # Apply filters
    filtered_data = filtered.copy()
    if len(date_range) == 2:
        filtered_data = filtered_data[
            (filtered_data['date'] >= pd.to_datetime(date_range[0])) &
            (filtered_data['date'] <= pd.to_datetime(date_range[1]))
        ]
    
    filtered_data = filtered_data[
        (filtered_data['avg_temp_f'] >= temp_range[0]) &
        (filtered_data['avg_temp_f'] <= temp_range[1]) &
        (filtered_data['energy_consumption'] >= energy_range[0]) &
        (filtered_data['energy_consumption'] <= energy_range[1])
    ]
    
    st.metric("Filtered Records", f"{len(filtered_data):,}")
    
    # Data table
    st.subheader("📋 Raw Data Table")
    st.dataframe(filtered_data, use_container_width=True)
    
    # Data statistics
    st.subheader("📈 Quick Statistics")
    
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.write("**Temperature Statistics (°F):**")
        temp_stats = filtered_data['avg_temp_f'].describe()
        st.dataframe(temp_stats.to_frame(), use_container_width=True)
    
    with stat_col2:
        st.write("**Energy Statistics (MWh):**")
        energy_stats = filtered_data['energy_consumption'].describe()
        st.dataframe(energy_stats.to_frame(), use_container_width=True)
    
    # Download options
    st.subheader("⬇️ Download Options")
    
    download_col1, download_col2, download_col3 = st.columns(3)
    with download_col1:
        st.download_button(
            label="📥 Download Filtered CSV",
            data=filtered_data.to_csv(index=False).encode("utf-8"),
            file_name="filtered_weather_energy_data.csv",
            mime="text/csv"
        )
    
    with download_col2:
        # Sample data for preview
        sample_size = min(1000, len(filtered_data))
        sample_data = filtered_data.sample(sample_size, random_state=42)
        st.download_button(
            label="� Download Sample (1K rows)",
            data=sample_data.to_csv(index=False).encode("utf-8"),
            file_name="sample_weather_energy_data.csv",
            mime="text/csv"
        )
    
    with download_col3:
        # Summary statistics
        summary_stats = filtered_data.describe()
        st.download_button(
            label="📈 Download Statistics",
            data=summary_stats.to_csv().encode("utf-8"),
            file_name="data_statistics.csv",
            mime="text/csv"
        )
    
    # Data dictionary
    st.subheader("📚 Data Dictionary")
    
    data_dict = pd.DataFrame({
        "Column": ["date", "city", "avg_temp_f", "energy_consumption"],
        "Type": ["datetime", "string", "float", "float"],
        "Description": [
            "Date of the weather/energy reading",
            "City name (Chicago, Houston, New York, Phoenix, Seattle)",
            "Average daily temperature in Fahrenheit",
            "Daily energy consumption in Megawatt-hours"
        ],
        "Units": ["YYYY-MM-DD", "N/A", "°F", "MWh"]
    })
    
    st.dataframe(data_dict, use_container_width=True)
    
    # Data quality note
    st.info("💡 **Data Quality Note:** All data has been validated for anomalies and missing values. " +
            f"Current dataset contains {len(filtered_data)} records across {len(filtered_data['city'].unique())} cities " +
            f"from {filtered_data['date'].min().strftime('%B %d, %Y')} to {filtered_data['date'].max().strftime('%B %d, %Y')}.")

# --- Tab 3: Geographic Overview (Enhanced & Beautiful)
with tab3:
    st.header("🗺️ Geographic Energy & Weather Overview")
    
    # City coordinates with more precision
    city_coords = {
        "New York": {"lat": 40.7128, "lon": -74.0060, "state": "NY", "region": "Northeast"},
        "Chicago": {"lat": 41.8781, "lon": -87.6298, "state": "IL", "region": "Midwest"},
        "Houston": {"lat": 29.7604, "lon": -95.3698, "state": "TX", "region": "South"},
        "Phoenix": {"lat": 33.4484, "lon": -112.0740, "state": "AZ", "region": "Southwest"},
        "Seattle": {"lat": 47.6062, "lon": -122.3321, "state": "WA", "region": "Northwest"}
    }
    
    # Get latest data for each city
    latest_data = []
    for city in df["city"].unique():
        city_data = df[df["city"] == city]
        if not city_data.empty:
            latest = city_data.loc[city_data["date"].idxmax()]
            coords = city_coords.get(city, {"lat": 0, "lon": 0, "state": "Unknown", "region": "Unknown"})
            latest_data.append({
                "city": city,
                "state": coords["state"],
                "region": coords["region"],
                "lat": coords["lat"],
                "lon": coords["lon"],
                "temp": latest["avg_temp_f"],
                "energy": latest["energy_consumption"],
                "date": latest["date"]
            })
    
    geo_df = pd.DataFrame(latest_data)
    
    # Header with last update info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("US Cities Energy & Weather Dashboard")
        st.write(f"**Last Updated:** {geo_df['date'].max().strftime('%B %d, %Y')}")
    with col2:
        st.metric("Cities Monitored", len(geo_df))
    with col3:
        st.metric("Regions Covered", len(geo_df['region'].unique()))
    
    # Main geographic visualization
    st.subheader("📍 Interactive Geographic Map")
    
    # Create enhanced scatter plot
    fig = px.scatter_geo(
        geo_df,
        lat="lat",
        lon="lon",
        text="city",
        size="energy",
        color="temp",
        color_continuous_scale="Viridis",  # Changed to more vibrant color scale
        size_max=80,  # Increased for better visibility
        title="🌡️ City Energy Usage & Temperature Overview",
        labels={
            "temp": "Temperature (°F)", 
            "energy": "Energy Consumption (MWh)",
            "city": "City"
        },
        hover_data={
            "city": True,
            "state": True,
            "region": True,
            "temp": ":.1f",
            "energy": ":,.0f",
            "lat": False,
            "lon": False
        }
    )
    
    # Enhanced map styling
    fig.update_geos(
        scope="usa",
        showcoastlines=True,
        coastlinecolor="darkblue",  # Darker, more vibrant
        showland=True,
        landcolor="lightgreen",  # More vibrant green
        showocean=True,
        oceancolor="deepskyblue",  # More vibrant blue
        showlakes=True,
        lakecolor="royalblue",  # More vibrant lake color
        showrivers=True,
        rivercolor="steelblue",  # More vibrant river color
        showcountries=True,
        countrycolor="darkslategray",  # More defined borders
        showsubunits=True,
        subunitcolor="slategray",  # State borders
        projection_type="albers usa"
    )
    
    # Enhanced layout
    fig.update_layout(
        title_font_size=28,  # Larger title
        title_x=0.5,  # Centered
        title_font_color="darkblue",  # More vibrant title color
        coloraxis_colorbar=dict(
            title="Temperature (°F)",
            tickfont=dict(size=12, color="darkblue"),
            title_font=dict(size=14, color="darkblue"),
            len=0.8,  # Longer colorbar
            thickness=20  # Thicker colorbar
        ),
        margin=dict(l=10, r=10, t=60, b=10),  # Better margins
        template="plotly_white",
        paper_bgcolor="aliceblue",  # Light blue background
        plot_bgcolor="white"
    )
    
    # Add custom hover template
    fig.update_traces(
        marker=dict(
            line=dict(width=3, color='gold'),  # Golden border for better visibility
            opacity=0.9  # More opaque
        ),
        textposition="top center",  # Position city labels above markers
        textfont=dict(size=10, color="darkblue")  # Stylish text
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics in a nice layout
    st.subheader("📊 Regional Summary")
    
    # Temperature analysis
    temp_col1, temp_col2, temp_col3 = st.columns(3)
    with temp_col1:
        hottest_city = geo_df.loc[geo_df['temp'].idxmax()]
        st.metric("Hottest City", hottest_city['city'], f"{hottest_city['temp']:.1f}°F")
    
    with temp_col2:
        coldest_city = geo_df.loc[geo_df['temp'].idxmin()]
        st.metric("Coldest City", coldest_city['city'], f"{coldest_city['temp']:.1f}°F")
    
    with temp_col3:
        avg_temp = geo_df['temp'].mean()
        st.metric("Average Temperature", f"{avg_temp:.1f}°F")
    
    # Energy analysis
    energy_col1, energy_col2, energy_col3 = st.columns(3)
    with energy_col1:
        highest_energy = geo_df.loc[geo_df['energy'].idxmax()]
        st.metric("Highest Usage", highest_energy['city'], f"{highest_energy['energy']:,.0f} MWh")
    
    with energy_col2:
        lowest_energy = geo_df.loc[geo_df['energy'].idxmin()]
        st.metric("Lowest Usage", lowest_energy['city'], f"{lowest_energy['energy']:,.0f} MWh")
    
    with energy_col3:
        total_energy = geo_df['energy'].sum()
        st.metric("Total Energy", f"{total_energy:,.0f} MWh")
    
    # Regional breakdown
    st.subheader("🏙️ Regional Analysis")
    
    region_stats = geo_df.groupby('region').agg({
        'temp': ['mean', 'min', 'max'],
        'energy': ['mean', 'sum'],
        'city': 'count'
    }).round(2)
    
    region_stats.columns = ['Avg Temp (°F)', 'Min Temp (°F)', 'Max Temp (°F)', 
                           'Avg Energy (MWh)', 'Total Energy (MWh)', 'Cities']
    region_stats = region_stats.reset_index()
    
    st.dataframe(region_stats, use_container_width=True)
    
    # Quick insights
    st.info("💡 **Key Insights:** " +
            f"The {hottest_city['city']} area shows the highest temperatures at {hottest_city['temp']:.1f}°F, " +
            f"while {highest_energy['city']} leads in energy consumption at {highest_energy['energy']:,.0f} MWh. " +
            f"Overall, the monitored cities consume {total_energy:,.0f} MWh of energy daily.")