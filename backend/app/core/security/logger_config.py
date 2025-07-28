import os
import logging
import logging.handlers
from typing import Dict, Any, Optional, List

from app.core.config import settings

# Default configuration
DEFAULT_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file"],  # Default to both console and file
    "pii_fields": [
        # Authentication data
        "password", 
        "token", 
        "secret", 
        "email", 
        "hashed_password", 
        "verification_token", 
        "reset_token", 
        "refresh_token", 
        "access_token",
        # Additional PII fields
        "ip_address",
        "user_agent",
        "cookie",
        "authorization",
        "phone",
        "address",
        "full_name",
        "backup_code",
        "hashed_code",
        "totp_secret"
    ],
    "file_path": "security.log",  # Default file path if not specified
    "max_bytes": 10485760,  # 10MB
    "backup_count": 10,  # Keep more backups
    "audit_enabled": True,  # Enable audit logging
    "audit_file_path": "audit.log"  # Separate file for audit logs
}


def get_log_level(level_str: str) -> int:
    """Convert string log level to logging level."""
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return levels.get(level_str.upper(), logging.INFO)


def get_logger_config() -> Dict[str, Any]:
    """Get logger configuration from environment or use defaults."""
    config = DEFAULT_CONFIG.copy()
    
    # Override from environment variables if set
    if hasattr(settings, "SECURITY_LOG_LEVEL"):
        config["level"] = settings.SECURITY_LOG_LEVEL
    
    if hasattr(settings, "SECURITY_LOG_FORMAT"):
        config["format"] = settings.SECURITY_LOG_FORMAT
    
    if hasattr(settings, "SECURITY_LOG_HANDLERS"):
        handlers = settings.SECURITY_LOG_HANDLERS
        if isinstance(handlers, str):
            config["handlers"] = [h.strip() for h in handlers.split(",")]
        else:
            config["handlers"] = handlers
    
    if hasattr(settings, "SECURITY_LOG_FILE"):
        config["file_path"] = settings.SECURITY_LOG_FILE
    
    if hasattr(settings, "SECURITY_LOG_MAX_BYTES"):
        config["max_bytes"] = settings.SECURITY_LOG_MAX_BYTES
    
    if hasattr(settings, "SECURITY_LOG_BACKUP_COUNT"):
        config["backup_count"] = settings.SECURITY_LOG_BACKUP_COUNT
    
    if hasattr(settings, "SECURITY_LOG_PII_FIELDS"):
        pii_fields = settings.SECURITY_LOG_PII_FIELDS
        if isinstance(pii_fields, str):
            config["pii_fields"] = [f.strip() for f in pii_fields.split(",")]
        else:
            config["pii_fields"] = pii_fields
    
    return config


def configure_security_logger(logger: logging.Logger, config: Optional[Dict[str, Any]] = None) -> None:
    """Configure security logger with the given configuration."""
    if config is None:
        config = get_logger_config()
    
    # Set level
    logger.setLevel(get_log_level(config["level"]))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:  # Make a copy of the list
        logger.removeHandler(handler)
    
    # Add handlers
    handlers = []
    
    if "console" in config["handlers"]:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(config["format"]))
        handlers.append(console_handler)
    
    if "file" in config["handlers"] and config["file_path"]:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config["file_path"],
            maxBytes=config["max_bytes"],
            backupCount=config["backup_count"]
        )
        file_handler.setFormatter(logging.Formatter(config["format"]))
        handlers.append(file_handler)
    
    # Add handlers to logger
    for handler in handlers:
        logger.addHandler(handler)


def get_pii_fields() -> List[str]:
    """Get list of PII fields to mask in logs."""
    config = get_logger_config()
    return config["pii_fields"]