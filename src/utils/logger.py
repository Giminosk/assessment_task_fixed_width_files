import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:

    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)  # 10MB file size
    console_handler = logging.StreamHandler()

    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger("fixed_width_file_handler", "logs/app.log")
