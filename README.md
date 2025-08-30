# 🔌 US Weather + Energy Analysis Pipeline

![CI/CD Status](https://github.com/chrisedeson/weather-energy-pipeline/actions/workflows/daily-pipeline.yml/badge.svg)

A production-grade data pipeline and interactive dashboard for analyzing the relationship between temperature and energy usage across 5 major US cities: New York, Chicago, Houston, Phoenix, and Seattle.

🔗 **Live Demo:** [weather-energy-pipeline.streamlit.app](https://weather-energy-pipeline.streamlit.app/)

🎥 **Video Walkthrough:** [Watch on YouTube](https://youtu.be/Ky0yjNRjG7o)

---

## 🚀 Features

- **Monthly Data Ingestion**: Automated pipeline fetching weather + energy data from NOAA and EIA APIs
- **Data Quality Monitoring**: Comprehensive reports on missing values, outliers, and data freshness
- **Interactive Dashboard**: 5-tab Streamlit interface with trend analysis, forecasting, and geographic views
- **Anomaly Detection**: Machine learning-based outlier identification using Isolation Forest
- **Multi-City Analysis**: Comparative analysis across 5 major US metropolitan areas
- **CI/CD Pipeline**: Automated monthly data refresh via GitHub Actions
- **Export Capabilities**: Downloadable datasets in multiple formats

---

## 🛠️ Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
git clone https://github.com/chrisedeson/weather-energy-pipeline.git
cd weather-energy-pipeline
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Clone and navigate**

   ```bash
   git clone https://github.com/chrisedeson/weather-energy-pipeline.git
   cd weather-energy-pipeline
   ```

2. **Environment setup**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **API Configuration**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - NOAA API Key: https://www.ncdc.noaa.gov/cdo-web/token
   # - EIA API Key: https://www.eia.gov/opendata/register.php
   ```

4. **Launch Dashboard**
   ```bash
   streamlit run dashboards/app.py
   ```

---

## 🏙️ Cities Covered

| City     | State | NOAA Station      | EIA Region |
| -------- | ----- | ----------------- | ---------- |
| New York | NY    | GHCND:USW00094728 | NYIS       |
| Chicago  | IL    | GHCND:USW00094846 | PJM        |
| Houston  | TX    | GHCND:USW00012960 | ERCO       |
| Phoenix  | AZ    | GHCND:USW00023183 | AZPS       |
| Seattle  | WA    | GHCND:USW00024233 | SCL        |

---

## 📊 Dashboard Tabs

1. **📈 Trends & Analysis**: Historical temperature vs energy consumption patterns
2. **🔮 Forecasting**: Predictive analytics and trend projections
3. **🗺️ Geographic**: Interactive US map with city-level metrics
4. **📋 Data Quality**: Automated quality reports and anomaly detection
5. **📄 Raw Data**: Complete dataset browser with export options

---

## 🧪 CI/CD Pipeline

Automated monthly data ingestion via GitHub Actions:

- **Schedule**: Monthly on the 1st at 12:00 UTC
- **Trigger**: Manual dispatch available
- **Workflow**: `.github/workflows/daily-pipeline.yml`
- **Data Window**: 90-day rolling window (current + 89 days historical)
- **Coverage**: Data fetching, quality checks, and validation

---

## � Data Files

All files are automatically updated in the `data/` directory:

- `merged_data.parquet`: Primary dataset (8,690+ records, 5 cities, 90+ days)
- `anomalies.csv`: ML-detected outliers and anomalies
- `quality_report.json`: Automated data quality metrics
- `raw/` directory: Individual city data files (CSV format)

---

## 📦 Dependencies

Core packages (managed via `requirements.txt` or `pyproject.toml`):

- **Data Processing**: pandas, numpy
- **Visualization**: plotly, matplotlib, seaborn, streamlit
- **APIs**: requests, pyyaml
- **ML**: scikit-learn
- **Environment**: python-dotenv

### Using Poetry (Alternative)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run dashboard
poetry run streamlit run dashboards/app.py
```

---

## 🔧 Pipeline Scripts

Execute in order for complete data refresh:

```bash
# 1. Fetch raw data from APIs
python3 src/pipeline.py

# 2. Clean and transform data
python3 src/transform.py

# 3. Generate quality reports
python3 src/data_quality.py

# 4. Run anomaly detection
python3 src/anomaly_detection.py
```

---

## 📈 Data Quality Metrics

Automated checks include:

- **Missing Values**: Count and location of null entries
- **Outliers**: Temperature extremes (>130°F or <-50°F) and invalid energy readings
- **Freshness**: Data age validation (flags data older than 24 hours)
- **Completeness**: Coverage across all 5 cities and date ranges

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python3 -m pytest tests/`
5. Submit a pull request

---
