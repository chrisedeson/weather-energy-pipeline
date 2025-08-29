#!/bin/bash
# Setup script for Weather-Energy Pipeline

echo "🔧 Setting up Weather-Energy Pipeline"
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to add your API keys to .env file:"
    echo "   1. NOAA API Key: https://www.ncdc.noaa.gov/cdo-web/token"
    echo "   2. EIA API Key: https://www.eia.gov/opendata/register.php"
    echo ""
    echo "   Edit .env file with your actual API keys before running the pipeline."
    echo ""
else
    echo "✅ .env file already exists"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Created virtual environment"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to .env file"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: python3 src/pipeline.py"
echo "4. Run: python3 src/transform.py"
echo "5. Run: python3 src/data_quality.py"
echo "6. Run: python3 src/anomaly_detection.py"
echo "7. Commit and push to GitHub"
echo "8. Run: streamlit run dashboards/app.py"
echo ""
echo "Or run the dashboard now with local data:"
echo "streamlit run dashboards/app.py"
