'use client'

import { useAuth } from '@/app/lib/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { ShieldExclamationIcon, UserIcon } from '@heroicons/react/24/outline'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRole?: string[]
  fallbackUrl?: string
  showUnauthorized?: boolean
}

export function ProtectedRoute({ 
  children, 
  requiredRole = [],
  fallbackUrl = '/auth/login',
  showUnauthorized = true 
}: ProtectedRouteProps) {
  const { isAuthenticated, user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Don't redirect while loading
    if (isLoading) return

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      router.push(fallbackUrl)
      return
    }

    // Check role requirements
    if (requiredRole.length > 0 && user && !requiredRole.includes(user.role)) {
      if (showUnauthorized) {
        // Stay on page but show unauthorized message
        return
      } else {
        // Redirect to dashboard or home
        router.push('/dashboard')
        return
      }
    }
  }, [isAuthenticated, user, isLoading, router, requiredRole, fallbackUrl, showUnauthorized])

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-white border-t-transparent"></div>
          </div>
          <h2 className="text-lg font-medium text-gray-900 mb-2">
            Verificando autenticación...
          </h2>
          <p className="text-gray-500">
            Por favor espera un momento
          </p>
        </motion.div>
      </div>
    )
  }

  // Don't render anything while redirecting
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full mb-4">
            <UserIcon className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-lg font-medium text-gray-900 mb-2">
            Redirigiendo al login...
          </h2>
          <p className="text-gray-500">
            Se requiere autenticación para acceder a esta página
          </p>
        </motion.div>
      </div>
    )
  }

  // Check role authorization
  if (requiredRole.length > 0 && user && !requiredRole.includes(user.role)) {
    if (showUnauthorized) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center p-8 max-w-md"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
              <ShieldExclamationIcon className="h-10 w-10 text-red-600" />
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Acceso No Autorizado
            </h2>
            
            <p className="text-gray-600 text-lg mb-6">
              No tienes permisos suficientes para acceder a esta página.
            </p>
            
            <div className="bg-gray-100 rounded-lg p-4 mb-6">
              <div className="text-sm text-gray-700">
                <p><strong>Tu rol actual:</strong> {user.role}</p>
                <p><strong>Roles requeridos:</strong> {requiredRole.join(', ')}</p>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => router.back()}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                Volver Atrás
              </button>
              <button
                onClick={() => router.push('/dashboard')}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Ir al Dashboard
              </button>
            </div>
          </motion.div>
        </div>
      )
    }
    
    // Redirecting, show nothing
    return null
  }

  // User is authenticated and authorized, render children
  return <>{children}</>
}

// Higher-order component version
export function withProtectedRoute<P extends object>(
  Component: React.ComponentType<P>,
  options: Omit<ProtectedRouteProps, 'children'> = {}
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }
}

export default ProtectedRoute