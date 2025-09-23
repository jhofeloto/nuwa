'use client'

import { useState, Fragment } from 'react'
import { Menu, Transition } from '@headlessui/react'
import { useAuth, User } from '@/app/lib/auth-context'
import { 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon,
  UserIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'
import Link from 'next/link'

interface UserMenuProps {
  className?: string
  showFullMenu?: boolean
}

// Role display mapping
const roleDisplayMap = {
  super_admin: { label: 'Super Admin', color: 'text-purple-600 bg-purple-100' },
  admin: { label: 'Admin', color: 'text-red-600 bg-red-100' },
  project_manager: { label: 'Project Manager', color: 'text-blue-600 bg-blue-100' },
  analyst: { label: 'Analyst', color: 'text-green-600 bg-green-100' },
  viewer: { label: 'Viewer', color: 'text-gray-600 bg-gray-100' },
  auditor: { label: 'Auditor', color: 'text-orange-600 bg-orange-100' },
  external: { label: 'External', color: 'text-indigo-600 bg-indigo-100' },
}

export function UserMenu({ className = '', showFullMenu = true }: UserMenuProps) {
  const { user, logout, isLoading } = useAuth()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  if (!user) return null

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  const getUserDisplayName = (user: User) => {
    if (user.fullName) return user.fullName
    if (user.firstName && user.lastName) return `${user.firstName} ${user.lastName}`
    if (user.username) return user.username
    return user.email
  }

  const getUserInitials = (user: User) => {
    const name = getUserDisplayName(user)
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const roleInfo = roleDisplayMap[user.role]

  if (!showFullMenu) {
    // Simple user avatar for compact displays
    return (
      <div className={`flex items-center ${className}`}>
        {user.avatarUrl ? (
          <img
            src={user.avatarUrl}
            alt={getUserDisplayName(user)}
            className="h-8 w-8 rounded-full object-cover"
          />
        ) : (
          <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
            {getUserInitials(user)}
          </div>
        )}
      </div>
    )
  }

  return (
    <Menu as="div" className={`relative inline-block text-left ${className}`}>
      <div>
        <Menu.Button className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
          {/* Avatar */}
          {user.avatarUrl ? (
            <img
              src={user.avatarUrl}
              alt={getUserDisplayName(user)}
              className="h-10 w-10 rounded-full object-cover border-2 border-gray-200"
            />
          ) : (
            <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center text-white font-medium border-2 border-gray-200">
              {getUserInitials(user)}
            </div>
          )}

          {/* User Info */}
          <div className="flex-1 text-left hidden sm:block">
            <div className="text-sm font-medium text-gray-900 truncate max-w-[120px]">
              {getUserDisplayName(user)}
            </div>
            <div className="flex items-center space-x-2">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${roleInfo.color}`}>
                {roleInfo.label}
              </span>
              {user.is2faEnabled && (
                <ShieldCheckIcon className="h-3 w-3 text-green-500" title="2FA Enabled" />
              )}
            </div>
          </div>

          {/* Dropdown Arrow */}
          <svg
            className="w-5 h-5 text-gray-400"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Panel className="absolute right-0 z-10 mt-2 w-72 origin-top-right divide-y divide-gray-100 rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          {/* User Info Section */}
          <div className="px-4 py-3">
            <div className="flex items-center space-x-3">
              {user.avatarUrl ? (
                <img
                  src={user.avatarUrl}
                  alt={getUserDisplayName(user)}
                  className="h-12 w-12 rounded-full object-cover"
                />
              ) : (
                <div className="h-12 w-12 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center text-white text-lg font-medium">
                  {getUserInitials(user)}
                </div>
              )}
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {getUserDisplayName(user)}
                </p>
                <p className="text-sm text-gray-500 truncate">
                  {user.email}
                </p>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${roleInfo.color}`}>
                    {roleInfo.label}
                  </span>
                  {user.is2faEnabled && (
                    <div className="flex items-center space-x-1">
                      <ShieldCheckIcon className="h-3 w-3 text-green-500" />
                      <span className="text-xs text-green-600">2FA</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-1">
            <Menu.Item>
              {({ active }) => (
                <Link
                  href="/dashboard/profile"
                  className={`${
                    active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                  } group flex items-center px-4 py-2 text-sm transition-colors duration-200`}
                >
                  <UserIcon className="mr-3 h-4 w-4 text-gray-400" />
                  Mi Perfil
                </Link>
              )}
            </Menu.Item>

            <Menu.Item>
              {({ active }) => (
                <Link
                  href="/dashboard/settings"
                  className={`${
                    active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                  } group flex items-center px-4 py-2 text-sm transition-colors duration-200`}
                >
                  <Cog6ToothIcon className="mr-3 h-4 w-4 text-gray-400" />
                  Configuración
                </Link>
              )}
            </Menu.Item>
          </div>

          {/* Logout Section */}
          <div className="py-1">
            <Menu.Item>
              {({ active }) => (
                <button
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className={`${
                    active ? 'bg-red-50 text-red-700' : 'text-red-600'
                  } group flex w-full items-center px-4 py-2 text-sm transition-colors duration-200 disabled:opacity-50`}
                >
                  {isLoggingOut ? (
                    <svg className="mr-3 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <ArrowRightOnRectangleIcon className="mr-3 h-4 w-4 text-red-400" />
                  )}
                  {isLoggingOut ? 'Cerrando sesión...' : 'Cerrar Sesión'}
                </button>
              )}
            </Menu.Item>
          </div>
        </Menu.Panel>
      </Transition>
    </Menu>
  )
}

export default UserMenu