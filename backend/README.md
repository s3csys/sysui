# SysUI Backend

This is the backend for the SysUI application, built with FastAPI and providing a secure authentication system.

## Features

- User registration with email verification
- Secure login with JWT authentication
- Two-Factor Authentication (2FA) using TOTP
- Role-based access control (admin, viewer, editor roles)
- Secure password storage with bcrypt hashing
- Token refresh mechanism
- Rate limiting for authentication endpoints
- Session management (view active sessions, logout from all devices)

## Prerequisites

- Python 3.9+
- MySQL database
- Redis (optional, for rate limiting)

## Installation

1. Clone the repository

```bash
git clone https://github.com/s3csys/sysui.git
cd sysui/backend
```

2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory with the following variables:

```
# API settings
API_V1_STR=/api/v1
SERVER_NAME=SysUI
SERVER_HOST=http://localhost
BACKEND_CORS_ORIGINS=["http://localhost","http://localhost:8080","http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key  # Generate a secure random key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7 days
ALGORITHM=HS256

# Database
DATABASE_URI=mysql+mysqlconnector://user:password@localhost/sysui

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Rate limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=60

# 2FA
TOTP_ISSUER=SysUI

# Email
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.example.com
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@example.com
EMAILS_FROM_NAME=SysUI
EMAIL_RESET_TOKEN_EXPIRE_HOURS=48
EMAIL_TEMPLATES_DIR=app/email-templates
```

5. Initialize the database

```bash
alembic upgrade head
```

## Running the Application

You can run the application using the provided run script or Makefile:

```bash
# Using the run script
python run.py

# Using the Makefile
make run
```

The API will be available at http://localhost:8000 by default.

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Tools

The project includes several utility scripts to help with development:

### Database Management

```bash
# Initialize the database with migrations
make migrate-up

# Create a new migration
make migrate message="your migration description"

# Initialize the database with a default admin user
make init-db
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Or use the test script directly
python -m scripts.run_tests --cov --html
```

### Security

```bash
# Generate a secure secret key for your .env file
python -m scripts.generate_secret_key

# Generate a self-signed SSL certificate for development
python -m scripts.generate_cert
# or
make cert
```

### Docker Development Environment

A Docker Compose configuration is provided to set up MySQL and Redis:

```bash
# Start the development environment
docker-compose up -d

# Stop the development environment
docker-compose down
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/login` - Login with username and password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/2fa/setup` - Set up 2FA
- `POST /api/v1/auth/2fa/verify-setup` - Verify 2FA setup
- `POST /api/v1/auth/2fa/verify` - Verify 2FA during login
- `POST /api/v1/auth/2fa/disable` - Disable 2FA
- `GET /api/v1/auth/sessions` - Get active sessions
- `DELETE /api/v1/auth/sessions/{session_id}` - Terminate a session
- `DELETE /api/v1/auth/sessions` - Terminate all sessions except current
- `POST /api/v1/auth/reset-password` - Request password reset
- `POST /api/v1/auth/reset-password/confirm` - Confirm password reset

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/                  # Application code
│   ├── api/              # API endpoints
│   │   ├── auth/         # Authentication endpoints
│   │   └── v1/           # API version 1
│   ├── core/             # Core functionality
│   │   └── security/     # Security utilities
│   ├── db/               # Database setup
│   ├── email-templates/  # Email templates
│   ├── middleware/       # Middleware components
│   ├── models/           # Database models
│   └── services/         # Business logic services
│       ├── auth/         # Authentication services
│       └── email/        # Email services
├── scripts/              # Utility scripts
│   ├── generate_secret_key.py  # Generate secure secret key
│   ├── init_db.py        # Initialize database with default data
│   └── run_tests.py      # Run tests with coverage
├── tests/                # Test suite
├── .env.example          # Example environment variables
├── alembic.ini           # Alembic configuration
├── docker-compose.yml    # Docker development environment
├── Makefile              # Development tasks
├── pytest.ini            # Pytest configuration
├── requirements.txt      # Python dependencies
└── run.py                # Application runner
```