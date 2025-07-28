@echo off
echo SysUI Frontend Installation Script

:: Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo npm is not installed. Please install Node.js and npm from https://nodejs.org/
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo Setting up SysUI Frontend Environment...

echo Installing dependencies...
npm install

echo Setting up environment variables...
if not exist .env (
    echo VITE_API_URL=http://localhost:8000 > .env
    echo VITE_APP_NAME=SysUI >> .env
    echo .env file created with default settings
) else (
    echo .env file already exists, skipping
)

:: Check for installation mode
if "%1"=="prod" (
    echo Building for production...
    npm run build
    echo Production build complete! Files are in the dist/ directory.
    
    :: Optional: Preview the production build
    set /p PREVIEW=Do you want to preview the production build? (y/n): 
    if /i "%PREVIEW%"=="y" (
        npm run preview
    )
) else (
    echo Starting development server...
    npm run dev
)

echo Setup complete!