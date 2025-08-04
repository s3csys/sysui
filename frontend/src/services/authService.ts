import axios from 'axios'
import { User } from '../types/user'

// The API URL should match what the Vite proxy is expecting
// The Vite proxy rewrites '/api' to '/api/v1' before forwarding to the backend
const API_URL = '/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    const token = localStorage.getItem('accessToken')
    if (token) {
      console.log('Adding Authorization header with token')
      config.headers.Authorization = `Bearer ${token}`
    } else {
      console.log('No token available for request')
    }
    return config
  },
  (error) => {
    console.error('API request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    console.log(`API Response Success: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status)
    return response
  },
  async (error) => {
    console.error(`API Response Error: ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    })
    
    const originalRequest = error.config
    
    // If error is 401 and we haven't tried to refresh token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('Received 401 error, attempting token refresh')
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refreshToken')
        console.log('Refresh token exists:', !!refreshToken)
        
        if (!refreshToken) {
          console.error('No refresh token available, redirecting to login')
          // No refresh token available, redirect to login
          window.location.href = '/login'
          return Promise.reject(error)
        }
        
        // Try to refresh the token
        // FIXED: Use URLSearchParams for x-www-form-urlencoded format as required by OAuth2
        const formData = new URLSearchParams()
        formData.append('refresh_token', refreshToken)
        console.log('Calling refresh token endpoint')
        
        try {
          const response = await axios.post('/api/v1/auth/refresh', formData, {
            baseURL: '',  // Use absolute URL to avoid interceptors
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          })
          
          console.log('Token refresh successful')
          
          const { access_token, refresh_token } = response.data
          
          // Update tokens in storage
          localStorage.setItem('accessToken', access_token)
          localStorage.setItem('refreshToken', refresh_token)
          console.log('Updated tokens in localStorage')
          
          // Update auth header and retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          console.log('Retrying original request with new token')
          return api(originalRequest)
        } catch (refreshApiError) {
          console.error('Token refresh API call failed:', refreshApiError)
          throw refreshApiError
        }
      } catch (refreshError) {
        console.error('Token refresh process failed:', refreshError)
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        console.log('Cleared tokens from localStorage, redirecting to login')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export const authService = {
  // Register a new user
  async register(userData: { email: string; username: string; password: string }) {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
  
  // Login user
  async login(email: string, password: string, rememberMe: boolean = false) {
    // Use the full email or username as provided
    const username = email;
    
    // Create URLSearchParams for x-www-form-urlencoded format as required by OAuth2
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    
    // Use the api instance which will correctly apply the proxy rewrite rules
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },
  
  // Logout user
  async logout(refreshToken: string) {
    try {
      // First try to get the current session
      const sessions = await this.getSessions()
      const currentSession = sessions.sessions.find(session => session.is_current)
      
      // If we found the current session, terminate it
      if (currentSession) {
        const response = await api.delete(`/auth/sessions/${currentSession.id}`)
        return response.data
      }
      
      // If we couldn't find the current session, terminate all sessions
      const response = await api.delete('/auth/sessions')
      return response.data
    } catch (error) {
      console.error('Error during logout:', error)
      // Even if the API call fails, we want to clear local storage
      return { message: 'Logged out locally' }
    }
  },
  
  // Get current user info
  async getCurrentUser(): Promise<User> {
    console.log('Calling getCurrentUser API')
    try {
      const response = await api.get('/auth/me')
      console.log('getCurrentUser response:', response.data)
      return response.data
    } catch (error) {
      console.error('getCurrentUser error:', error)
      throw error
    }
  },
  
  // Update user profile
  async updateProfile(profileData: { name: string; email: string }): Promise<User> {
    const response = await api.put('/profile/update', {
      email: profileData.email,
      full_name: profileData.name
    })
    return response.data
  },
  
  // Update user password
  async updatePassword(currentPassword: string, newPassword: string): Promise<any> {
    const response = await api.put('/profile/update-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
    return response.data
  },
  
  // Refresh token
  async refreshToken(refreshToken: string) {
    // FIXED: Use URLSearchParams for x-www-form-urlencoded format
    const formData = new URLSearchParams()
    formData.append('refresh_token', refreshToken)
    
    const response = await api.post('/auth/refresh', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },
  
  // Setup two-factor authentication
  async setupTwoFactor() {
    const response = await api.post('/auth/2fa/setup')
    return response.data
  },
  
  // Verify two-factor setup
  async verifyTwoFactor(token: string, remember: boolean = false) {
    const response = await api.post('/auth/2fa/verify', { token, remember })
    return response.data
  },
  
  // Verify two-factor during login
  async verifyTwoFactorLogin(email: string, token: string) {
    const response = await api.post('/auth/2fa/login', { email, token })
    return response.data
  },
  
  // Request password reset
  async forgotPassword(email: string) {
    const response = await api.post('/auth/forgot-password', { email })
    return response.data
  },
  
  // Reset password with token
  async resetPassword(token: string, password: string) {
    const response = await api.post('/auth/reset-password', { token, password })
    return response.data
  },
  
  // Verify email with token
  async verifyEmail(token: string) {
    const response = await api.post('/auth/verify-email', { token })
    return response.data
  },
  
  // Get user sessions
  async getSessions() {
    const response = await api.get('/auth/sessions')
    return response.data
  },
  
  // Revoke a specific session
  async revokeSession(sessionId: string) {
    const response = await api.delete(`/auth/sessions/${sessionId}`)
    return response.data
  },
  
  // Revoke all sessions except current
  async revokeAllSessions() {
    const response = await api.delete('/auth/sessions')
    return response.data
  },
}