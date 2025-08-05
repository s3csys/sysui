# SysUI Installation Guide

This guide provides instructions for installing and setting up the SysUI application, which consists of a FastAPI backend and a React frontend.

## System Requirements

### Windows
- Windows 10 or later
- Python 3.9 or higher
- Node.js 16 or higher
- npm 7 or higher
- MySQL/MariaDB (optional, can be run in Docker)
- Redis (optional, can be run in Docker)

### Linux (Debian/Ubuntu)
- Python 3.9 or higher
- Node.js 16 or higher
- npm 7 or higher
- MySQL/MariaDB (optional, can be run in Docker)
- Redis (optional, can be run in Docker)

## Quick Installation

### Windows

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the SysUI directory
3. Run the unified installation script:

```
install.bat
```

### Linux (Debian/Ubuntu)

1. Open a terminal
2. Navigate to the SysUI directory
3. Make the installation script executable:

```bash
chmod +x install.sh
```

4. Run the unified installation script:

```bash
./install.sh
```

## Manual Installation

If you prefer to install the components separately, follow these steps:

### Backend Setup

#### Windows

1. Navigate to the backend directory:

```
cd backend
```

2. Run the setup script:

```
setup_dev.bat
```

#### Linux

1. Navigate to the backend directory:

```bash
cd backend
```

2. Make the setup script executable:

```bash
chmod +x setup_dev.sh
```

3. Run the setup script:

```bash
./setup_dev.sh
```

### Frontend Setup

#### Windows

1. Navigate to the frontend directory:

```
cd frontend
```

2. Run the installation script:

```
install.bat
```

#### Linux

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Make the installation script executable:

```bash
chmod +x install.sh
```

3. Run the installation script:

```bash
./install.sh
```

## Post-Installation

After installation, you need to start both the backend and frontend services:

### Starting the Backend

#### Windows

1. Navigate to the backend directory
2. Activate the virtual environment:

```
venv\Scripts\activate
```

3. Run the application:

```
python run.py
```

#### Linux

1. Navigate to the backend directory
2. Activate the virtual environment:

```bash
source venv/bin/activate
```

3. Run the application:

```bash
python run.py
```

### Starting the Frontend

#### Windows/Linux

1. Navigate to the frontend directory
2. Start the development server:

```bash
npm run dev
```

## Configuration

### Backend Configuration

The backend configuration is stored in the `.env` file in the backend directory. You can modify this file to change the following settings:

- API settings (endpoints, server details)
- Security settings (JWT secret, token expiration)
- Database connection (MySQL/MariaDB)
- Redis connection
- Rate limiting
- Two-factor authentication
- Email settings

### Frontend Configuration

The frontend configuration is stored in the `.env` file in the frontend directory. You can modify this file to change the following settings:

- API URL (backend server address)
- Application name
- Server configuration (host, port, allowed hosts)

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Make sure MySQL/MariaDB is running
   - Check the database credentials in the `.env` file
   - Ensure the database exists and the user has appropriate permissions

2. **Redis Connection Error**
   - Make sure Redis is running
   - Check the Redis connection settings in the `.env` file

3. **Node.js/npm Issues**
   - Make sure Node.js and npm are installed and in your PATH
   - Try clearing the npm cache: `npm cache clean --force`
   - Reinstall dependencies: `rm -rf node_modules && npm install`

4. **Python Environment Issues**
   - Make sure Python 3.9+ is installed and in your PATH
   - Try recreating the virtual environment
   - Reinstall dependencies: `pip install -r requirements.txt`

### Installation Logs

- Windows: Check the log file in the `%TEMP%` directory
- Linux: Check the log file in the `/tmp` directory

## Additional Resources

- Backend Documentation: See `backend/README.md`
- Frontend Documentation: See `frontend/README.md`
- API Documentation: Available at `http://localhost:8000/docs` when the backend is running