import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { jwtDecode } from 'jwt-decode'
import { authService } from '../services/authService'
import { User } from '../types/user'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<{ requiresTwoFactor: boolean }>
  register: (userData: { email: string; username: string; password: string }) => Promise<void>
  logout: () => void
  setupTwoFactor: () => Promise<{ qrCodeUrl: string; secret: string }>
  verifyTwoFactor: (token: string, remember?: boolean) => Promise<void>
  verifyTwoFactorLogin: (token: string) => Promise<void>
  forgotPassword: (email: string) => Promise<void>
  resetPassword: (token: string, password: string) => Promise<void>
  verifyEmail: (token: string) => Promise<void>
  updateProfile: (profileData: { name: string; email: string }) => Promise<void>
  updatePassword: (currentPassword: string, newPassword: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is already logged in
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem('accessToken')
        console.log('Checking auth status, token exists:', !!token)
        
        if (!token) {
          console.log('No token found, not authenticated')
          setIsLoading(false)
          return
        }
        
        // Check if token is expired
        try {
          const decoded = jwtDecode(token)
          const currentTime = Date.now() / 1000
          console.log('Token expiry check:', decoded.exp, 'Current time:', currentTime)
          
          if (decoded.exp && decoded.exp < currentTime) {
            // Token is expired, try to refresh
            console.log('Token expired, attempting refresh')
            await refreshToken()
          } else {
            // Token is valid, get user info
            console.log('Token valid, getting user info')
            try {
              const userData = await authService.getCurrentUser()
              console.log('User data received:', userData)
              setUser(userData)
            } catch (error) {
              console.error('Error getting user data:', error)
              // If getCurrentUser fails, try to refresh token
              console.log('Attempting token refresh after getCurrentUser failure')
              await refreshToken()
            }
          }
        } catch (error) {
          // Invalid token, try to refresh
          console.error('Token validation error:', error)
          await refreshToken()
        }
      } catch (error) {
        // If refresh fails, clear auth state
        console.error('Auth check failed:', error)
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        setUser(null)
      } finally {
        setIsLoading(false)
        console.log('Auth loading complete, isAuthenticated:', !!user)
      }
    }

    checkAuthStatus()
  }, [])

  const refreshToken = async () => {
    console.log('Starting token refresh process')
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      console.log('Refresh token exists:', !!refreshToken)
      
      if (!refreshToken) {
        console.error('No refresh token available')
        throw new Error('No refresh token available')
      }
      
      console.log('Calling authService.refreshToken')
      try {
        const response = await authService.refreshToken(refreshToken)
        console.log('Token refresh successful, new tokens received')
        
        localStorage.setItem('accessToken', response.access_token)
        localStorage.setItem('refreshToken', response.refresh_token)
        
        console.log('Tokens stored in localStorage, fetching user data')
        const userData = await authService.getCurrentUser()
        console.log('User data after refresh:', userData)
        setUser(userData)
        
        return true
      } catch (refreshError) {
        console.error('Token refresh API call failed:', refreshError)
        throw refreshError
      }
    } catch (error) {
      console.error('Token refresh process failed:', error)
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      setUser(null)
      return false
    }
  }

  const login = async (email: string, password: string) => {
    console.log('Login attempt for email:', email)
    try {
      console.log('Calling authService.login')
      const response = await authService.login(email, password)
      console.log('Login response received:', { ...response, access_token: response.access_token ? '[REDACTED]' : undefined, refresh_token: response.refresh_token ? '[REDACTED]' : undefined })
      
      if (response.requiresTwoFactor) {
        console.log('2FA required, storing email in sessionStorage')
        // Store email for 2FA verification
        sessionStorage.setItem('twoFactorEmail', email)
        return { requiresTwoFactor: true }
      }
      
      console.log('Storing tokens in localStorage')
      // Fix: Use snake_case property names from the backend response
      localStorage.setItem('accessToken', response.access_token)
      localStorage.setItem('refreshToken', response.refresh_token)
      
      console.log('Fetching user data after login')
      try {
        const userData = await authService.getCurrentUser()
        console.log('User data received after login:', userData)
        setUser(userData)
        console.log('User state updated, authentication complete')
        return { requiresTwoFactor: false }
      } catch (userDataError) {
        console.error('Failed to fetch user data after login:', userDataError)
        throw userDataError
      }
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const register = async (userData: { email: string; username: string; password: string }) => {
    try {
      await authService.register(userData)
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        await authService.logout(refreshToken)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      setUser(null)
      navigate('/login')
    }
  }

  const setupTwoFactor = async () => {
    try {
      const response = await authService.setupTwoFactor()
      return response
    } catch (error) {
      throw error
    }
  }

  const verifyTwoFactor = async (token: string, remember: boolean = false) => {
    try {
      await authService.verifyTwoFactor(token, remember)
    } catch (error) {
      throw error
    }
  }

  const verifyTwoFactorLogin = async (token: string) => {
    try {
      const email = sessionStorage.getItem('twoFactorEmail')
      
      if (!email) {
        throw new Error('Email not found for 2FA verification')
      }
      
      const response = await authService.verifyTwoFactorLogin(email, token)
      
      localStorage.setItem('accessToken', response.access_token)
      localStorage.setItem('refreshToken', response.refresh_token)
      
      const userData = await authService.getCurrentUser()
      setUser(userData)
      
      // Clear the stored email
      sessionStorage.removeItem('twoFactorEmail')
    } catch (error) {
      throw error
    }
  }

  const forgotPassword = async (email: string) => {
    try {
      await authService.forgotPassword(email)
    } catch (error) {
      throw error
    }
  }

  const resetPassword = async (token: string, password: string) => {
    try {
      await authService.resetPassword(token, password)
    } catch (error) {
      throw error
    }
  }

  const verifyEmail = async (token: string) => {
    try {
      await authService.verifyEmail(token)
    } catch (error) {
      throw error
    }
  }

  const updateProfile = async (profileData: { name: string; email: string }) => {
    try {
      const updatedUser = await authService.updateProfile(profileData)
      setUser(updatedUser)
    } catch (error) {
      throw error
    }
  }

  const updatePassword = async (currentPassword: string, newPassword: string) => {
    try {
      await authService.updatePassword(currentPassword, newPassword)
    } catch (error) {
      throw error
    }
  }

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    setupTwoFactor,
    verifyTwoFactor,
    verifyTwoFactorLogin,
    forgotPassword,
    resetPassword,
    verifyEmail,
    updateProfile,
    updatePassword,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  
  return context
}