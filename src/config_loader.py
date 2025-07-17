import os
import yaml
from dotenv import load_dotenv

load_dotenv()  # Load .env file

def load_config(path="config/config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_api_keys():
    return {
        "NOAA": os.getenv("NOAA_API_KEY"),
        "EIA": os.getenv("EIA_API_KEY")
    }
