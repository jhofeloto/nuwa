'use client'

import { useAuth } from '@/app/lib/auth-context'
import { usePermissions } from '@/app/lib/auth-hooks'
import { 
  PlusIcon,
  ChartBarIcon,
  DocumentMagnifyingGlassIcon,
  UserGroupIcon,
  CogIcon,
  MapIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface QuickAction {
  name: string
  description: string
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  href: string
  permissions: string[]
  color: string
}

const quickActions: QuickAction[] = [
  {
    name: 'Create Project',
    description: 'Start a new carbon capture project',
    icon: PlusIcon,
    href: '/dashboard/project/create',
    permissions: ['PROJECT_CREATE'],
    color: 'bg-green-500 hover:bg-green-600'
  },
  {
    name: 'Analytics',
    description: 'View carbon analytics and reports',
    icon: ChartBarIcon,
    href: '/analytics',
    permissions: ['PROJECT_READ', 'EVALUATION_READ'],
    color: 'bg-blue-500 hover:bg-blue-600'
  },
  {
    name: 'Evaluations',
    description: 'Manage project evaluations',
    icon: DocumentMagnifyingGlassIcon,
    href: '/dashboard/evaluations',
    permissions: ['EVALUATION_CREATE', 'EVALUATION_READ'],
    color: 'bg-purple-500 hover:bg-purple-600'
  },
  {
    name: 'Satellite Data',
    description: 'Access satellite monitoring',
    icon: MapIcon,
    href: '/dashboard/satellite',
    permissions: ['SATELLITE_READ', 'SATELLITE_ANALYZE'],
    color: 'bg-indigo-500 hover:bg-indigo-600'
  },
  {
    name: 'User Management',
    description: 'Manage team members and roles',
    icon: UserGroupIcon,
    href: '/dashboard/users',
    permissions: ['USER_READ', 'USER_CREATE'],
    color: 'bg-orange-500 hover:bg-orange-600'
  },
  {
    name: 'System Settings',
    description: 'Configure system preferences',
    icon: CogIcon,
    href: '/dashboard/settings',
    permissions: ['SYSTEM_CONFIG', 'SYSTEM_MONITOR'],
    color: 'bg-gray-500 hover:bg-gray-600'
  }
]

export function QuickActions() {
  const { user } = useAuth()
  const { hasAnyPermission } = usePermissions()

  if (!user) return null

  // Filter actions based on user permissions
  const availableActions = quickActions.filter(action => 
    hasAnyPermission(action.permissions)
  )

  if (availableActions.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          No actions available for your current role.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Quick Actions
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {availableActions.map((action) => (
          <Link
            key={action.name}
            href={action.href}
            className="group relative block p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 transition-all duration-200 hover:shadow-md"
          >
            <div className="flex items-start space-x-3">
              <div className={`flex-shrink-0 p-2 rounded-lg ${action.color} transition-colors duration-200`}>
                <action.icon className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200">
                  {action.name}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {action.description}
                </p>
              </div>
            </div>
            
            {/* Hover effect */}
            <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-500/10 to-green-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none" />
          </Link>
        ))}
      </div>

      {/* Role-based tip */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          💡 Available actions are based on your role: <span className="font-medium">{user.role.replace('_', ' ')}</span>
        </p>
      </div>
    </div>
  )
}