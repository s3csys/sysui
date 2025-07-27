@echo off
REM Setup development environment for SysUI backend on Windows

echo Setting up SysUI backend development environment...

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Generate a secret key
echo Generating a secret key...
for /f "tokens=*" %%a in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%a

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    
    echo Please update the .env file with your database and email settings.
    echo Don't forget to set SECRET_KEY=%SECRET_KEY%
)

REM Start Docker services if Docker is available
docker-compose --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Starting Docker services...
    docker-compose up -d
) else (
    echo Docker Compose not found. Please install Docker and Docker Compose to use the containerized services.
    echo You'll need to set up MySQL and Redis manually.
)

echo.
echo Setup complete! Next steps:
echo 1. Update your .env file with your database and email settings
echo 2. Run 'alembic upgrade head' to initialize the database
echo 3. Run 'python -m scripts.init_db' to create an admin user
echo 4. Run 'python run.py' to start the application
echo.
echo For more information, see the README.md file.

pause