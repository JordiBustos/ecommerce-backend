"""
Security Logging Configuration
Tracks security events, suspicious activity, and potential threats
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Security event logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Security log file handler (rotates at 10MB, keeps 10 backups)
security_handler = RotatingFileHandler(
    log_dir / "security.log", maxBytes=10_485_760, backupCount=10
)
security_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
security_logger.addHandler(security_handler)

# Access log handler
access_logger = logging.getLogger("access")
access_logger.setLevel(logging.INFO)

access_handler = RotatingFileHandler(
    log_dir / "access.log", maxBytes=10_485_760, backupCount=10
)
access_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
access_logger.addHandler(access_handler)


def log_security_event(event_type: str, details: dict, severity: str = "info"):
    """Log security-related events"""
    message = f"[{event_type}] {details}"

    if severity == "critical":
        security_logger.critical(message)
    elif severity == "error":
        security_logger.error(message)
    elif severity == "warning":
        security_logger.warning(message)
    else:
        security_logger.info(message)


def log_access(ip: str, method: str, path: str, status: int, user_id: int = None):
    """Log access attempts"""
    user_info = f"user_id={user_id}" if user_id else "anonymous"
    access_logger.info(f"{ip} - {method} {path} - {status} - {user_info}")
