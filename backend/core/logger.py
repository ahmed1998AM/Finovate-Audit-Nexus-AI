"""
Finovate Audit Nexus AI - Logger Module

Centralized logging configuration for the entire application
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path


class FinovateLogger:
    """Custom logger class for Finovate Audit Nexus AI"""

    def __init__(
        self,
        name: str = "finovate",
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_size_mb: int = 10,
        retention_days: int = 30
    ):
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = Path(log_dir)
        self.max_size_mb = max_size_mb
        self.retention_days = retention_days

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # JSON handler for structured logging
        json_log_file = self.log_dir / f"{name}_json_{datetime.now().strftime('%Y%m%d')}.log"
        self.json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
        self.json_handler.setLevel(self.log_level)

    def _log_json(self, level: str, message: str, **kwargs):
        """Log message in JSON format"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
            **kwargs
        }
        self.json_handler.emit(
            logging.LogRecord(
                name=self.name,
                level=self.log_level,
                pathname="",
                lineno=0,
                msg=json.dumps(log_entry, ensure_ascii=False),
                args=(),
                exc_info=None
            )
        )

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message)
        if kwargs:
            self._log_json("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message)
        if kwargs:
            self._log_json("WARNING", message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
        if kwargs:
            self._log_json("ERROR", message, exc_info=exc_info, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message)
        if kwargs:
            self._log_json("DEBUG", message, **kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info)
        if kwargs:
            self._log_json("CRITICAL", message, exc_info=exc_info, **kwargs)

    def audit(self, action: str, user: str, details: dict = None):
        """Log audit trail"""
        self.info(
            f"AUDIT: {action}",
            user=user,
            action=action,
            details=details or {},
            audit_trail=True
        )


def setup_logger(
    name: str = "finovate",
    log_level: str = "INFO",
    log_dir: str = "logs"
) -> FinovateLogger:
    """
    Setup and return a logger instance

    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files

    Returns:
        FinovateLogger instance
    """
    return FinovateLogger(name=name, log_level=log_level, log_dir=log_dir)


# Global default logger
default_logger = setup_logger()


def get_logger(name: str = "finovate") -> FinovateLogger:
    """Get a logger instance with the specified name"""
    return setup_logger(name=name)
