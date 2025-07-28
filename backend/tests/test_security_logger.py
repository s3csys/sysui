import pytest
import json
import logging
from unittest.mock import MagicMock, patch
from fastapi import Request

from app.core.security.logger import (
    log_security_event,
    log_auth_success,
    log_auth_failure,
    log_security_violation,
    mask_pii
)


def test_mask_pii():
    """Test that PII is properly masked in logs."""
    # Test data with PII
    data = {
        "username": "testuser",
        "password": "secret123",
        "email": "test@example.com",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "non_sensitive": "visible data"
    }
    
    # Mask PII
    masked = mask_pii(data)
    
    # Check that PII fields are masked
    assert masked["password"] == "*****"
    assert masked["email"] == "*****"
    assert masked["token"] == "*****"
    
    # Check that non-PII fields are unchanged
    assert masked["username"] == "testuser"
    assert masked["non_sensitive"] == "visible data"
    
    # Check that original data is not modified
    assert data["password"] == "secret123"


@patch("app.core.security.logger.security_logger")
def test_log_security_event(mock_logger):
    """Test that security events are properly logged."""
    # Create mock request
    mock_request = MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"user-agent": "test-agent"}
    mock_request.url.path = "/api/auth/login"
    mock_request.method = "POST"
    
    # Log event
    log_security_event(
        "test_event",
        {"username": "testuser", "password": "secret123"},
        mock_request,
        "info"
    )
    
    # Check that logger was called
    mock_logger.info.assert_called_once()
    
    # Parse log message
    log_message = mock_logger.info.call_args[0][0]
    log_data = json.loads(log_message)
    
    # Check log structure
    assert "event_id" in log_data
    assert "timestamp" in log_data
    assert log_data["event_type"] == "test_event"
    assert log_data["details"]["username"] == "testuser"
    assert log_data["details"]["password"] == "*****"  # PII should be masked
    assert log_data["request"]["ip"] == "127.0.0.1"
    assert log_data["request"]["user_agent"] == "test-agent"
    assert log_data["request"]["path"] == "/api/auth/login"
    assert log_data["request"]["method"] == "POST"


@patch("app.core.security.logger.security_logger")
def test_log_auth_success(mock_logger):
    """Test that authentication success is properly logged."""
    # Log auth success
    log_auth_success("testuser", 123, None)
    
    # Check that logger was called
    mock_logger.info.assert_called_once()
    
    # Parse log message
    log_message = mock_logger.info.call_args[0][0]
    log_data = json.loads(log_message)
    
    # Check log structure
    assert log_data["event_type"] == "authentication_success"
    assert log_data["details"]["username"] == "testuser"
    assert log_data["details"]["user_id"] == 123


@patch("app.core.security.logger.security_logger")
def test_log_auth_failure(mock_logger):
    """Test that authentication failure is properly logged."""
    # Log auth failure
    log_auth_failure("testuser", "invalid_credentials", None)
    
    # Check that logger was called
    mock_logger.warning.assert_called_once()
    
    # Parse log message
    log_message = mock_logger.warning.call_args[0][0]
    log_data = json.loads(log_message)
    
    # Check log structure
    assert log_data["event_type"] == "authentication_failure"
    assert log_data["details"]["username"] == "testuser"
    assert log_data["details"]["reason"] == "invalid_credentials"


@patch("app.core.security.logger.security_logger")
def test_log_security_violation(mock_logger):
    """Test that security violations are properly logged."""
    # Log security violation
    log_security_violation(
        "rate_limit",
        {"ip": "127.0.0.1", "endpoint": "/api/auth/login"},
        None
    )
    
    # Check that logger was called
    mock_logger.error.assert_called_once()
    
    # Parse log message
    log_message = mock_logger.error.call_args[0][0]
    log_data = json.loads(log_message)
    
    # Check log structure
    assert log_data["event_type"] == "security_violation_rate_limit"
    assert log_data["details"]["ip"] == "127.0.0.1"
    assert log_data["details"]["endpoint"] == "/api/auth/login"