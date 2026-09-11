"""Utility functions including logging initialization and retry decorators.

Provides cross-cutting concerns like logging configuration and backoff retry logic.
"""
from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
import time
from functools import wraps
from pathlib import Path
from typing import Callable, Any, TypeVar

T = TypeVar("T", bound=Callable[..., Any])

def setup_logging(log_dir: Path) -> logging.Logger:
    """Configures structured logging to both console and a rotating log file.

    Args:
        log_dir: The directory where log files should be written.

    Returns:
        A configured Logger instance.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "ecourts_scraper.log"

    logger = logging.getLogger("ecourts_scraper")
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers if re-initialized
    if logger.handlers:
        return logger

    # Console Handler (Level INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating, Level DEBUG)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

def retry_on_failure(
    retries: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[T], T]:
    """Decorator to retry a function with exponential backoff on specified exceptions.

    Args:
        retries: Number of retries before giving up.
        delay: Initial delay between retries in seconds.
        backoff: Multiplicative factor applied to the delay on each failure.
        exceptions: Tuple of exception types to trigger a retry.
    """
    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger("ecourts_scraper")
            current_delay = delay
            for attempt in range(1, retries + 2):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt > retries:
                        logger.error(
                            f"Function '{func.__name__}' failed after {retries} retries. Exception: {e}"
                        )
                        raise
                    logger.warning(
                        f"Attempt {attempt}/{retries + 1} of '{func.__name__}' failed with exception: {e}. "
                        f"Retrying in {current_delay:.2f} seconds..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper  # type: ignore
    return decorator

def clean_text(text: Any) -> str:
    """Standardizes text values by removing trailing/leading whitespaces and multiple spaces."""
    if not text:
        return ""
    return " ".join(str(text).split())
