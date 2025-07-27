# SysUI Installer Scripts

This directory contains scripts for installing and configuring SysUI on Debian/Ubuntu systems.

## Overview

The installer scripts automate the process of setting up SysUI, including:

- Installing system dependencies
- Setting up Python virtual environment
- Configuring database (MySQL/MariaDB)
- Setting up Redis
- Generating secure configuration files

## Files

- `install.sh` - Main installer script
- `debian/packages.sh` - Debian-specific package installation
- `ubuntu/packages.sh` - Ubuntu-specific package installation
- `test_install.sh` - Test script to verify installation

## Usage

### Installation

To install SysUI, run the following command as root or with sudo:

```bash
sudo ./install.sh
```

### Command-line Options

The installer script supports the following options:

- `-h, --help` - Display help information
- `-v, --verbose` - Enable verbose output
- `-n, --non-interactive` - Run in non-interactive mode (no prompts)
- `--version` - Display version information

### Examples

1. Standard installation with prompts:
   ```bash
   sudo ./install.sh
   ```

2. Verbose installation:
   ```bash
   sudo ./install.sh -v
   ```

3. Non-interactive installation (for automated deployments):
   ```bash
   sudo ./install.sh -n
   ```

## Testing

To verify that SysUI is correctly installed, run the test script:

```bash
sudo ./test_install.sh
```

The test script checks:

- System packages
- Python environment
- Database connection
- Redis connection
- Configuration files

## System Requirements

- Debian or Ubuntu Linux distribution
- Minimum 2GB RAM
- Minimum 5GB free disk space
- Root or sudo access

## Troubleshooting

If you encounter issues during installation:

1. Check the installation log at `/tmp/sysui_install_*.log`
2. Run the installer with the `-v` option for verbose output
3. Run the test script to identify specific issues

## Security Notes

- The installer generates secure random passwords for the database
- Configuration files are created with restricted permissions (600)
- JWT secrets are generated using cryptographically secure methods

## License

See the main project license file for details.