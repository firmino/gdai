"""
Logger Module

This module provides a custom logger for the GDAI project with enhanced features:
- Module path resolution for better log context.
- Configurable log levels and formats via environment variables.

Usage:
    from src.shared.logger import logger
    logger.info("This is an info message")
"""

import os
import sys
import inspect
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Disable existing handlers from the root logger
logging.getLogger().handlers = []


class ModulePathFilter(logging.Filter):
    """Filter that adds module path information to log records"""

    def _resolve_module_path(self, filepath):
        """
        Resolve a filepath to a module path in the format 'src.module.filename'
        """
        try:
            path_obj = Path(filepath).resolve()
            parts = []

            # Traverse up to find 'src' directory
            for parent in path_obj.parents:
                if parent.name == "src":
                    parts.append("src")
                    break
                parts.append(parent.name)

            # Add the filename without extension
            parts.reverse()
            parts.append(path_obj.stem)
            return ".".join(parts)
        except Exception as e:
            return f"unknown.{Path(filepath).name}" if filepath else "unknown"

    def _get_module_path(self, record):
        """
        Get the module path for a log record, either from the record's pathname
        or by inspecting the stack frames.

        Args:
            record: The log record

        Returns:
            A string representing the module path
        """
        # Try to use the pathname from the log record
        if hasattr(record, "pathname") and not ("logger.py" in record.pathname or "logging" in record.pathname):
            return self._resolve_module_path(record.pathname)

        # Fallback to stack inspection
        filepath = self._find_caller_filepath()
        if filepath:
            return self._resolve_module_path(filepath)
        return "unknown"

    def _find_caller_filepath(self):
        """
        Find the filepath of the actual caller by inspecting stack frames.

        Returns:
            The filepath of the caller or None if not found
        """
        frame = inspect.currentframe()
        try:
            # Navigate up the stack to find a non-logging caller
            while frame:
                filename = os.path.basename(frame.f_code.co_filename)
                if filename == "logger.py" or "logging" in frame.f_code.co_filename:
                    frame = frame.f_back
                else:
                    return frame.f_code.co_filename
            return None
        finally:
            # Clean up frame reference
            del frame

    def filter(self, record):
        """
        Add the module path to the log record.

        Args:
            record: The log record

        Returns:
            True to allow the log record to be processed
        """
        record.module_path = self._get_module_path(record)
        return True


# Create the GDAI logger
GDAI_LOG_LEVEL = os.getenv("GDAI_LOG_LEVEL", "INFO").upper()
if GDAI_LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    raise ValueError(f"Invalid GDAI_LOG_LEVEL: {GDAI_LOG_LEVEL}. Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")

gdai_logger = logging.getLogger("GDAI")
gdai_logger.setLevel(GDAI_LOG_LEVEL)

# Remove any existing handlers
for handler in gdai_logger.handlers[:]:
    gdai_logger.removeHandler(handler)

# Add a custom filter
gdai_logger.addFilter(ModulePathFilter())


# Get log format from environment or use default
GDAI_LOG_FORMAT = os.getenv("GDAI_LOG_FORMAT", "[%(asctime)s] [GDAI] [%(module_path)s] [%(levelname)s]: %(message)s")
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(GDAI_LOG_FORMAT, "%Y-%m-%d %H:%M:%S,%f")
old_format = formatter.formatTime

def format_time(self, record, datefmt=None):
    result = old_format(record, datefmt)
    return result[:-3]  # Remove last 3 digits of microseconds


formatter.formatTime = format_time.__get__(formatter)


# add file handler if enabled 
console_handler.setFormatter(formatter)
gdai_logger.handlers = [console_handler]
gdai_logger.propagate = False


GDAI_LOG_FILE_ENABLED = os.getenv("GDAI_LOG_FILE_ENABLED", "false").lower() == "true"
if GDAI_LOG_FILE_ENABLED:
    try:
        log_file_path = os.getenv("GDAI_LOG_FILE_PATH", "/tmp/gdai.log")
        max_bytes = int(float(os.getenv("GDAI_LOG_FILE_MAX_SIZE_MB", "10")) * 1024 * 1024)
        backup_count = int(os.getenv("GDAI_LOG_FILE_BACKUP_COUNT", "5"))
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file_path)
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=max_bytes, 
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        gdai_logger.addHandler(file_handler)
    except Exception as e:
        # Use console handler to report file handler initialization error
        console_handler.setFormatter(formatter)
        gdai_logger.addHandler(console_handler)
        gdai_logger.error(f"Failed to initialize file logging: {e}")


class Logger:
    """Singleton logger class that delegates to the configured GDAI logger"""
    _instance = None
 
    def __new__(cls):
        """Ensure only one instance of Logger exists"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the logger instance (only once)"""
        if self._initialized:
            return
        self._initialized = True

    def info(self, message, *args, **kwargs):
        """
        Log info message with optional formatting arguments.
        
        Args:
            message: The message to log (can include format specifiers)
            *args: Values to use for string formatting
            **kwargs: Additional parameters to pass to the logger
        """
        gdai_logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """
        Log warning message with optional formatting arguments.
        
        Args:
            message: The message to log (can include format specifiers)
            *args: Values to use for string formatting
            **kwargs: Additional parameters to pass to the logger
        """
        gdai_logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """
        Log error message with optional formatting arguments.
        
        Args:
            message: The message to log (can include format specifiers)
            *args: Values to use for string formatting
            **kwargs: Additional parameters to pass to the logger
        """
        gdai_logger.error(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """
        Log debug message with optional formatting arguments.
        
        Args:
            message: The message to log (can include format specifiers)
            *args: Values to use for string formatting
            **kwargs: Additional parameters to pass to the logger
        """
        gdai_logger.debug(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """
        Log critical message with optional formatting arguments.
        
        Args:
            message: The message to log (can include format specifiers)
            *args: Values to use for string formatting
            **kwargs: Additional parameters to pass to the logger
        """
        gdai_logger.critical(message, *args, **kwargs)

    def exception(self, message, *args, exc_info=True, **kwargs):
        """
        Log exception information with traceback.

        Should be called from an exception handler.

        Args:
            message: The message to log
            *args: Variable arguments for message formatting
            exc_info: Boolean indicating if exception info should be added, defaults to True
            **kwargs: Additional logger parameters
        """
        gdai_logger.error(message, *args, exc_info=exc_info, **kwargs)


# Create a singleton logger instance
logger = Logger()
