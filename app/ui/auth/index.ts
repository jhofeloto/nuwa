// Auth component exports
export { LoginForm } from './login-form'
export { RegisterForm } from './register-form'
export { AuthModal } from './auth-modal'
export { UserMenu } from './user-menu'
export { ProtectedRoute, withProtectedRoute } from './protected-route'

// Auth context and hooks
export { useAuth, AuthProvider, withAuth } from '@/app/lib/auth-context'
export { usePermissions, useRoleHierarchy, useComponentVisibility } from '@/app/lib/auth-hooks'

// Types
export type {
  User,
  UserRole,
  UserStatus,
  AuthTokens,
  RegisterData
} from '@/app/lib/auth-context'