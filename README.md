# SysUI - Comprehensive Server Management Interface

## Overview

SysUI is a modern, secure, and user-friendly server management interface built with FastAPI (backend) and React (frontend). It provides a comprehensive solution for managing and monitoring servers with a focus on security and usability.

## Features

### Authentication and Security
- User registration with email verification
- Secure login with JWT authentication
- Two-Factor Authentication (2FA) using TOTP
- Role-based access control (admin, editor, viewer roles)
- Secure password storage with bcrypt hashing
- Token refresh mechanism
- Rate limiting for authentication endpoints
- Session management (view active sessions, logout from all devices)

### User Interface
- Modern, responsive design built with React and TailwindCSS
- Clean and intuitive user interface
- Consistent design language
- Support for different screen sizes

### Server Management
- Server monitoring and status overview
- Configuration management
- Log viewing and analysis
- Task scheduling and automation

## Architecture

SysUI consists of two main components:

1. **Backend**: A FastAPI application that provides a RESTful API for server management operations
2. **Frontend**: A React application that consumes the API and provides a user interface

## Installation

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

### Quick Start

#### Windows

```
install.bat
```

#### Linux

```bash
chmod +x install.sh
./install.sh
```

## Documentation

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [Installation Guide](INSTALL.md)

## Development

### Backend Development

The backend is built with FastAPI and provides a RESTful API for server management operations. It uses SQLAlchemy for database operations, Alembic for database migrations, and various security libraries for authentication and authorization.

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

### Frontend Development

The frontend is built with React, TypeScript, and TailwindCSS. It uses Vite for building and development, React Router for routing, and various UI libraries for components.

```bash
cd frontend
npm run dev
```

## Testing

### Backend Testing

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m pytest
```

### Frontend Testing

```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.