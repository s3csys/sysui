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
        
        if (!token) {
          setIsLoading(false)
          return
        }
        
        // Check if token is expired
        try {
          const decoded = jwtDecode(token)
          const currentTime = Date.now() / 1000
          
          if (decoded.exp && decoded.exp < currentTime) {
            // Token is expired, try to refresh
            await refreshToken()
          } else {
            // Token is valid, get user info
            const userData = await authService.getCurrentUser()
            setUser(userData)
          }
        } catch (error) {
          // Invalid token, try to refresh
          await refreshToken()
        }
      } catch (error) {
        // If refresh fails, clear auth state
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuthStatus()
  }, [])

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }
      
      const response = await authService.refreshToken(refreshToken)
      
      localStorage.setItem('accessToken', response.accessToken)
      localStorage.setItem('refreshToken', response.refreshToken)
      
      const userData = await authService.getCurrentUser()
      setUser(userData)
      
      return true
    } catch (error) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      setUser(null)
      return false
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password)
      
      if (response.requiresTwoFactor) {
        // Store email for 2FA verification
        sessionStorage.setItem('twoFactorEmail', email)
        return { requiresTwoFactor: true }
      }
      
      localStorage.setItem('accessToken', response.accessToken)
      localStorage.setItem('refreshToken', response.refreshToken)
      
      const userData = await authService.getCurrentUser()
      setUser(userData)
      
      return { requiresTwoFactor: false }
    } catch (error) {
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
      
      localStorage.setItem('accessToken', response.accessToken)
      localStorage.setItem('refreshToken', response.refreshToken)
      
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