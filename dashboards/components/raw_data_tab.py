"""
Raw Data Tab Component
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import get_filtered_data

def render_raw_data_tab(df, selected_cities):
    """Render the Raw Data tab"""
    st.header("📄 Raw Data Explorer")

    filtered = get_filtered_data(df, selected_cities)

    if filtered.empty:
        st.warning("No data available for selected cities.")
        return

    # Data overview
    st.subheader("📊 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", len(filtered))

    with col2:
        st.metric("Cities", len(filtered["city"].unique()))

    with col3:
        date_range = f"{filtered['date'].min()} to {filtered['date'].max()}"
        st.metric("Date Range", date_range)

    with col4:
        st.metric("Columns", len(filtered.columns))

    # Data preview
    st.subheader("👀 Data Preview")

    # Show first N rows
    preview_rows = st.slider("Number of rows to preview", 5, 100, 20)
    st.dataframe(filtered.head(preview_rows), use_container_width=True)

    # Column information
    st.subheader("📋 Column Information")

    col_info = pd.DataFrame({
        "Column": filtered.columns,
        "Data Type": filtered.dtypes.astype(str),
        "Non-Null Count": filtered.count(),
        "Null Count": filtered.isnull().sum(),
        "Unique Values": [filtered[col].nunique() for col in filtered.columns]
    })

    st.dataframe(col_info, use_container_width=True)

    # Statistical summary
    st.subheader("📈 Statistical Summary")

    # Numeric columns only
    numeric_cols = filtered.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        st.dataframe(filtered[numeric_cols].describe(), use_container_width=True)
    else:
        st.info("No numeric columns found for statistical summary.")

    # Data filtering options
    st.subheader("🔍 Advanced Filtering")

    col1, col2 = st.columns(2)

    with col1:
        # Date range filter
        min_date = filtered["date"].min()
        max_date = filtered["date"].max()

        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered = filtered[
                (filtered["date"] >= pd.to_datetime(start_date)) &
                (filtered["date"] <= pd.to_datetime(end_date))
            ]

    with col2:
        # Temperature range filter
        if "avg_temp_f" in filtered.columns:
            temp_range = st.slider(
                "Temperature Range (°F)",
                float(filtered["avg_temp_f"].min()),
                float(filtered["avg_temp_f"].max()),
                (float(filtered["avg_temp_f"].min()), float(filtered["avg_temp_f"].max()))
            )

            filtered = filtered[
                (filtered["avg_temp_f"] >= temp_range[0]) &
                (filtered["avg_temp_f"] <= temp_range[1])
            ]

    # Filtered data preview
    st.subheader("📊 Filtered Data Preview")
    st.dataframe(filtered.head(preview_rows), use_container_width=True)

    # Export options
    st.subheader("💾 Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        # CSV export
        st.download_button(
            "⬇️ Download CSV",
            data=filtered.to_csv(index=False).encode(),
            file_name="weather_energy_data.csv",
            mime="text/csv"
        )

    with col2:
        # JSON export
        st.download_button(
            "⬇️ Download JSON",
            data=filtered.to_json(orient="records", indent=2),
            file_name="weather_energy_data.json",
            mime="application/json"
        )

    with col3:
        # Excel export (if available)
        try:
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered.to_excel(writer, sheet_name='Data', index=False)
            st.download_button(
                "⬇️ Download Excel",
                data=buffer.getvalue(),
                file_name="weather_energy_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("Excel export requires 'openpyxl' package")

    # Data insights
    st.subheader("💡 Quick Insights")

    insights_col1, insights_col2 = st.columns(2)

    with insights_col1:
        if "avg_temp_f" in filtered.columns:
            st.info(f"🌡️ **Temperature Range:** {filtered['avg_temp_f'].min():.1f}°F - {filtered['avg_temp_f'].max():.1f}°F")
            st.info(f"🌡️ **Average Temperature:** {filtered['avg_temp_f'].mean():.1f}°F")

    with insights_col2:
        if "energy_consumption" in filtered.columns:
            st.info(f"⚡ **Energy Range:** {filtered['energy_consumption'].min():.0f} - {filtered['energy_consumption'].max():.0f} MWh")
            st.info(f"⚡ **Average Consumption:** {filtered['energy_consumption'].mean():.0f} MWh")
