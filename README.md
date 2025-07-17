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
    
    source .venv/bin/activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run Streamlit app**
    ```bash
    streamlit run app.py
    ```

## 🧪 **CI/CD**

This project uses GitHub Actions for automatic daily data ingestion and quality checks. Workflow is defined in `.github/workflows/daily-pipeline.yml`.

## 📊 **Data**

Data is stored in the `data/` directory and auto-updated daily:

- `merged_data.csv`: main dataset

- `quality_report.json`: summary of freshness and outliers

<!-- - `anomalies.csv`: detected anomalies -->
