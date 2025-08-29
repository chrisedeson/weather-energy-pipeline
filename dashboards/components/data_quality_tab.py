"""
Data Quality Tab Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import get_filtered_data, load_anomalies, load_quality_report

def render_data_quality_tab(df, selected_cities, report):
    """Render the Data Quality tab"""
    st.header("🚨 Data Quality & Anomalies")

    filtered = get_filtered_data(df, selected_cities)

    if filtered.empty:
        st.warning("No data available for selected cities.")
        return

    # Quality Report Section
    st.subheader("📊 Data Quality Report")

    if report:
        col1, col2, col3 = st.columns(3)

        # Missing values
        missing_count = sum(report.get("missing_values", {}).values())
        with col1:
            st.metric("Missing Values", missing_count)

        # Outliers
        outliers = report.get("outliers", {})
        total_outliers = outliers.get("temperature_outliers", 0) + outliers.get("negative_energy_readings", 0)
        with col2:
            st.metric("Outliers Detected", total_outliers)

        # Freshness
        freshness = report.get("freshness", {})
        is_fresh = freshness.get("is_fresh", False)
        with col3:
            status = "🟢 Fresh" if is_fresh else "🔴 Stale"
            st.metric("Data Freshness", status)

        # Detailed quality metrics
        with st.expander("📋 Detailed Quality Metrics"):
            st.json(report)
    else:
        st.warning("No quality report available. Run the data quality pipeline.")

    # Anomalies Section
    st.subheader("🔍 Anomaly Detection")

    anomalies_df = load_anomalies()

    if not anomalies_df.empty:
        # Filter anomalies for selected cities
        city_anomalies = anomalies_df[anomalies_df["city"].isin(selected_cities)] if selected_cities else anomalies_df

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Anomalies", len(city_anomalies))

        with col2:
            if len(city_anomalies) > 0:
                latest_anomaly = city_anomalies["date"].max().strftime("%Y-%m-%d")
                st.metric("Latest Anomaly", latest_anomaly)

        # Anomalies by city
        if not city_anomalies.empty:
            st.subheader("📈 Anomalies by City")

            anomaly_counts = city_anomalies.groupby("city").size().reset_index(name="count")

            fig = px.bar(
                anomaly_counts,
                x="city",
                y="count",
                title="Anomaly Distribution by City",
                labels={"count": "Number of Anomalies", "city": "City"},
                color="count",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Anomalies over time
            st.subheader("📅 Anomalies Over Time")

            # Group by date and count anomalies
            time_anomalies = city_anomalies.groupby("date").size().reset_index(name="count")
            time_anomalies["date"] = pd.to_datetime(time_anomalies["date"])

            fig_time = px.line(
                time_anomalies,
                x="date",
                y="count",
                title="Anomaly Frequency Over Time",
                labels={"count": "Number of Anomalies", "date": "Date"},
                markers=True  # Add markers to show individual data points
            )
            
            # Improve the visualization
            fig_time.update_traces(
                line=dict(width=3),
                marker=dict(size=8, symbol="circle")
            )
            
            # Add reference line for average
            avg_anomalies = time_anomalies["count"].mean()
            fig_time.add_hline(
                y=avg_anomalies, 
                line_dash="dash", 
                line_color="rgba(255, 0, 0, 0.5)",
                annotation_text=f"Avg: {avg_anomalies:.1f}"
            )
            
            # Update layout for better readability
            fig_time.update_layout(
                yaxis=dict(
                    title="Number of Anomalies",
                    range=[0, max(time_anomalies["count"]) * 1.2],  # Add some space at top
                    dtick=1  # Force integer ticks
                ),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_time, use_container_width=True)

            # Anomaly details table
            st.subheader("📋 Anomaly Details")

            # Show recent anomalies
            recent_anomalies = city_anomalies.sort_values("date", ascending=False).head(20)
            st.dataframe(
                recent_anomalies[["date", "city", "avg_temp_f", "energy_consumption"]],
                use_container_width=True
            )

            # Download anomalies
            st.download_button(
                "⬇️ Download Anomalies CSV",
                data=city_anomalies.to_csv(index=False).encode(),
                file_name="anomalies.csv",
                mime="text/csv"
            )
    else:
        st.info("No anomalies data available. Run the anomaly detection pipeline.")

    # Data completeness check
    st.subheader("✅ Data Completeness")

    completeness_df = filtered.copy()
    completeness_df["date"] = pd.to_datetime(completeness_df["date"])

    # Check for missing dates
    date_range = pd.date_range(
        start=completeness_df["date"].min(),
        end=completeness_df["date"].max(),
        freq='D'
    )

    missing_dates = []
    for city in selected_cities:
        city_dates = completeness_df[completeness_df["city"] == city]["date"]
        expected_dates = date_range
        missing = expected_dates.difference(city_dates)
        if len(missing) > 0:
            missing_dates.extend([(city, date.strftime("%Y-%m-%d")) for date in missing])

    if missing_dates:
        st.warning(f"⚠️ Found {len(missing_dates)} missing date(s) in the dataset.")
        missing_df = pd.DataFrame(missing_dates, columns=["City", "Missing Date"])
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success("✅ No missing dates found in the selected data range.")
