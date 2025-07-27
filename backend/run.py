#!/usr/bin/env python
"""
Application runner script.

Usage:
    python run.py
"""

import os
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.getenv("API_HOST", settings.API_HOST)
    port = int(os.getenv("API_PORT", settings.API_PORT))
    reload = os.getenv("API_RELOAD", "False").lower() in ("true", "1", "t")
    
    print(f"Starting server at {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )