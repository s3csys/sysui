#!/bin/bash

# SysUI Installation Test Script
# This script verifies that all components of SysUI are correctly installed

# Set strict error handling
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage information
show_usage() {
    cat << EOF
SysUI Installation Test Script

Usage: $0 [OPTIONS]

Options:
  -h, --help           Display this help message and exit
  -v, --verbose        Enable verbose output

This script verifies that all components of SysUI are correctly installed.
EOF
}

# Function for logging
log() {
    local level=$1
    local message=$2
    
    case ${level} in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} ${message}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} ${message}"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} ${message}"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${message}"
            ;;
        *)
            echo -e "[${level}] ${message}"
            ;;
    esac
}

# Function to check if the script is run as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log "ERROR" "This script must be run as root or with sudo privileges"
        exit 1
    fi
}

# Function to test system packages
test_system_packages() {
    log "INFO" "Testing system packages..."
    
    # Define required packages
    local required_packages=("python3" "python3-pip" "python3-venv" "git" "curl" "wget")
    local missing_packages=()
    
    # Check each package
    for package in "${required_packages[@]}"; do
        if ! dpkg -l | grep -q "${package}"; then
            missing_packages+=("${package}")
        fi
    done
    
    # Check database packages
    if ! dpkg -l | grep -q "mysql-server\|mariadb-server"; then
        missing_packages+=("mysql-server/mariadb-server")
    fi
    
    # Check Redis
    if ! dpkg -l | grep -q "redis-server"; then
        missing_packages+=("redis-server")
    fi
    
    # Report results
    if [[ ${#missing_packages[@]} -eq 0 ]]; then
        log "SUCCESS" "All required system packages are installed"
    else
        log "ERROR" "Missing required packages: ${missing_packages[*]}"
        exit 1
    fi
}

# Function to test Python environment
test_python_env() {
    log "INFO" "Testing Python environment..."
    
    # Check Python version
    local python_version=$(python3 --version | cut -d' ' -f2)
    log "INFO" "Detected Python version: ${python_version}"
    
    # Check if Python version is at least 3.9
    if [[ $(echo "${python_version}" | cut -d. -f1) -lt 3 ]] || \
       [[ $(echo "${python_version}" | cut -d. -f1) -eq 3 && $(echo "${python_version}" | cut -d. -f2) -lt 9 ]]; then
        log "ERROR" "Python version must be at least 3.9. Found: ${python_version}"
        exit 1
    else
        log "SUCCESS" "Python version check passed"
    fi
    
    # Check virtual environment
    local venv_dir="/opt/sysui/venv"
    if [[ ! -d "${venv_dir}" ]]; then
        log "ERROR" "Python virtual environment not found at ${venv_dir}"
        exit 1
    fi
    
    # Check if pip is installed in the virtual environment
    if [[ ! -f "${venv_dir}/bin/pip" ]]; then
        log "ERROR" "pip not found in virtual environment"
        exit 1
    fi
    
    # Check if required Python packages are installed
    local required_packages=("fastapi" "uvicorn" "sqlalchemy" "pydantic" "python-jose" "passlib" "python-multipart" "mysqlclient" "redis" "rq" "pyotp")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! "${venv_dir}/bin/pip" list | grep -q "${package}"; then
            missing_packages+=("${package}")
        fi
    done
    
    # Report results
    if [[ ${#missing_packages[@]} -eq 0 ]]; then
        log "SUCCESS" "All required Python packages are installed"
    else
        log "ERROR" "Missing required Python packages: ${missing_packages[*]}"
        exit 1
    fi
}

# Function to test database
test_database() {
    log "INFO" "Testing database connection..."
    
    # Check if MySQL/MariaDB service is running
    if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mariadb; then
        log "ERROR" "MySQL/MariaDB service is not running"
        exit 1
    else
        log "SUCCESS" "Database service is running"
    fi
    
    # Check database configuration file
    local db_config="/opt/sysui/config/database.conf"
    if [[ ! -f "${db_config}" ]]; then
        log "ERROR" "Database configuration file not found at ${db_config}"
        exit 1
    else
        log "SUCCESS" "Database configuration file exists"
    fi
    
    # Extract database credentials from config file
    local db_name=$(grep "name" "${db_config}" | cut -d'=' -f2 | tr -d ' ')
    local db_user=$(grep "user" "${db_config}" | cut -d'=' -f2 | tr -d ' ')
    local db_password=$(grep "password" "${db_config}" | cut -d'=' -f2 | tr -d ' ')
    
    # Test database connection
    if mysql -u"${db_user}" -p"${db_password}" -e "USE ${db_name}" 2>/dev/null; then
        log "SUCCESS" "Database connection successful"
    else
        log "ERROR" "Failed to connect to database"
        exit 1
    fi
}

# Function to test Redis
test_redis() {
    log "INFO" "Testing Redis connection..."
    
    # Check if Redis service is running
    if ! systemctl is-active --quiet redis-server; then
        log "ERROR" "Redis service is not running"
        exit 1
    else
        log "SUCCESS" "Redis service is running"
    fi
    
    # Check Redis configuration file
    local redis_config="/opt/sysui/config/redis.conf"
    if [[ ! -f "${redis_config}" ]]; then
        log "ERROR" "Redis configuration file not found at ${redis_config}"
        exit 1
    else
        log "SUCCESS" "Redis configuration file exists"
    fi
    
    # Test Redis connection
    if redis-cli ping | grep -q "PONG"; then
        log "SUCCESS" "Redis connection successful"
    else
        log "ERROR" "Failed to connect to Redis"
        exit 1
    fi
}

# Function to test configuration files
test_config_files() {
    log "INFO" "Testing configuration files..."
    
    # Check main configuration file
    local main_config="/opt/sysui/config/config.ini"
    if [[ ! -f "${main_config}" ]]; then
        log "ERROR" "Main configuration file not found at ${main_config}"
        exit 1
    else
        log "SUCCESS" "Main configuration file exists"
    fi
    
    # Check logging configuration file
    local logging_config="/opt/sysui/config/logging.ini"
    if [[ ! -f "${logging_config}" ]]; then
        log "ERROR" "Logging configuration file not found at ${logging_config}"
        exit 1
    else
        log "SUCCESS" "Logging configuration file exists"
    fi
    
    # Check log directory
    if [[ ! -d "/var/log/sysui" ]]; then
        log "ERROR" "Log directory not found at /var/log/sysui"
        exit 1
    else
        log "SUCCESS" "Log directory exists"
    fi
    
    # Check file permissions
    if [[ $(stat -c "%a" "${main_config}") != "600" ]]; then
        log "ERROR" "Incorrect permissions on ${main_config}"
        exit 1
    else
        log "SUCCESS" "File permissions are correct"
    fi
}

# Parse command-line arguments
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main test process
main() {
    log "INFO" "Starting SysUI installation tests..."
    
    # Check if running as root
    check_root
    
    # Run tests
    test_system_packages
    test_python_env
    test_database
    test_redis
    test_config_files
    
    log "SUCCESS" "All tests passed! SysUI is correctly installed."
}

# Run the main function
main