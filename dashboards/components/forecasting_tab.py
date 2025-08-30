"""
Forecasting Tab Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

    # Calculate confidence interval
    std_dev = np.std(y)
    upper_bound = forecast_values + 1.96 * std_dev
    lower_bound = forecast_values - 1.96 * std_dev

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

    # Create beautiful forecast visualization
    fig = px.line(
        combined_df,
        x="date",
        y="energy_consumption",
        color="type",
        title=f"{city} Energy Consumption Forecast",
        labels={
            "energy_consumption": "Energy Consumption (MWh)",
            "date": "Date",
            "type": "Data Type"
        },
        color_discrete_map={
            "Historical": "#2E86AB",  # Professional blue
            "Forecast": "#F24236"    # Vibrant red-orange
        }
    )

    # Enhance the plot styling
    fig.update_traces(
        mode="lines+markers",
        line=dict(width=3),
        marker=dict(size=6, symbol="circle"),
        hovertemplate="<b>%{fullData.name}</b><br>" +
                     "Date: %{x|%Y-%m-%d}<br>" +
                     "Consumption: %{y:.1f} MWh<br>" +
                     "<extra></extra>"
    )

    # Add confidence interval as filled area
    fig.add_trace(
        go.Scatter(
            x=list(forecast_dates) + list(forecast_dates)[::-1],
            y=list(upper_bound) + list(lower_bound)[::-1],
            fill='toself',
            fillcolor='rgba(242, 66, 54, 0.2)',  # Light red with transparency
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval',
            showlegend=True,
            hovertemplate="Confidence Interval<br>" +
                         "Upper: %{y:.1f} MWh<br>" +
                         "<extra></extra>"
        )
    )

    # Add a vertical line to separate historical from forecast using scatter
    fig.add_trace(
        go.Scatter(
            x=[last_date.strftime('%Y-%m-%d'), last_date.strftime('%Y-%m-%d')],
            y=[combined_df['energy_consumption'].min(), combined_df['energy_consumption'].max()],
            mode='lines',
            line=dict(color='gray', dash='dot', width=2),
            name='Forecast Start',
            showlegend=True,
            hovertemplate="Forecast begins<br>%{x}<extra></extra>"
        )
    )

    # Enhance layout
    fig.update_layout(
        height=500,
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            linecolor='lightgray',
            tickformat="%b %d"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            linecolor='lightgray',
            title_font=dict(size=14)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgray',
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Add subtle styling
    fig.update_xaxes(showline=True, linewidth=1, linecolor='lightgray', mirror=False)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='lightgray', mirror=False)

    st.plotly_chart(fig, use_container_width=True)

    # Enhanced Forecast metrics with better styling
    st.subheader("📊 Forecast Analytics")

    avg_forecast = np.mean(forecast_values)
    trend = (forecast_values[-1] - forecast_values[0]) / days
    accuracy_indicator = "High" if len(city_df) > 30 else "Medium" if len(city_df) > 15 else "Low"

    # Create metrics in a more visually appealing layout
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📈 Avg Daily Forecast",
            f"{avg_forecast:.1f} MWh",
            delta=f"{trend:+.2f} MWh/day",
            delta_color="normal"
        )

    with col2:
        confidence_range = upper_bound[-1] - lower_bound[-1]
        st.metric(
            "🎯 Confidence Range",
            f"±{confidence_range:.1f} MWh",
            help="95% confidence interval width"
        )

    with col3:
        st.metric(
            "📅 Forecast Period",
            f"{days} days",
            help=f"Forecasting from {forecast_dates[0].strftime('%Y-%m-%d')} to {forecast_dates[-1].strftime('%Y-%m-%d')}"
        )

    with col4:
        st.metric(
            "📊 Model Accuracy",
            accuracy_indicator,
            help=f"Based on {len(city_df)} historical data points"
        )

    # Enhanced summary with better formatting
    trend_direction = "📈 increasing" if trend > 0 else "📉 decreasing"
    confidence_level = "High" if confidence_range < np.mean(forecast_values) * 0.1 else "Medium"

    st.success(
        f"🔮 **Forecast Summary for {city}:**\n\n"
        f"• Expected average daily consumption: **{avg_forecast:.1f} MWh**\n"
        f"• Trend: **{trend_direction}** by {abs(trend):.2f} MWh/day\n"
        f"• Confidence Level: **{confidence_level}**\n"
        f"• Forecast Period: **{days} days** ({forecast_dates[0].strftime('%b %d')} - {forecast_dates[-1].strftime('%b %d')})"
    )

    # Enhanced forecast table with better formatting
    st.subheader("📋 Detailed Forecast")

    # Add some styling to the dataframe
    forecast_table = forecast_df.copy()
    forecast_table["date"] = forecast_table["date"].dt.strftime("%Y-%m-%d")
    forecast_table["energy_consumption"] = forecast_table["energy_consumption"].round(1)
    forecast_table["confidence_lower"] = lower_bound.round(1)
    forecast_table["confidence_upper"] = upper_bound.round(1)
    forecast_table = forecast_table.rename(columns={
        "energy_consumption": "Forecast (MWh)",
        "confidence_lower": "Lower Bound",
        "confidence_upper": "Upper Bound"
    })

    st.dataframe(
        forecast_table,
        use_container_width=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
            "Forecast (MWh)": st.column_config.NumberColumn("Forecast (MWh)", format="%.1f"),
            "Lower Bound": st.column_config.NumberColumn("Lower Bound", format="%.1f"),
            "Upper Bound": st.column_config.NumberColumn("Upper Bound", format="%.1f")
        }
    )
