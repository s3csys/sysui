import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../ui/LoadingSpinner'

interface ProtectedRouteProps {
  children: React.ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()

  console.log('ProtectedRoute - Auth State:', { 
    isAuthenticated, 
    isLoading, 
    hasUser: !!user,
    user: user,
    pathname: location.pathname 
  })

  if (isLoading) {
    console.log('ProtectedRoute - Still loading, showing spinner')
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!isAuthenticated) {
    console.log('ProtectedRoute - Not authenticated, redirecting to login')
    // Redirect to login page with return url
    return <Navigate to={`/login?returnUrl=${encodeURIComponent(location.pathname)}`} replace />
  }

  console.log('ProtectedRoute - Authenticated, rendering children')
  return <>{children}</>
}

export default ProtectedRoute