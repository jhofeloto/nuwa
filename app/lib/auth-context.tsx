'use client'

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'

// Types
interface User {
  id: number
  email: string
  username?: string
  firstName?: string
  lastName?: string
  fullName?: string
  role: UserRole
  status: UserStatus
  isEmailVerified: boolean
  is2faEnabled: boolean
  organizationId?: number
  avatarUrl?: string
  title?: string
  department?: string
  createdAt: string
  lastLogin?: string
}

type UserRole = 'super_admin' | 'admin' | 'project_manager' | 'analyst' | 'viewer' | 'auditor' | 'external'
type UserStatus = 'active' | 'inactive' | 'suspended' | 'pending_verification' | 'pending_approval' | 'archived'

interface AuthTokens {
  accessToken: string
  refreshToken: string
  expiresAt: string
}

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; tokens: AuthTokens } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'CLEAR_ERROR' }

// Initial state
const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      }
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      }
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      }
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }
    default:
      return state
  }
}

// Context
interface AuthContextType extends AuthState {
  login: (email: string, password: string, remember?: boolean) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  updateProfile: (userData: Partial<User>) => Promise<void>
  clearError: () => void
}

interface RegisterData {
  email: string
  password: string
  firstName?: string
  lastName?: string
  username?: string
  organizationId?: number
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// API Base URL - configure according to your backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://8001-itul5g8xqfm9r87o3q08w-6532622b.e2b.dev'

// Storage utilities
const TOKEN_STORAGE_KEY = 'nuwa_auth_tokens'
const USER_STORAGE_KEY = 'nuwa_auth_user'

function saveToStorage(key: string, data: any) {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, JSON.stringify(data))
  }
}

function loadFromStorage(key: string) {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : null
  }
  return null
}

function removeFromStorage(key: string) {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(key)
  }
}

// Auth Provider
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Load auth state from storage on mount
  useEffect(() => {
    const storedTokens = loadFromStorage(TOKEN_STORAGE_KEY)
    const storedUser = loadFromStorage(USER_STORAGE_KEY)

    if (storedTokens && storedUser) {
      // Check if token is still valid
      const expiresAt = new Date(storedTokens.expiresAt)
      if (expiresAt > new Date()) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: {
            user: storedUser,
            tokens: storedTokens,
          },
        })
      } else {
        // Token expired, try to refresh
        refreshTokenSilently(storedTokens.refreshToken)
      }
    }
  }, [])

  // API call helper
  async function apiCall(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    // Add auth token if available
    if (state.tokens?.accessToken) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${state.tokens.accessToken}`,
      }
    }

    const response = await fetch(url, config)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Network error' }))
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Auth methods
  async function login(email: string, password: string, remember = false) {
    try {
      dispatch({ type: 'AUTH_START' })

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, remember }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data = await response.json()
      const { user, tokens } = data

      // Save to storage
      saveToStorage(TOKEN_STORAGE_KEY, tokens)
      saveToStorage(USER_STORAGE_KEY, user)

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, tokens },
      })
    } catch (error) {
      dispatch({
        type: 'AUTH_FAILURE',
        payload: error instanceof Error ? error.message : 'Login failed',
      })
      throw error
    }
  }

  async function register(userData: RegisterData) {
    try {
      dispatch({ type: 'AUTH_START' })

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      const data = await response.json()
      
      // Registration successful but may require email verification
      dispatch({
        type: 'AUTH_FAILURE',
        payload: data.message || 'Please check your email to verify your account',
      })
    } catch (error) {
      dispatch({
        type: 'AUTH_FAILURE',
        payload: error instanceof Error ? error.message : 'Registration failed',
      })
      throw error
    }
  }

  async function logout() {
    try {
      if (state.tokens?.accessToken) {
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${state.tokens.accessToken}`,
          },
        }).catch(() => {
          // Ignore logout API errors, still clear local state
        })
      }
    } finally {
      // Clear storage
      removeFromStorage(TOKEN_STORAGE_KEY)
      removeFromStorage(USER_STORAGE_KEY)
      
      dispatch({ type: 'AUTH_LOGOUT' })
    }
  }

  async function refreshTokenSilently(refreshToken: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data = await response.json()
      const { tokens } = data

      // Update storage
      saveToStorage(TOKEN_STORAGE_KEY, tokens)

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: state.user!,
          tokens,
        },
      })
    } catch (error) {
      // Refresh failed, logout user
      await logout()
    }
  }

  async function refreshToken() {
    if (!state.tokens?.refreshToken) {
      throw new Error('No refresh token available')
    }
    
    await refreshTokenSilently(state.tokens.refreshToken)
  }

  async function updateProfile(userData: Partial<User>) {
    try {
      const response = await apiCall('/api/v1/auth/me', {
        method: 'PATCH',
        body: JSON.stringify(userData),
      })

      const updatedUser = response.user
      saveToStorage(USER_STORAGE_KEY, updatedUser)
      
      dispatch({
        type: 'UPDATE_USER',
        payload: updatedUser,
      })
    } catch (error) {
      throw error
    }
  }

  function clearError() {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
    clearError,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Higher-order component for protected routes
export function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      // Redirect to login or show login component
      return <div>Please log in to access this page</div>
    }

    return <Component {...props} />
  }
}

export type { User, UserRole, UserStatus, AuthTokens, RegisterData }