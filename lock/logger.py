import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(os.environ.get("WATERLOCK_LOG_DIR", Path.home() / ".waterlock"))
LOG_FILE = LOG_DIR / "engine.log"


def get_logger(name="waterlock"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(LOG_FILE, maxBytes=200_000, backupCount=2, encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except OSError:
        pass

    return logger