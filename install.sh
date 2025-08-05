#!/bin/bash

# SysUI Unified Installation Script
# This script sets up both the frontend and backend components of SysUI

set -e

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Set variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"
LOG_FILE="/tmp/sysui_install_$(date +%Y%m%d%H%M%S).log"

# Function to display usage information
show_usage() {
    cat << EOF
SysUI Unified Installation Script

Usage: $0 [OPTIONS]

Options:
  -h, --help           Display this help message and exit
  -v, --verbose        Enable verbose output
  -n, --non-interactive Run in non-interactive mode (no prompts)
  --version            Display version information and exit

For more information, visit: https://github.com/s3csys/sysui
EOF
}

# Function for logging
log() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Always log to file
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"
    
    # Display to console
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
    log "INFO" "Checking for root privileges"
    if [[ $EUID -ne 0 ]]; then
        log "WARNING" "This script is not being run as root"
        log "WARNING" "Some operations may fail without root privileges"
        
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "ERROR" "Installation aborted by user"
            exit 1
        fi
    else
        log "INFO" "Root privileges confirmed"
    fi
}

# Function to check system requirements
check_system_requirements() {
    log "INFO" "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python 3 is not installed"
        echo -e "\nTroubleshooting tip: Install Python 3.9 or higher with your package manager."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log "INFO" "Python version: ${PYTHON_VERSION}"
    
    # Check if Python version is at least 3.9
    if [[ $(echo "${PYTHON_VERSION}" | cut -d. -f1) -lt 3 ]] || \
       [[ $(echo "${PYTHON_VERSION}" | cut -d. -f1) -eq 3 && $(echo "${PYTHON_VERSION}" | cut -d. -f2) -lt 9 ]]; then
        log "ERROR" "Python version must be at least 3.9. Found: ${PYTHON_VERSION}"
        echo -e "\nTroubleshooting tip: Install Python 3.9 or higher."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log "ERROR" "Node.js is not installed"
        echo -e "\nTroubleshooting tip: Install Node.js with your package manager or from https://nodejs.org/"
        exit 1
    fi
    
    # Check Node.js version
    NODE_VERSION=$(node --version)
    log "INFO" "Node.js version: ${NODE_VERSION}"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log "ERROR" "npm is not installed"
        echo -e "\nTroubleshooting tip: Install npm with your package manager or reinstall Node.js."
        exit 1
    fi
    
    # Check MySQL/MariaDB (optional)
    if command -v mysql &> /dev/null; then
        log "INFO" "MySQL/MariaDB is installed"
        MYSQL_INSTALLED=true
    else
        log "WARNING" "MySQL/MariaDB is not installed"
        log "WARNING" "You will need to configure the database connection manually"
        MYSQL_INSTALLED=false
    fi
    
    log "SUCCESS" "System requirements check passed"
}

# Function to setup backend
setup_backend() {
    log "INFO" "Setting up backend..."
    
    cd "${BACKEND_DIR}"
    
    # Run the backend setup script
    log "INFO" "Running backend setup script..."
    if [[ -f "setup_dev.sh" ]]; then
        bash "setup_dev.sh"
        if [[ $? -ne 0 ]]; then
            log "ERROR" "Backend setup failed"
            echo -e "\nTroubleshooting tip: Check the error messages above."
            exit 1
        fi
    else
        log "ERROR" "Backend setup script not found: ${BACKEND_DIR}/setup_dev.sh"
        exit 1
    fi
    
    log "SUCCESS" "Backend setup completed successfully"
}

# Function to setup frontend
setup_frontend() {
    log "INFO" "Setting up frontend..."
    
    cd "${FRONTEND_DIR}"
    
    # Run the frontend setup script
    log "INFO" "Running frontend setup script..."
    if [[ -f "install.sh" ]]; then
        bash "install.sh"
        if [[ $? -ne 0 ]]; then
            log "ERROR" "Frontend setup failed"
            echo -e "\nTroubleshooting tip: Check the error messages above."
            exit 1
        fi
    else
        log "ERROR" "Frontend setup script not found: ${FRONTEND_DIR}/install.sh"
        exit 1
    fi
    
    log "SUCCESS" "Frontend setup completed successfully"
}

# Function to display summary
display_summary() {
    log "INFO" "Installation completed successfully!"
    
    cat << EOF

${GREEN}SysUI Installation Summary${NC}
---------------------------

${BLUE}Installed Components:${NC}
- Backend: ${BACKEND_DIR}
- Frontend: ${FRONTEND_DIR}

${BLUE}Next Steps:${NC}
1. Start the backend:
   cd ${BACKEND_DIR}
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python run.py

2. Start the frontend:
   cd ${FRONTEND_DIR}
   npm run dev

${BLUE}For more information:${NC}
- Installation log: ${LOG_FILE}
- Documentation: https://github.com/s3csys/sysui

Thank you for installing SysUI!
EOF
}

# Main installation process
main() {
    log "INFO" "Starting SysUI unified installation..."
    
    # Check if running as root
    check_root
    
    # Check system requirements
    check_system_requirements
    
    # Setup backend
    setup_backend
    
    # Setup frontend
    setup_frontend
    
    # Display summary
    display_summary
    
    log "SUCCESS" "SysUI unified installation completed successfully!"
}

# Parse command-line arguments
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
        -n|--non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        --version)
            echo "SysUI Unified Installation Script v1.0.0"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run the main function
main