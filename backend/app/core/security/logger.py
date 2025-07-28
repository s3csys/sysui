import logging
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import uuid
import os
from fastapi import Request

from app.core.security.logger_config import configure_security_logger, get_pii_fields, get_logger_config

# Configure security logger
security_logger = logging.getLogger("security")

# Configure audit logger
audit_logger = logging.getLogger("audit")

# Configure loggers with settings
config = get_logger_config()
configure_security_logger(security_logger)

# Configure audit logger if enabled
if config.get("audit_enabled", False):
    audit_format = "%(asctime)s - AUDIT - %(message)s"
    audit_handler = logging.FileHandler(config.get("audit_file_path", "audit.log"))
    audit_handler.setFormatter(logging.Formatter(audit_format))
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)


def mask_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask personally identifiable information in logs.
    
    Args:
        data: Dictionary containing data to mask
        
    Returns:
        Dict: Data with PII masked
    """
    masked_data = data.copy()
    
    # Get PII fields from configuration
    pii_fields = get_pii_fields()
    
    # Additional PII fields that should always be masked
    additional_pii_fields = [
        "password", "token", "secret", "key", "hash", "email", "phone",
        "address", "name", "ssn", "social_security", "credit_card", "card_number",
        "verification_token", "reset_token", "access_token", "refresh_token"
    ]
    
    # Combine all PII fields
    all_pii_fields = set(pii_fields + additional_pii_fields)
    
    # Mask PII fields (exact matches)
    for field in all_pii_fields:
        if field in masked_data:
            masked_data[field] = "*****"
    
    # Mask PII fields (partial matches)
    for key in list(masked_data.keys()):
        for pii_field in all_pii_fields:
            # Check if the key contains a PII field name
            if pii_field in key.lower() and masked_data[key] is not None and isinstance(masked_data[key], (str, int)):
                masked_data[key] = "*****"
                break
    
    return masked_data


def log_security_event(event_type: str, details: Dict[str, Any], request: Optional[Request] = None, level: str = "info") -> None:
    """
    Log a security event with structured data.
    
    Args:
        event_type: Type of security event (e.g., "login_attempt", "password_change")
        details: Details of the event
        request: Optional FastAPI request object
        level: Log level ("info", "warning", "error")
    """
    # Create event ID
    event_id = str(uuid.uuid4())
    
    # Get timestamp
    timestamp = datetime.utcnow().isoformat()
    
    # Get request information if available
    request_info = {}
    if request:
        request_info = {
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "path": str(request.url.path),
            "method": request.method
        }
    
    # Mask PII in details
    masked_details = mask_pii(details)
    
    # Create log entry
    log_entry = {
        "event_id": event_id,
        "timestamp": timestamp,
        "event_type": event_type,
        "details": masked_details,
        "request": request_info
    }
    
    # Log with appropriate level
    log_message = json.dumps(log_entry)
    if level == "warning":
        security_logger.warning(log_message)
    elif level == "error":
        security_logger.error(log_message)
    else:
        security_logger.info(log_message)


def log_auth_success(username: str, user_id: int, request: Optional[Request] = None) -> None:
    """
    Log successful authentication.
    
    Args:
        username: Username of the authenticated user
        user_id: ID of the authenticated user
        request: Optional FastAPI request object
    """
    log_security_event(
        event_type="authentication_success",
        details={
            "username": username,
            "user_id": user_id
        },
        request=request,
        level="info"
    )


def log_auth_failure(username: str, reason: str, request: Optional[Request] = None) -> None:
    """
    Log failed authentication attempt.
    
    Args:
        username: Username that failed authentication
        reason: Reason for authentication failure
        request: Optional FastAPI request object
    """
    log_security_event(
        event_type="authentication_failure",
        details={
            "username": username,
            "reason": reason
        },
        request=request,
        level="warning"
    )


def log_security_violation(violation_type: str, details: Dict[str, Any], request: Optional[Request] = None) -> None:
    """
    Log security violation.
    
    Args:
        violation_type: Type of security violation
        details: Details of the violation
        request: Optional FastAPI request object
    """
    log_security_event(
        event_type=f"security_violation_{violation_type}",
        details=details,
        request=request,
        level="error"
    )


def log_audit_event(action: str, user_id: Optional[int] = None, username: Optional[str] = None, 
                   resource_type: Optional[str] = None, resource_id: Optional[Union[int, str]] = None,
                   details: Optional[Dict[str, Any]] = None, request: Optional[Request] = None) -> None:
    """
    Log an audit event for sensitive operations.
    
    Args:
        action: The action being performed (e.g., "user_created", "role_changed")
        user_id: ID of the user performing the action
        username: Username of the user performing the action
        resource_type: Type of resource being acted upon (e.g., "user", "role")
        resource_id: ID of the resource being acted upon
        details: Additional details about the action
        request: Optional FastAPI request object
    """
    if not config.get("audit_enabled", False):
        return
    
    # Create event ID
    event_id = str(uuid.uuid4())
    
    # Get timestamp
    timestamp = datetime.utcnow().isoformat()
    
    # Get request information if available
    request_info = {}
    if request:
        request_info = {
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "path": str(request.url.path),
            "method": request.method
        }
    
    # Mask PII in details
    masked_details = mask_pii(details or {})
    
    # Create audit log entry
    audit_entry = {
        "event_id": event_id,
        "timestamp": timestamp,
        "action": action,
        "user_id": user_id,
        "username": username,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": masked_details,
        "request": request_info
    }
    
    # Log audit event
    audit_logger.info(json.dumps(audit_entry))