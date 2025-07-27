#!/bin/bash

# Setup development environment for SysUI backend

set -e

echo "Setting up SysUI backend development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Generate a secret key
echo "Generating a secret key..."
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Replace the placeholder secret key with a real one
    sed -i "s/SECRET_KEY=your-secret-key/SECRET_KEY=$SECRET_KEY/g" .env
    
    echo "Please update the .env file with your database and email settings."
fi

# Start Docker services if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "Starting Docker services..."
    docker-compose up -d
else
    echo "Docker Compose not found. Please install Docker and Docker Compose to use the containerized services."
    echo "You'll need to set up MySQL and Redis manually."
fi

echo ""
echo "Setup complete! Next steps:"
echo "1. Update your .env file with your database and email settings"
echo "2. Run 'alembic upgrade head' to initialize the database"
echo "3. Run 'python -m scripts.init_db' to create an admin user"
echo "4. Run 'python run.py' to start the application"
echo ""
echo "For more information, see the README.md file."