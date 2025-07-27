#!/bin/bash

# SysUI Installer Script
# This script installs and configures SysUI on Debian/Ubuntu systems

# Set strict error handling
set -e

# Script version
VERSION="1.0.0"

# Default values
VERBOSE=false
NON_INTERACTIVE=false
LOG_FILE="/tmp/sysui_install_$(date +%Y%m%d%H%M%S).log"

# Minimum system requirements
MIN_RAM_MB=2048
MIN_DISK_MB=5120

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage information
show_usage() {
    cat << EOF
SysUI Installer Script v${VERSION}

Usage: $0 [OPTIONS]

Options:
  -h, --help           Display this help message and exit
  -v, --verbose        Enable verbose output
  -n, --non-interactive Run in non-interactive mode (no prompts)
  --version            Display version information and exit

For more information, visit: https://github.com/s3csys/sysui
EOF
}

# Function to display version information
show_version() {
    echo "SysUI Installer Script v${VERSION}"
}

# Function for logging
log() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Always log to file
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"
    
    # Display to console based on verbosity
    if [[ "${VERBOSE}" == true ]] || [[ "${level}" != "DEBUG" ]]; then
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
    fi
}

# Function to check if the script is run as root
check_root() {
    log "DEBUG" "Checking for root privileges"
    if [[ $EUID -ne 0 ]]; then
        log "ERROR" "This script must be run as root or with sudo privileges"
        echo -e "\nTroubleshooting tip: Run the script with sudo: 'sudo $0'"
        exit 1
    fi
    log "DEBUG" "Root privileges confirmed"
}

# Function to check system requirements
check_system_requirements() {
    log "INFO" "Checking system requirements..."
    
    # Check RAM
    local total_ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local total_ram_mb=$((total_ram_kb / 1024))
    
    log "DEBUG" "Total RAM: ${total_ram_mb}MB (Minimum: ${MIN_RAM_MB}MB)"
    
    if [[ ${total_ram_mb} -lt ${MIN_RAM_MB} ]]; then
        log "ERROR" "Insufficient RAM. Found: ${total_ram_mb}MB, Required: ${MIN_RAM_MB}MB"
        echo -e "\nTroubleshooting tip: SysUI requires at least ${MIN_RAM_MB}MB of RAM to function properly."
        exit 1
    fi
    
    # Check disk space
    local install_dir="/opt/sysui"
    local disk_space_kb=$(df -k --output=avail $(dirname "${install_dir}") | tail -n1)
    local disk_space_mb=$((disk_space_kb / 1024))
    
    log "DEBUG" "Available disk space: ${disk_space_mb}MB (Minimum: ${MIN_DISK_MB}MB)"
    
    if [[ ${disk_space_mb} -lt ${MIN_DISK_MB} ]]; then
        log "ERROR" "Insufficient disk space. Found: ${disk_space_mb}MB, Required: ${MIN_DISK_MB}MB"
        echo -e "\nTroubleshooting tip: Free up at least ${MIN_DISK_MB}MB of disk space and try again."
        exit 1
    fi
    
    log "SUCCESS" "System requirements check passed"
}

# Function to detect OS distribution
detect_os() {
    log "INFO" "Detecting operating system..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS_NAME=$ID
        OS_VERSION=$VERSION_ID
        OS_PRETTY_NAME=$PRETTY_NAME
    else
        log "ERROR" "Cannot detect operating system. /etc/os-release file not found."
        echo -e "\nTroubleshooting tip: This script is designed for Debian/Ubuntu systems. Make sure you're running a supported distribution."
        exit 1
    fi
    
    # Check if OS is supported
    if [[ "${OS_NAME}" != "debian" ]] && [[ "${OS_NAME}" != "ubuntu" ]]; then
        log "ERROR" "Unsupported operating system: ${OS_PRETTY_NAME}"
        echo -e "\nTroubleshooting tip: This script supports only Debian and Ubuntu distributions."
        exit 1
    fi
    
    log "SUCCESS" "Detected ${OS_PRETTY_NAME}"
    
    # Source distribution-specific script
    local dist_script=""
    if [[ "${OS_NAME}" == "debian" ]]; then
        dist_script="$(dirname "$0")/debian/packages.sh"
    elif [[ "${OS_NAME}" == "ubuntu" ]]; then
        dist_script="$(dirname "$0")/ubuntu/packages.sh"
    fi
    
    if [[ -f "${dist_script}" ]]; then
        log "DEBUG" "Sourcing distribution-specific script: ${dist_script}"
        . "${dist_script}"
    else
        log "ERROR" "Distribution-specific script not found: ${dist_script}"
        echo -e "\nTroubleshooting tip: Make sure the installer package is complete and includes all necessary files."
        exit 1
    fi
}

# Function to install system dependencies
install_dependencies() {
    log "INFO" "Updating package lists..."
    apt-get update -q || {
        log "ERROR" "Failed to update package lists"
        echo -e "\nTroubleshooting tip: Check your internet connection and try again. If the problem persists, check if your apt sources are correctly configured."
        exit 1
    }
    
    log "INFO" "Installing system dependencies..."
    
    # Install common packages
    local common_packages=("python3" "python3-pip" "python3-venv" "git" "curl" "wget")
    
    # Install distribution-specific packages
    if [[ "${OS_NAME}" == "debian" ]] || [[ "${OS_NAME}" == "ubuntu" ]]; then
        install_db_packages
        install_redis_packages
        install_dev_packages
    fi
    
    # Install common packages
    log "DEBUG" "Installing common packages: ${common_packages[*]}"
    apt-get install -y "${common_packages[@]}" || {
        log "ERROR" "Failed to install common packages"
        echo -e "\nTroubleshooting tip: Try running 'apt-get update' manually and check for errors."
        exit 1
    }
    
    # Verify Python version
    local python_version=$(python3 --version | cut -d' ' -f2)
    log "DEBUG" "Installed Python version: ${python_version}"
    
    # Check if Python version is at least 3.9
    if [[ $(echo "${python_version}" | cut -d. -f1) -lt 3 ]] || \
       [[ $(echo "${python_version}" | cut -d. -f1) -eq 3 && $(echo "${python_version}" | cut -d. -f2) -lt 9 ]]; then
        log "ERROR" "Python version must be at least 3.9. Found: ${python_version}"
        echo -e "\nTroubleshooting tip: Install Python 3.9 or higher manually and try again."
        exit 1
    fi
    
    log "SUCCESS" "System dependencies installed successfully"
}

# Function to set up Python virtual environment
setup_python_env() {
    local app_dir="/opt/sysui"
    local venv_dir="${app_dir}/venv"
    
    log "INFO" "Setting up Python virtual environment..."
    
    # Create application directory if it doesn't exist
    if [[ ! -d "${app_dir}" ]]; then
        log "DEBUG" "Creating application directory: ${app_dir}"
        mkdir -p "${app_dir}" || {
            log "ERROR" "Failed to create application directory: ${app_dir}"
            echo -e "\nTroubleshooting tip: Check if you have permission to create directories in /opt."
            exit 1
        }
    fi
    
    # Check if virtual environment already exists
    if [[ -d "${venv_dir}" ]]; then
        log "WARNING" "Python virtual environment already exists at ${venv_dir}"
        
        if [[ "${NON_INTERACTIVE}" == false ]]; then
            read -p "Do you want to recreate the virtual environment? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log "INFO" "Skipping virtual environment creation"
                return 0
            fi
        else
            log "INFO" "Skipping virtual environment recreation in non-interactive mode"
            return 0
        fi
        
        log "DEBUG" "Removing existing virtual environment"
        rm -rf "${venv_dir}"
    fi
    
    # Create virtual environment
    log "DEBUG" "Creating Python virtual environment at ${venv_dir}"
    python3 -m venv "${venv_dir}" || {
        log "ERROR" "Failed to create Python virtual environment"
        echo -e "\nTroubleshooting tip: Make sure python3-venv package is installed."
        exit 1
    }
    
    # Activate virtual environment and install dependencies
    log "DEBUG" "Installing Python dependencies"
    
    # Check if requirements.txt exists
    local requirements_file="${app_dir}/requirements.txt"
    
    # If requirements.txt doesn't exist, create a basic one
    if [[ ! -f "${requirements_file}" ]]; then
        log "WARNING" "Requirements file not found, creating a basic one"
        cat > "${requirements_file}" << EOF
fastapi>=0.68.0,<0.69.0
uvicorn>=0.15.0,<0.16.0
sqlalchemy>=1.4.23,<1.5.0
pydantic>=1.8.2,<1.9.0
python-jose[cryptography]>=3.3.0,<3.4.0
passlib[bcrypt]>=1.7.4,<1.8.0
python-multipart>=0.0.5,<0.0.6
mysqlclient>=2.0.3,<2.1.0
redis>=4.0.2,<4.1.0
rq>=1.10.0,<1.11.0
pyotp>=2.6.0,<2.7.0
EOF
    fi
    
    # Install dependencies
    "${venv_dir}/bin/pip" install --upgrade pip || {
        log "ERROR" "Failed to upgrade pip"
        echo -e "\nTroubleshooting tip: Check your internet connection and try again."
        exit 1
    }
    
    "${venv_dir}/bin/pip" install -r "${requirements_file}" || {
        log "ERROR" "Failed to install Python dependencies"
        echo -e "\nTroubleshooting tip: Check the requirements.txt file for errors or incompatible packages."
        exit 1
    }
    
    log "SUCCESS" "Python virtual environment set up successfully"
}

# Function to set up database
setup_database() {
    log "INFO" "Setting up database..."
    
    # Check if MySQL/MariaDB is installed and running
    if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mariadb; then
        log "ERROR" "MySQL/MariaDB service is not running"
        echo -e "\nTroubleshooting tip: Start the database service with 'systemctl start mysql' or 'systemctl start mariadb'."
        exit 1
    fi
    
    # Generate a secure password if in non-interactive mode
    local db_name="sysui"
    local db_user="sysui"
    local db_password=""
    
    if [[ "${NON_INTERACTIVE}" == true ]]; then
        db_password=$(openssl rand -base64 12)
    else
        # Prompt for database details
        read -p "Enter database name [${db_name}]: " input_db_name
        db_name=${input_db_name:-$db_name}
        
        read -p "Enter database user [${db_user}]: " input_db_user
        db_user=${input_db_user:-$db_user}
        
        read -s -p "Enter database password (leave empty to generate): " input_db_password
        echo
        
        if [[ -z "${input_db_password}" ]]; then
            db_password=$(openssl rand -base64 12)
            log "INFO" "Generated database password: ${db_password}"
        else
            db_password="${input_db_password}"
        fi
    fi
    
    # Check if database already exists
    if mysql -e "USE ${db_name}" 2>/dev/null; then
        log "WARNING" "Database '${db_name}' already exists"
        
        if [[ "${NON_INTERACTIVE}" == false ]]; then
            read -p "Do you want to drop and recreate the database? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log "INFO" "Skipping database recreation"
                return 0
            fi
            
            # Drop database
            log "DEBUG" "Dropping existing database '${db_name}'"
            mysql -e "DROP DATABASE ${db_name}" || {
                log "ERROR" "Failed to drop database '${db_name}'"
                echo -e "\nTroubleshooting tip: Make sure you have sufficient privileges to drop databases."
                exit 1
            }
        else
            log "INFO" "Skipping database recreation in non-interactive mode"
            return 0
        fi
    fi
    
    # Create database and user
    log "DEBUG" "Creating database '${db_name}'"
    mysql -e "CREATE DATABASE ${db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" || {
        log "ERROR" "Failed to create database '${db_name}'"
        echo -e "\nTroubleshooting tip: Make sure you have sufficient privileges to create databases."
        exit 1
    }
    
    # Check if user already exists
    if mysql -e "SELECT User FROM mysql.user WHERE User='${db_user}'" | grep -q "${db_user}"; then
        log "DEBUG" "User '${db_user}' already exists, updating password"
        mysql -e "ALTER USER '${db_user}'@'localhost' IDENTIFIED BY '${db_password}'" || {
            log "ERROR" "Failed to update password for user '${db_user}'"
            echo -e "\nTroubleshooting tip: Make sure you have sufficient privileges to modify users."
            exit 1
        }
    else
        log "DEBUG" "Creating user '${db_user}'"
        mysql -e "CREATE USER '${db_user}'@'localhost' IDENTIFIED BY '${db_password}'" || {
            log "ERROR" "Failed to create user '${db_user}'"
            echo -e "\nTroubleshooting tip: Make sure you have sufficient privileges to create users."
            exit 1
        }
    fi
    
    # Grant privileges
    log "DEBUG" "Granting privileges to user '${db_user}'"
    mysql -e "GRANT ALL PRIVILEGES ON ${db_name}.* TO '${db_user}'@'localhost'" || {
        log "ERROR" "Failed to grant privileges to user '${db_user}'"
        echo -e "\nTroubleshooting tip: Make sure you have sufficient privileges to grant permissions."
        exit 1
    }
    
    mysql -e "FLUSH PRIVILEGES" || {
        log "ERROR" "Failed to flush privileges"
        echo -e "\nTroubleshooting tip: Make sure you have sufficient privileges to flush privileges."
        exit 1
    }
    
    # Save database configuration
    local config_dir="/opt/sysui/config"
    mkdir -p "${config_dir}"
    
    cat > "${config_dir}/database.conf" << EOF
[database]
type = mysql
host = localhost
port = 3306
name = ${db_name}
user = ${db_user}
password = ${db_password}
EOF
    
    # Set secure permissions
    chmod 600 "${config_dir}/database.conf"
    chown root:root "${config_dir}/database.conf"
    
    log "SUCCESS" "Database setup completed successfully"
}

# Function to set up Redis
setup_redis() {
    log "INFO" "Setting up Redis..."
    
    # Check if Redis is installed and running
    if ! systemctl is-active --quiet redis-server; then
        log "WARNING" "Redis service is not running"
        
        # Try to start Redis
        log "DEBUG" "Attempting to start Redis service"
        systemctl start redis-server || {
            log "ERROR" "Failed to start Redis service"
            echo -e "\nTroubleshooting tip: Install Redis with 'apt-get install redis-server' and start it with 'systemctl start redis-server'."
            exit 1
        }
    fi
    
    # Test Redis connection
    if ! redis-cli ping > /dev/null 2>&1; then
        log "ERROR" "Cannot connect to Redis server"
        echo -e "\nTroubleshooting tip: Make sure Redis is installed and running. Check Redis configuration at /etc/redis/redis.conf."
        exit 1
    fi
    
    # Save Redis configuration
    local config_dir="/opt/sysui/config"
    mkdir -p "${config_dir}"
    
    cat > "${config_dir}/redis.conf" << EOF
[redis]
host = localhost
port = 6379
db = 0
EOF
    
    # Set secure permissions
    chmod 600 "${config_dir}/redis.conf"
    chown root:root "${config_dir}/redis.conf"
    
    log "SUCCESS" "Redis setup completed successfully"
}

# Function to generate configuration files
generate_config() {
    log "INFO" "Generating configuration files..."
    
    local config_dir="/opt/sysui/config"
    mkdir -p "${config_dir}"
    
    # Generate JWT secret
    local jwt_secret=$(openssl rand -hex 32)
    
    # Create main configuration file
    cat > "${config_dir}/config.ini" << EOF
[app]
name = SysUI
debug = false
secret_key = ${jwt_secret}
allow_origins = http://localhost:8000,http://localhost:3000

[security]
enable_2fa = true
failed_login_attempts = 5
password_min_length = 12
password_require_uppercase = true
password_require_lowercase = true
password_require_numbers = true
password_require_special = true
EOF
    
    # Set secure permissions
    chmod 600 "${config_dir}/config.ini"
    chown root:root "${config_dir}/config.ini"
    
    # Create logging configuration
    cat > "${config_dir}/logging.ini" << EOF
[loggers]
keys = root

[handlers]
keys = console, file

[formatters]
keys = standard

[logger_root]
level = INFO
handlers = console, file
qualname = sysui
propagation = 0

[handler_console]
class = StreamHandler
level = INFO
formatter = standard
args = (sys.stdout,)

[handler_file]
class = handlers.RotatingFileHandler
level = INFO
formatter = standard
args = ('/var/log/sysui/app.log', 'a', 10485760, 5)

[formatter_standard]
format = %(asctime)s [%(levelname)s] %(name)s: %(message)s
datefmt = %Y-%m-%d %H:%M:%S
EOF
    
    # Create log directory
    mkdir -p /var/log/sysui
    chmod 755 /var/log/sysui
    
    log "SUCCESS" "Configuration files generated successfully"
}

# Function to display summary and next steps
display_summary() {
    log "INFO" "Installation completed successfully!"
    
    cat << EOF

${GREEN}SysUI Installation Summary${NC}
---------------------------

${BLUE}Installed Components:${NC}
- Python environment: /opt/sysui/venv
- Configuration files: /opt/sysui/config
- Log files: /var/log/sysui

${BLUE}Next Steps:${NC}
1. Deploy your SysUI application code to /opt/sysui
2. Configure your web server (Nginx/Apache) to proxy requests to the FastAPI application
3. Start the application with: /opt/sysui/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000

${BLUE}For more information:${NC}
- Installation log: ${LOG_FILE}
- Documentation: https://github.com/s3csys/sysui/docs

Thank you for installing SysUI!
EOF
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
            show_version
            exit 0
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main installation process
main() {
    log "INFO" "Starting SysUI installation..."
    
    # Check if running as root
    check_root
    
    # Check system requirements
    check_system_requirements
    
    # Detect OS distribution
    detect_os
    
    # Install dependencies
    install_dependencies
    
    # Set up Python virtual environment
    setup_python_env
    
    # Set up database
    setup_database
    
    # Set up Redis
    setup_redis
    
    # Generate configuration files
    generate_config
    
    # Display summary
    display_summary
    
    log "SUCCESS" "SysUI installation completed successfully!"
}

# Run the main function
main