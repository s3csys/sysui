import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Role } from '../../types/user'
import LoadingSpinner from '../ui/LoadingSpinner'

interface RoleProtectedRouteProps {
  children: React.ReactNode
  requiredRole: Role
}

// Role hierarchy
const roleHierarchy: Record<Role, number> = {
  admin: 3,
  editor: 2,
  viewer: 1,
}

const RoleProtectedRoute = ({ children, requiredRole }: RoleProtectedRouteProps) => {
  const { user, isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Check if user has the required role or higher
  const userRoleLevel = user?.role ? roleHierarchy[user.role] : 0
  const requiredRoleLevel = roleHierarchy[requiredRole]

  if (userRoleLevel < requiredRoleLevel) {
    // User doesn't have sufficient permissions
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

export default RoleProtectedRoute