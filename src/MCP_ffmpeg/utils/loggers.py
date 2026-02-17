"""
This file will contain the code to set up logging
"""

import logging
import sys
from datetime import datetime

from src.MCP_ffmpeg.utils.variables import CommonVariables


def setup_logger(name: str, log_file: str = None, level=logging.DEBUG):
    """
    Set up a logger with console and file handlers.

    :param name: Logger name (usually __name__ from calling module)
    :param log_file: Path to log file (optional, defaults to logs/search_engine.log)
    :param level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    :return: logging.Logger Configured logger instance
    """

    # Create logs directory if it doesn't exist
    log_dir = CommonVariables.LOGS_DIR
    log_dir.mkdir(exist_ok=True)

    # Default log file with timestamp
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"search_engine_{timestamp}.log"
    else:
        log_file = log_dir / log_file

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Console handler (INFO and above, simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)

    # File handler (DEBUG and above, detailed format)
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str):
    """
    Get or create a logger for a module.

    :param name: Usually __name__ from the calling module
    :return:logging.Logger: Logger instance
    """

    return setup_logger(name)


def get_job_ffmpeg_logger(job_id: str) -> logging.Logger:
    """
    This method creates a log file for each job id

    :param job_id:job id
    :return: logger for job id
    """

    job_dir = CommonVariables.OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    log_file = job_dir / "ffmpeg_logs.log"

    log = logging.getLogger(f"ffmpeg.{job_id}")
    log.setLevel(logging.INFO)

    # avoid duplicate handlers if called multiple times
    if any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "") == str(log_file)
           for h in log.handlers):
        return log

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    log.addHandler(fh)
    # optional: don't also spam console via root handlers
    log.propagate = False

    return log