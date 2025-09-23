'use client'

import { useAuth, UserRole } from './auth-context'
import { useMemo } from 'react'

// Permission mappings based on roles
const ROLE_PERMISSIONS = {
  super_admin: [
    'project:create', 'project:read', 'project:update', 'project:delete', 'project:approve',
    'evaluation:create', 'evaluation:read', 'evaluation:update', 'evaluation:delete', 'evaluation:verify',
    'satellite:read', 'satellite:analyze', 'satellite:manage',
    'ml:read', 'ml:predict', 'ml:train', 'ml:manage',
    'user:create', 'user:read', 'user:update', 'user:delete', 'user:manage',
    'system:read', 'system:manage', 'system:configure',
    'gis:read', 'gis:analyze', 'gis:manage'
  ],
  admin: [
    'project:create', 'project:read', 'project:update', 'project:delete',
    'evaluation:create', 'evaluation:read', 'evaluation:update', 'evaluation:delete',
    'satellite:read', 'satellite:analyze',
    'ml:read', 'ml:predict',
    'user:create', 'user:read', 'user:update',
    'system:read',
    'gis:read', 'gis:analyze'
  ],
  project_manager: [
    'project:create', 'project:read', 'project:update', 'project:delete',
    'evaluation:create', 'evaluation:read', 'evaluation:update',
    'satellite:read', 'satellite:analyze',
    'ml:read', 'ml:predict',
    'user:read',
    'gis:read', 'gis:analyze'
  ],
  analyst: [
    'project:read',
    'evaluation:read', 'evaluation:create', 'evaluation:update',
    'satellite:read', 'satellite:analyze',
    'ml:read', 'ml:predict',
    'user:read',
    'gis:read', 'gis:analyze'
  ],
  viewer: [
    'project:read',
    'evaluation:read',
    'satellite:read',
    'ml:read',
    'user:read',
    'gis:read'
  ],
  auditor: [
    'project:read',
    'evaluation:read', 'evaluation:verify',
    'satellite:read',
    'ml:read',
    'user:read',
    'system:read',
    'gis:read'
  ],
  external: [
    'project:read',
    'evaluation:read',
    'satellite:read',
    'ml:read'
  ]
}

export function usePermissions() {
  const { user } = useAuth()

  const permissions = useMemo(() => {
    if (!user) return []
    return ROLE_PERMISSIONS[user.role as UserRole] || []
  }, [user])

  const hasPermission = (permission: string): boolean => {
    return permissions.includes(permission)
  }

  const hasAnyPermission = (permissionList: string[]): boolean => {
    return permissionList.some(permission => permissions.includes(permission))
  }

  const hasAllPermissions = (permissionList: string[]): boolean => {
    return permissionList.every(permission => permissions.includes(permission))
  }

  const canManageUsers = (): boolean => {
    return hasAnyPermission(['user:create', 'user:update', 'user:delete', 'user:manage'])
  }

  const canManageProjects = (): boolean => {
    return hasAnyPermission(['project:create', 'project:update', 'project:delete'])
  }

  const canManageSystem = (): boolean => {
    return hasAnyPermission(['system:manage', 'system:configure'])
  }

  const canAccessML = (): boolean => {
    return hasAnyPermission(['ml:read', 'ml:predict', 'ml:train', 'ml:manage'])
  }

  const canAccessSatellite = (): boolean => {
    return hasAnyPermission(['satellite:read', 'satellite:analyze', 'satellite:manage'])
  }

  const canVerifyEvaluations = (): boolean => {
    return hasPermission('evaluation:verify')
  }

  const isAdminLevel = (): boolean => {
    return user?.role === 'super_admin' || user?.role === 'admin'
  }

  const isProjectManagerLevel = (): boolean => {
    return ['super_admin', 'admin', 'project_manager'].includes(user?.role || '')
  }

  return {
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    canManageUsers,
    canManageProjects,
    canManageSystem,
    canAccessML,
    canAccessSatellite,
    canVerifyEvaluations,
    isAdminLevel,
    isProjectManagerLevel,
    user
  }
}

// Role hierarchy helper
export function useRoleHierarchy() {
  const { user } = useAuth()

  const ROLE_LEVELS = {
    external: 1,
    viewer: 2,
    auditor: 3,
    analyst: 4,
    project_manager: 5,
    admin: 6,
    super_admin: 7
  }

  const getUserLevel = (): number => {
    if (!user) return 0
    return ROLE_LEVELS[user.role as UserRole] || 0
  }

  const hasRoleOrHigher = (requiredRole: UserRole): boolean => {
    const userLevel = getUserLevel()
    const requiredLevel = ROLE_LEVELS[requiredRole] || 0
    return userLevel >= requiredLevel
  }

  const canAccessRole = (targetRole: UserRole): boolean => {
    // Users can only manage users with lower roles
    const userLevel = getUserLevel()
    const targetLevel = ROLE_LEVELS[targetRole] || 0
    return userLevel > targetLevel
  }

  return {
    getUserLevel,
    hasRoleOrHigher,
    canAccessRole,
    userRole: user?.role as UserRole
  }
}

// Component visibility helper
export function useComponentVisibility() {
  const { hasPermission, canManageUsers, canManageProjects, isAdminLevel } = usePermissions()
  const { user } = useAuth()

  return {
    // Navigation visibility
    showAdminPanel: isAdminLevel(),
    showUserManagement: canManageUsers(),
    showProjectManagement: canManageProjects(),
    showSystemSettings: hasPermission('system:manage'),
    
    // Feature visibility
    showMLFeatures: hasPermission('ml:read'),
    showSatelliteFeatures: hasPermission('satellite:read'),
    showAdvancedAnalytics: hasPermission('gis:analyze'),
    
    // Action buttons visibility
    showCreateProject: hasPermission('project:create'),
    showEditProject: hasPermission('project:update'),
    showDeleteProject: hasPermission('project:delete'),
    showApproveProject: hasPermission('project:approve'),
    
    showCreateEvaluation: hasPermission('evaluation:create'),
    showEditEvaluation: hasPermission('evaluation:update'),
    showVerifyEvaluation: hasPermission('evaluation:verify'),
    
    // User info
    userDisplayName: user?.fullName || user?.firstName || user?.username || user?.email || 'Usuario',
    userRole: user?.role,
    userAvatar: user?.avatarUrl
  }
}