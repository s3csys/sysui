#!/bin/bash

# Ubuntu-specific package installation functions

# Function to install database packages
install_db_packages() {
    log "INFO" "Installing database packages for Ubuntu..."
    
    # Check if MySQL or MariaDB is already installed
    if dpkg -l | grep -q "mysql-server\|mariadb-server"; then
        log "DEBUG" "MySQL/MariaDB is already installed"
    else
        # Install MySQL by default on Ubuntu
        log "DEBUG" "Installing MySQL server"
        
        # Set non-interactive installation for MySQL
        if [[ "${NON_INTERACTIVE}" == true ]]; then
            # Set root password to random value in non-interactive mode
            local mysql_root_password=$(openssl rand -base64 12)
            log "INFO" "Generated MySQL root password: ${mysql_root_password}"
            
            # Pre-configure MySQL root password
            debconf-set-selections <<< "mysql-server mysql-server/root_password password ${mysql_root_password}"
            debconf-set-selections <<< "mysql-server mysql-server/root_password_again password ${mysql_root_password}"
        fi
        
        apt-get install -y mysql-server || {
            log "ERROR" "Failed to install MySQL server"
            echo -e "\nTroubleshooting tip: Try running 'apt-get update' and then retry the installation."
            exit 1
        }
        
        # Secure MySQL installation if in interactive mode
        if [[ "${NON_INTERACTIVE}" == false ]]; then
            log "INFO" "Running MySQL secure installation..."
            log "WARNING" "You will be prompted to set the root password and other security options"
            mysql_secure_installation
        else
            log "WARNING" "Skipping MySQL secure installation in non-interactive mode"
            log "WARNING" "It is recommended to run 'mysql_secure_installation' manually after the script completes"
        fi
    fi
    
    # Install MySQL client and Python connector
    log "DEBUG" "Installing MySQL client and Python connector"
    apt-get install -y mysql-client python3-dev default-libmysqlclient-dev build-essential || {
        log "ERROR" "Failed to install MySQL client and development packages"
        echo -e "\nTroubleshooting tip: Try installing the packages individually to identify which one is failing."
        exit 1
    }
    
    log "SUCCESS" "Database packages installed successfully"
}

# Function to install Redis packages
install_redis_packages() {
    log "INFO" "Installing Redis for Ubuntu..."
    
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
        
        # Configure Redis to accept connections from localhost only
        sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/g' /etc/redis/redis.conf
        
        # Enable Redis to start on boot
        systemctl enable redis-server
        
        # Restart Redis to apply configuration changes
        systemctl restart redis-server
    fi
    
    log "SUCCESS" "Redis installed successfully"
}

# Function to install development tools
install_dev_packages() {
    log "INFO" "Installing development tools for Ubuntu..."
    
    # Install development packages
    local dev_packages=("build-essential" "libssl-dev" "libffi-dev" "python3-dev" "python3.9" "python3.9-venv" "python3.9-dev")
    
    # Check if Python 3.9 is available in the repositories
    if ! apt-cache search python3.9 | grep -q "python3.9"; then
        log "WARNING" "Python 3.9 not found in standard repositories"
        log "INFO" "Adding deadsnakes PPA to install Python 3.9"
        
        # Install software-properties-common if not already installed
        apt-get install -y software-properties-common || {
            log "ERROR" "Failed to install software-properties-common"
            echo -e "\nTroubleshooting tip: Try running 'apt-get update' and then retry the installation."
            exit 1
        }
        
        # Add deadsnakes PPA
        add-apt-repository -y ppa:deadsnakes/ppa || {
            log "ERROR" "Failed to add deadsnakes PPA"
            echo -e "\nTroubleshooting tip: Check your internet connection and try again."
            exit 1
        }
        
        # Update package lists
        apt-get update -q
    fi
    
    log "DEBUG" "Installing development packages: ${dev_packages[*]}"
    apt-get install -y "${dev_packages[@]}" || {
        log "ERROR" "Failed to install development packages"
        echo -e "\nTroubleshooting tip: Try installing the packages individually to identify which one is failing."
        exit 1
    }
    
    # Set Python 3.9 as the default Python 3 version if installed
    if command -v python3.9 &> /dev/null; then
        log "DEBUG" "Setting Python 3.9 as the default Python 3 version"
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
    fi
    
    log "SUCCESS" "Development tools installed successfully"
}