from config_loader import load_config, get_api_keys
from logger import get_logger

config = load_config()
api_keys = get_api_keys()
logger = get_logger()

logger.info("Loaded config for %d cities", len(config["cities"]))
logger.info("NOAA Key loaded: %s", bool(api_keys["NOAA"]))
logger.info("EIA Key loaded: %s", bool(api_keys["EIA"]))
