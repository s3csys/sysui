#!/bin/bash

# Debian-specific package installation functions

# Function to install database packages
install_db_packages() {
    log "INFO" "Installing database packages for Debian..."
    
    # Check if MySQL or MariaDB is already installed
    if dpkg -l | grep -q "mysql-server\|mariadb-server"; then
        log "DEBUG" "MySQL/MariaDB is already installed"
    else
        # Install MariaDB by default on Debian
        log "DEBUG" "Installing MariaDB server"
        apt-get install -y mariadb-server || {
            log "ERROR" "Failed to install MariaDB server"
            echo -e "\nTroubleshooting tip: Try running 'apt-get update' and then retry the installation."
            exit 1
        }
        
        # Secure MariaDB installation if in interactive mode
        if [[ "${NON_INTERACTIVE}" == false ]]; then
            log "INFO" "Running MariaDB secure installation..."
            log "WARNING" "You will be prompted to set the root password and other security options"
            mysql_secure_installation
        else
            log "WARNING" "Skipping MariaDB secure installation in non-interactive mode"
            log "WARNING" "It is recommended to run 'mysql_secure_installation' manually after the script completes"
        fi
    fi
    
    # Install MySQL client and Python connector
    log "DEBUG" "Installing MySQL client and Python connector"
    apt-get install -y mariadb-client python3-dev default-libmysqlclient-dev build-essential || {
        log "ERROR" "Failed to install MySQL client and development packages"
        echo -e "\nTroubleshooting tip: Try installing the packages individually to identify which one is failing."
        exit 1
    }
    
    log "SUCCESS" "Database packages installed successfully"
}

# Function to install Redis packages
install_redis_packages() {
    log "INFO" "Installing Redis for Debian..."
    
    # Check if Redis is already installed
    if dpkg -l | grep -q "redis-server"; then
        log "DEBUG" "Redis is already installed"
    else
        log "DEBUG" "Installing Redis server"
        apt-get install -y redis-server || {
            log "ERROR" "Failed to install Redis server"
            echo -e "\nTroubleshooting tip: Try running 'apt-get update' and then retry the installation."
            exit 1
        }
        
        # Enable Redis to start on boot
        systemctl enable redis-server
    fi
    
    log "SUCCESS" "Redis installed successfully"
}

# Function to install development tools
install_dev_packages() {
    log "INFO" "Installing development tools for Debian..."
    
    # Install development packages
    local dev_packages=("build-essential" "libssl-dev" "libffi-dev" "python3-dev")
    
    log "DEBUG" "Installing development packages: ${dev_packages[*]}"
    apt-get install -y "${dev_packages[@]}" || {
        log "ERROR" "Failed to install development packages"
        echo -e "\nTroubleshooting tip: Try installing the packages individually to identify which one is failing."
        exit 1
    }
    
    log "SUCCESS" "Development tools installed successfully"
}