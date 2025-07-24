"""
logger.py – configure a daily–rotating logger that writes:
  [DD-MM-YYYY HH:MM:SS] [LEVEL] [payload]
Logs user inputs, model outputs, reasoning, errors.
Provides setup utilities for application-wide logging.
"""
from loguru import logger
import os

def setup_logger(log_dir: str, log_name: str = "app"):
    """
    Configure loguru logger with daily rotation and multiple log levels.

    Args:
        log_dir (str): Directory where logs are stored.
        log_name (str): Log file name prefix.

    Returns:
        loguru.logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{log_name}.log")
    logger.remove()  # Remove default handler
    logger.add(log_path, rotation="1 day", retention="7 days", encoding="utf-8",
               format="[<green>{time:DD-MM-YYYY HH:mm:ss}</green>] [<level>{level}</level>] <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>")
    return logger