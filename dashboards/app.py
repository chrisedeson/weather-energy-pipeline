"""
Main Streamlit Dashboard Application
Orchestrates all dashboard components in a modular structure
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_data, load_quality_report
from components.trends_tab import render_trends_tab
from components.forecasting_tab import render_forecasting_tab
from components.geographic_tab import render_geographic_tab
from components.data_quality_tab import render_data_quality_tab
from components.raw_data_tab import render_raw_data_tab

# ---- Page Configuration
st.set_page_config(
    page_title="US Weather + Energy Dashboard",
    layout="wide",
    page_icon="🔌"
)

def main():
    """Main dashboard application"""
    st.title("🔌 US Weather + Energy Dashboard")

    # ---- Load Data
    with st.spinner("Loading data..."):
        df = load_data()
        report = load_quality_report()

    if df.empty:
        st.error("❌ Unable to load data. Please check your data pipeline.")
        return

    # ---- Sidebar Filters
    st.sidebar.header("🎛️ Filters")

    # City selection
    cities = sorted(df["city"].unique().tolist())
    selected_cities = st.sidebar.multiselect(
        "Select Cities",
        cities,
        default=cities,
        help="Choose cities to include in the analysis"
    )

    # Data info in sidebar
    st.sidebar.header("📊 Data Info")
    st.sidebar.metric("Total Records", len(df))
    st.sidebar.metric("Cities Available", len(cities))
    st.sidebar.metric("Date Range", f"{df['date'].min()} to {df['date'].max()}")

    # ---- Main Content Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Trends & Analysis",
        "🔮 Forecasting",
        "🗺️ Geographic",
        "🚨 Data Quality",
        "📄 Raw Data"
    ])

    # ---- Render Each Tab
    with tab1:
        render_trends_tab(df, selected_cities)

    with tab2:
        render_forecasting_tab(df, selected_cities)

    with tab3:
        render_geographic_tab(df, selected_cities)

    with tab4:
        render_data_quality_tab(df, selected_cities, report)

    with tab5:
        render_raw_data_tab(df, selected_cities)

    # ---- Footer
    st.markdown("---")
    st.markdown("*Dashboard last updated: Data refreshes monthly on the 1st*")
    st.markdown("*Built with Streamlit, Pandas, and Plotly*")

if __name__ == "__main__":
    main()
