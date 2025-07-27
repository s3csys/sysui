#!/usr/bin/env python
"""
Dependency checker script.

Checks if all required dependencies are installed and available.

Usage:
    python -m scripts.check_dependencies
"""

import importlib.util
import shutil
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.9 or higher."""
    required_version = (3, 9)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]} or higher is required")
        print(f"   Current version: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    else:
        print(f"✅ Python {current_version[0]}.{current_version[1]}.{current_version[2]} detected")
        return True


def check_pip_package(package_name):
    """Check if a pip package is installed."""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ {package_name} is not installed")
        return False
    else:
        print(f"✅ {package_name} is installed")
        return True


def check_command(command, args=["-v"]):
    """Check if a command is available."""
    if shutil.which(command) is None:
        print(f"❌ {command} is not installed or not in PATH")
        return False
    else:
        try:
            result = subprocess.run([command] + args, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   check=False)
            print(f"✅ {command} is installed")
            return True
        except Exception as e:
            print(f"❌ {command} check failed: {e}")
            return False


def check_docker():
    """Check if Docker and Docker Compose are installed."""
    docker_ok = check_command("docker", ["--version"])
    compose_ok = check_command("docker-compose", ["--version"])
    
    if docker_ok and compose_ok:
        print("✅ Docker environment is ready")
        return True
    else:
        print("❌ Docker environment is not complete")
        return False


def check_database_connection():
    """Check if database connection is possible."""
    try:
        import os
        from dotenv import load_dotenv
        
        # Try to load environment variables
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            print("✅ .env file found")
        else:
            print("❌ .env file not found")
            return False
        
        # Try to connect to database
        try:
            import sqlalchemy
            from sqlalchemy import create_engine
            
            database_url = os.getenv("DATABASE_URI")
            if not database_url:
                print("❌ DATABASE_URI not set in .env file")
                return False
            
            engine = create_engine(database_url)
            connection = engine.connect()
            connection.close()
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    except ImportError:
        print("❌ Required packages for database check not installed")
        return False


def main():
    """Run all dependency checks."""
    print("Checking system dependencies...\n")
    
    python_ok = check_python_version()
    print()
    
    print("Checking required Python packages...")
    fastapi_ok = check_pip_package("fastapi")
    sqlalchemy_ok = check_pip_package("sqlalchemy")
    alembic_ok = check_pip_package("alembic")
    pydantic_ok = check_pip_package("pydantic")
    jose_ok = check_pip_package("jose")
    passlib_ok = check_pip_package("passlib")
    print()
    
    print("Checking external tools...")
    docker_ok = check_docker()
    print()
    
    print("Checking database connection...")
    db_ok = check_database_connection()
    print()
    
    # Summary
    all_ok = all([
        python_ok, fastapi_ok, sqlalchemy_ok, alembic_ok, 
        pydantic_ok, jose_ok, passlib_ok, db_ok
    ])
    
    print("Summary:")
    if all_ok:
        print("✅ All dependencies are satisfied!")
    else:
        print("❌ Some dependencies are missing or not configured correctly.")
        print("   Please install missing dependencies and check your configuration.")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())