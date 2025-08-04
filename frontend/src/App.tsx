import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import RoleProtectedRoute from './components/auth/RoleProtectedRoute'
import MainLayout from './components/layout/MainLayout'
import AuthLayout from './components/layout/AuthLayout'
import LoadingSpinner from './components/ui/LoadingSpinner'

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/auth/LoginPage'))
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('./pages/auth/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('./pages/auth/ResetPasswordPage'))
const VerifyEmailPage = lazy(() => import('./pages/auth/VerifyEmailPage'))
const SetupTwoFactorPage = lazy(() => import('./pages/auth/SetupTwoFactorPage'))
const VerifyTwoFactorPage = lazy(() => import('./pages/auth/VerifyTwoFactorPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const SessionsPage = lazy(() => import('./pages/SessionsPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))

function App() {
  console.log('App - Rendering App component')
  return (
    <AuthProvider>
      <Suspense fallback={<div className="flex h-screen items-center justify-center"><LoadingSpinner size="lg" /></div>}>
        <Routes>
          {/* Auth routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route path="/setup-2fa" element={<SetupTwoFactorPage />} />
            <Route path="/verify-2fa" element={<VerifyTwoFactorPage />} />
          </Route>

          {/* Protected routes */}
          <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/sessions" element={<SessionsPage />} />
            
            {/* Admin routes */}
            <Route 
              path="/admin/*" 
              element={
                <RoleProtectedRoute requiredRole="admin">
                  <Navigate to="/dashboard" replace />
                </RoleProtectedRoute>
              } 
            />
          </Route>

          {/* 404 route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </AuthProvider>
  )
}

export default App