import axios from 'axios'
import { User } from '../types/user'

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
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // If error is 401 and we haven't tried to refresh token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refreshToken')
        
        if (!refreshToken) {
          // No refresh token available, redirect to login
          window.location.href = '/login'
          return Promise.reject(error)
        }
        
        // Try to refresh the token
        const response = await axios.post(`${API_URL}/v1/auth/refresh-token`, {
          refreshToken,
        })
        
        const { accessToken, refreshToken: newRefreshToken } = response.data
        
        // Update tokens in storage
        localStorage.setItem('accessToken', accessToken)
        localStorage.setItem('refreshToken', newRefreshToken)
        
        // Update auth header and retry original request
        originalRequest.headers.Authorization = `Bearer ${accessToken}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
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
    const response = await api.post('/v1/auth/register', userData)
    return response.data
  },
  
  // Login user
  async login(email: string, password: string) {
    // Using form data format as required by the backend
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    // Use the correct API endpoint with v1 prefix
    const response = await axios.post(`${API_URL}/v1/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },
  
  // Logout user
  async logout(refreshToken: string) {
    const response = await api.post('/v1/auth/logout', { refreshToken })
    return response.data
  },
  
  // Get current user info
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/v1/auth/me')
    return response.data
  },
  
  // Update user profile
  async updateProfile(profileData: { name: string; email: string }): Promise<User> {
    const response = await api.put('/v1/profile/update', {
      email: profileData.email,
      full_name: profileData.name
    })
    return response.data
  },
  
  // Update user password
  async updatePassword(currentPassword: string, newPassword: string): Promise<any> {
    const response = await api.put('/v1/profile/update-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
    return response.data
  },
  
  // Refresh token
  async refreshToken(refreshToken: string) {
    const response = await api.post('/v1/auth/refresh-token', { refreshToken })
    return response.data
  },
  
  // Setup two-factor authentication
  async setupTwoFactor() {
    const response = await api.post('/v1/auth/2fa/setup')
    return response.data
  },
  
  // Verify two-factor setup
  async verifyTwoFactor(token: string, remember: boolean = false) {
    const response = await api.post('/v1/auth/2fa/verify', { token, remember })
    return response.data
  },
  
  // Verify two-factor during login
  async verifyTwoFactorLogin(email: string, token: string) {
    const response = await api.post('/v1/auth/2fa/login', { email, token })
    return response.data
  },
  
  // Request password reset
  async forgotPassword(email: string) {
    const response = await api.post('/v1/auth/forgot-password', { email })
    return response.data
  },
  
  // Reset password with token
  async resetPassword(token: string, password: string) {
    const response = await api.post('/v1/auth/reset-password', { token, password })
    return response.data
  },
  
  // Verify email with token
  async verifyEmail(token: string) {
    const response = await api.post('/v1/auth/verify-email', { token })
    return response.data
  },
  
  // Get user sessions
  async getSessions() {
    const response = await api.get('/v1/auth/sessions')
    return response.data
  },
  
  // Revoke a specific session
  async revokeSession(sessionId: string) {
    const response = await api.delete(`/v1/auth/sessions/${sessionId}`)
    return response.data
  },
  
  // Revoke all sessions except current
  async revokeAllSessions() {
    const response = await api.delete('/v1/auth/sessions')
    return response.data
  },
}