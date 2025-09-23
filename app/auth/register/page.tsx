'use client'

import { useAuth } from '@/app/lib/auth-context'
import { RegisterForm } from '@/app/ui/auth/register-form'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

export default function RegisterPage() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  const handleRegisterSuccess = () => {
    setShowSuccessMessage(true)
    // After showing success message, redirect to login
    setTimeout(() => {
      router.push('/auth/login')
    }, 3000)
  }

  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600"></div>
      </div>
    )
  }

  if (showSuccessMessage) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center p-8"
        >
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            ¡Registro Exitoso!
          </h2>
          
          <p className="text-gray-600 text-lg mb-6 max-w-md">
            Tu cuenta ha sido creada correctamente. Revisa tu email para verificar tu cuenta 
            antes de iniciar sesión.
          </p>
          
          <div className="flex items-center justify-center space-x-2 text-blue-600">
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Redirigiendo al login...</span>
          </div>
        </motion.div>
      </div>
    )
  }

  return <RegisterForm onSuccess={handleRegisterSuccess} />
}