@echo off
echo Setting up SysUI Frontend Development Environment...

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

echo Starting development server...
npm run dev

echo Setup complete!