import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def configure(root: Path):
    folder = root / "data" / "logs"
    folder.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("mgu_manager")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(folder / "mgu-unified-manager.log",
                                      maxBytes=2_000_000, backupCount=4,
                                      encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    return logger
