@echo off
REM SysUI Unified Installation Script for Windows
REM This script sets up both the frontend and backend components of SysUI

echo ===================================================
echo SysUI Unified Installation Script
echo ===================================================
echo.

SETLOCAL EnableDelayedExpansion

REM Set variables
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
set "LOG_FILE=%TEMP%\sysui_install_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log"

REM Check if Python is installed
echo Checking for Python installation...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9 or higher from https://www.python.org/downloads/
    echo After installation, make sure to check "Add Python to PATH" option.
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if !PYTHON_MAJOR! LSS 3 (
    echo ERROR: Python version must be at least 3.9. Found: !PYTHON_VERSION!
    echo Please install Python 3.9 or higher.
    exit /b 1
)

if !PYTHON_MAJOR! EQU 3 if !PYTHON_MINOR! LSS 9 (
    echo ERROR: Python version must be at least 3.9. Found: !PYTHON_VERSION!
    echo Please install Python 3.9 or higher.
    exit /b 1
)

echo Python !PYTHON_VERSION! detected.

REM Check if Node.js is installed
echo Checking for Node.js installation...
node --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo After installation, make sure to restart your command prompt.
    exit /b 1
)

REM Check Node.js version
for /f "tokens=1" %%V in ('node --version') do set NODE_VERSION=%%V
echo Node.js !NODE_VERSION! detected.

REM Check if npm is installed
echo Checking for npm installation...
npm --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm is not installed or not in PATH.
    echo Please reinstall Node.js from https://nodejs.org/
    exit /b 1
)

REM Check if MySQL is installed (optional)
echo Checking for MySQL installation...
mysql --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: MySQL is not installed or not in PATH.
    echo You will need to configure the database connection manually.
    echo We recommend installing MySQL from https://dev.mysql.com/downloads/installer/
    set MYSQL_INSTALLED=false
) else (
    set MYSQL_INSTALLED=true
    echo MySQL detected.
)

REM Setup Backend
echo.
echo ===================================================
echo Setting up Backend
echo ===================================================
echo.

cd "%BACKEND_DIR%"

REM Run the backend setup script
echo Running backend setup script...
call setup_dev.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Backend setup failed.
    echo Please check the error messages above.
    exit /b 1
)

REM Setup Frontend
echo.
echo ===================================================
echo Setting up Frontend
echo ===================================================
echo.

cd "%FRONTEND_DIR%"

REM Run the frontend setup script
echo Running frontend setup script...
call install.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Frontend setup failed.
    echo Please check the error messages above.
    exit /b 1
)

REM Installation complete
echo.
echo ===================================================
echo SysUI Installation Complete!
echo ===================================================
echo.
echo Backend: %BACKEND_DIR%
echo Frontend: %FRONTEND_DIR%
echo.
echo To start the backend:
echo   1. Navigate to %BACKEND_DIR%
echo   2. Activate the virtual environment: .\venv\Scripts\activate
echo   3. Run the application: python run.py
echo.
echo To start the frontend:
echo   1. Navigate to %FRONTEND_DIR%
echo   2. Run: npm run dev
echo.
echo Thank you for installing SysUI!

ENDLOCAL