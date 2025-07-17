import logging
from pathlib import Path

LOG_PATH = Path("logs/pipeline.log")
LOG_PATH.parent.mkdir(exist_ok=True)

def get_logger(name="pipeline", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Console
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

        # File
        fh = logging.FileHandler(LOG_PATH)
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
