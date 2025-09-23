'use client'

import { useAuth } from '@/app/lib/auth-context'
import { Card } from '@headlessui/react'
import { 
  UserIcon, 
  ShieldCheckIcon, 
  ClockIcon,
  BuildingOfficeIcon 
} from '@heroicons/react/24/outline'

export function DashboardHeader() {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated || !user) {
    return null
  }

  const getRoleColor = (role: string) => {
    const colors = {
      'super_admin': 'bg-red-100 text-red-800 border-red-200',
      'admin': 'bg-purple-100 text-purple-800 border-purple-200',
      'project_manager': 'bg-blue-100 text-blue-800 border-blue-200',
      'analyst': 'bg-green-100 text-green-800 border-green-200',
      'viewer': 'bg-gray-100 text-gray-800 border-gray-200',
      'auditor': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'external': 'bg-orange-100 text-orange-800 border-orange-200',
    }
    return colors[role as keyof typeof colors] || colors['viewer']
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-xl p-6 mb-6 border border-green-200 dark:border-green-800">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        {/* User Info Section */}
        <div className="flex items-center space-x-4 mb-4 lg:mb-0">
          <div className="flex-shrink-0">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <UserIcon className="w-8 h-8 text-white" />
            </div>
          </div>
          
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Welcome back, {user.first_name || user.username}!
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              {user.email}
            </p>
            <div className="flex items-center space-x-2 mt-1">
              <span 
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getRoleColor(user.role)}`}
              >
                <ShieldCheckIcon className="w-3 h-3 mr-1" />
                {user.role.charAt(0).toUpperCase() + user.role.slice(1).replace('_', ' ')}
              </span>
              
              {user.organization && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                  <BuildingOfficeIcon className="w-3 h-3 mr-1" />
                  {user.organization.name}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Status Section */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
          <div className="text-center lg:text-right">
            <p className="text-sm text-gray-500 dark:text-gray-400">Last Login</p>
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {user.last_login ? formatDate(user.last_login) : 'Never'}
            </p>
          </div>
          
          <div className="text-center lg:text-right">
            <p className="text-sm text-gray-500 dark:text-gray-400">Member Since</p>
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {formatDate(user.created_at)}
            </p>
          </div>
          
          <div className="text-center lg:text-right col-span-2 lg:col-span-1">
            <p className="text-sm text-gray-500 dark:text-gray-400">Account Status</p>
            <p className={`text-sm font-medium ${
              user.status === 'active' ? 'text-green-600' : 'text-yellow-600'
            }`}>
              {user.status.charAt(0).toUpperCase() + user.status.slice(1)}
            </p>
          </div>
        </div>
      </div>

      {/* Permissions Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap gap-1">
          <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">Permissions:</span>
          {user.permissions?.slice(0, 4).map((permission) => (
            <span
              key={permission}
              className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              {permission.replace(':', ': ')}
            </span>
          ))}
          {user.permissions && user.permissions.length > 4 && (
            <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
              +{user.permissions.length - 4} more
            </span>
          )}
        </div>
      </div>
    </div>
  )
}