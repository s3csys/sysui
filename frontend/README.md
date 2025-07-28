# SysUI Frontend

## Overview

This is the frontend application for SysUI, a comprehensive server management interface. It's built with React, TypeScript, and TailwindCSS, providing a modern and responsive user interface for server management operations.

## Features

- **Authentication System**
  - User registration with email verification
  - Login with username/password
  - Two-factor authentication (2FA) using TOTP
  - Password reset functionality
  - Session management

- **Role-Based Access Control**
  - Support for different user roles (admin, editor, viewer)
  - Protected routes based on user roles

- **Modern UI**
  - Responsive design for all screen sizes
  - Clean and intuitive user interface
  - Consistent design language

## Prerequisites

- Node.js (v16 or later)
- npm (v7 or later)

## Getting Started

### Installation

1. Install Node.js and npm if not already installed
   - Windows: Download and install from [nodejs.org](https://nodejs.org/)
   - Linux: `sudo apt install nodejs npm` (Ubuntu/Debian) or equivalent for your distribution
   - macOS: `brew install node` (using Homebrew)

2. Clone the repository (if not already done)
   ```
   git clone https://github.com/yourusername/sysui.git
   cd sysui
   ```

3. Navigate to the frontend directory
   ```
   cd frontend
   ```

4. Install dependencies
   ```
   npm install
   ```

### Development

1. Start the development server
   ```
   npm run dev
   ```

2. Open your browser and navigate to `http://localhost:5173`

### Building for Production

1. Build the application
   ```
   npm run build
   ```

2. The built files will be in the `dist` directory

## Project Structure

```
frontend/
├── public/            # Static assets
├── src/
│   ├── components/    # Reusable UI components
│   │   ├── auth/      # Authentication-related components
│   │   ├── layout/    # Layout components
│   │   └── ui/        # UI components
│   ├── context/       # React context providers
│   ├── pages/         # Page components
│   │   └── auth/      # Authentication pages
│   ├── services/      # API services
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Utility functions
│   ├── App.tsx        # Main application component
│   ├── main.tsx       # Application entry point
│   └── index.css      # Global styles
├── .env               # Environment variables
├── index.html         # HTML template
├── package.json       # Dependencies and scripts
├── postcss.config.js  # PostCSS configuration
├── tailwind.config.js # Tailwind CSS configuration
├── tsconfig.json      # TypeScript configuration
└── vite.config.ts     # Vite configuration
```

## Backend Integration

This frontend application is designed to work with the SysUI backend API. By default, it expects the backend to be running at `http://localhost:8000`. You can change this by modifying the `.env` file:

```
VITE_API_URL=http://your-backend-url
```

## Testing

Run tests with:

```
npm test
```

Or in watch mode:

```
npm run test:watch
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the terms specified in the repository's main license file.