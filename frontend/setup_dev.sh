#!/bin/bash

echo "Setting up SysUI Frontend Development Environment..."

echo "Installing dependencies..."
npm install

echo "Setting up environment variables..."
if [ ! -f .env ]; then
    echo "VITE_API_URL=http://localhost:8000" > .env
    echo "VITE_APP_NAME=SysUI" >> .env
    echo ".env file created with default settings"
else
    echo ".env file already exists, skipping"
fi

echo "Starting development server..."
npm run dev

echo "Setup complete!"