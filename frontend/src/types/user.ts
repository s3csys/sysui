export type Role = 'admin' | 'editor' | 'viewer'

export interface User {
  id: string
  email: string
  username: string
  name?: string
  full_name?: string
  role: Role
  isTwoFactorEnabled: boolean
  is_2fa_enabled?: boolean
  is_active?: boolean
  is_verified?: boolean
  createdAt: string
  updatedAt: string
}

export interface Session {
  id: string
  userId: string
  userAgent: string
  ipAddress: string
  lastActive: string
  createdAt: string
  isCurrent: boolean
}

export interface Permission {
  id: string
  name: string
  description: string
}