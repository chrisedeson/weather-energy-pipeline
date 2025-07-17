# 🔌 US Weather + Energy Analysis Pipeline

![CI/CD Status](https://github.com/chrisedeson/weather-energy-pipeline/actions/workflows/daily-pipeline.yml/badge.svg)

A production-grade data pipeline and interactive dashboard for analyzing the relationship between temperature and energy usage across US cities.

🔗 **Live Demo:** [weather-energy-pipeline.streamlit.app](https://weather-energy-pipeline.streamlit.app/)

---

## 🚀 Features

- Daily ingestion and refresh of weather + energy usage data
- Data quality reports (missing values, freshness, outliers)
- Historical trend visualization by city and time range
- Machine learning-based anomaly detection
- Downloadable full CSV
- CI/CD with GitHub Actions

---

## 🛠️ Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/chrisedeson/weather-energy-pipeline.git

   cd weather-energy-pipeline
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv

   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add .env file**  
   Create a `.env` file using .env.example as a guide:
   ```
   NOAA_API_KEY=your_openweather_api_key
   EIA_API_KEY=your_energy_api_key
   ```

5. **Run Streamlit app**
   ```bash
   streamlit run dashboards/app.py
   ```

---

## 🧪 CI/CD

This project uses GitHub Actions for automatic daily data ingestion and quality checks.  
Workflow is defined in `.github/workflows/daily-pipeline.yml`.

It runs on:
- Daily schedule at 12:00 UTC
- Manual dispatch from GitHub UI

---

## 📊 Data Files

All updated daily into the `data/` folder:

- `merged_data.csv`: Final cleaned dataset
- `anomalies.csv`: Flagged anomalies via Isolation Forest
- `quality_report.json`: Freshness + missing values report

---