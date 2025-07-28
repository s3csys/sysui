from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any, Union
import secrets
from pathlib import Path
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # 60 minutes * 24 hours * 30 days = 30 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    SERVER_NAME: str = "SysUI"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Security Logging
    SECURITY_LOG_LEVEL: str = "INFO"
    SECURITY_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SECURITY_LOG_HANDLERS: str = "console"
    SECURITY_LOG_FILE: Optional[str] = None
    SECURITY_LOG_MAX_BYTES: int = 10485760  # 10MB
    SECURITY_LOG_BACKUP_COUNT: int = 5
    SECURITY_LOG_PII_FIELDS: str = "password,token,secret,email,hashed_password,verification_token,reset_token,refresh_token,access_token"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DATABASE_URI: Optional[str] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def validate_database_uri(cls, v: Optional[str], info) -> Optional[str]:
        # If SQLALCHEMY_DATABASE_URI is not set, try to use DATABASE_URI
        if not v and info.data.get("DATABASE_URI"):
            return info.data.get("DATABASE_URI")
        return v
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 2FA
    TOTP_ISSUER: str = "SysUI"
    
    # JWT Token
    TOKEN_ISSUER: str = "sysui-auth"
    TOKEN_AUDIENCE: str = "sysui-api"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], info) -> str:
        if not v:
            return info.data["SERVER_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED", mode="before")
    def get_emails_enabled(cls, v: bool, info) -> bool:
        return bool(
            info.data.get("SMTP_HOST")
            and info.data.get("SMTP_PORT")
            and info.data.get("EMAILS_FROM_EMAIL")
        )

    model_config = {
        "case_sensitive": True, 
        "env_file": ".env",
        "extra": "allow"
    }


settings = Settings()