#!/bin/bash

echo "SysUI Frontend Installation Script"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Installing Node.js and npm..."
    # This is a basic approach - in a real environment, you might want to use nvm or a specific version
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y nodejs npm
    elif command -v yum &> /dev/null; then
        # RHEL/CentOS/Fedora
        sudo yum install -y nodejs npm
    elif command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew install node
    else
        echo "Unable to install Node.js and npm automatically. Please install them manually."
        exit 1
    fi
fi

echo "Setting up SysUI Frontend Environment..."

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

# Check for installation mode
if [ "$1" = "prod" ]; then
    echo "Building for production..."
    npm run build
    echo "Production build complete! Files are in the dist/ directory."
    
    # Optional: Preview the production build
    read -p "Do you want to preview the production build? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm run preview
    fi
else
    echo "Starting development server..."
    npm run dev
fi

echo "Setup complete!"