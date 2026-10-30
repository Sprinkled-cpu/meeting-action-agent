"""
Structured logging configuration with JSON and console formatters.
"""

import sys
import logging
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as structured single-line JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_logging(level: str = "INFO", json_format: bool = False) -> logging.Logger:
    """Configures root logger with clean formatting."""
    root_logger = logging.getLogger("meeting_action_agent")
    root_logger.setLevel(level.upper())
    
    # Avoid duplicate handlers
    if root_logger.handlers:
        return root_logger
        
    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        fmt = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        
    root_logger.addHandler(handler)
    return root_logger


logger = setup_logging()
