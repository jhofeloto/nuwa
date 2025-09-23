'use client'

import { useState, FormEvent } from 'react'
import { useAuth, RegisterData } from '@/app/lib/auth-context'
import { Button } from '@/app/ui/button'
import { Card } from '@/app/ui/card'
import { 
  EyeIcon, 
  EyeSlashIcon, 
  LockClosedIcon, 
  AtSymbolIcon,
  UserIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'

interface RegisterFormProps {
  onSuccess?: () => void
  onSwitchToLogin?: () => void
  embedded?: boolean
}

interface FormData extends RegisterData {
  confirmPassword: string
  agreeToTerms: boolean
}

interface PasswordValidation {
  length: boolean
  uppercase: boolean
  lowercase: boolean
  number: boolean
  special: boolean
}

export function RegisterForm({ onSuccess, onSwitchToLogin, embedded = false }: RegisterFormProps) {
  const { register, isLoading, error, clearError } = useAuth()
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    username: '',
    agreeToTerms: false,
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [passwordValidation, setPasswordValidation] = useState<PasswordValidation>({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false,
  })
  const [step, setStep] = useState(1) // 1: Basic Info, 2: Password & Terms

  // Password validation
  const validatePassword = (password: string): PasswordValidation => {
    return {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    }
  }

  // Form validation
  const validateStep1 = () => {
    const errors: Record<string, string> = {}
    
    if (!formData.email) {
      errors.email = 'Email es requerido'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email debe ser válido'
    }
    
    if (!formData.firstName) {
      errors.firstName = 'Nombre es requerido'
    }
    
    if (!formData.lastName) {
      errors.lastName = 'Apellido es requerido'
    }
    
    if (formData.username && formData.username.length < 3) {
      errors.username = 'Nombre de usuario debe tener al menos 3 caracteres'
    }
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const validateStep2 = () => {
    const errors: Record<string, string> = {}
    const passwordChecks = validatePassword(formData.password)
    
    if (!formData.password) {
      errors.password = 'Contraseña es requerida'
    } else if (!Object.values(passwordChecks).every(check => check)) {
      errors.password = 'La contraseña no cumple con todos los requisitos'
    }
    
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Confirmación de contraseña es requerida'
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Las contraseñas no coinciden'
    }
    
    if (!formData.agreeToTerms) {
      errors.agreeToTerms = 'Debes aceptar los términos y condiciones'
    }
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    clearError()
    
    if (step === 1) {
      if (validateStep1()) {
        setStep(2)
      }
      return
    }
    
    if (!validateStep2()) {
      return
    }

    try {
      const registerData: RegisterData = {
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        username: formData.username || undefined,
      }
      
      await register(registerData)
      onSuccess?.()
    } catch (error) {
      console.error('Registration error:', error)
    }
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Update password validation in real-time
    if (field === 'password') {
      setPasswordValidation(validatePassword(value as string))
    }
    
    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const containerClasses = embedded 
    ? "w-full max-w-md" 
    : "min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50 p-4"

  const ValidationIcon = ({ isValid }: { isValid: boolean }) => (
    <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
      isValid ? 'bg-green-100' : 'bg-gray-100'
    }`}>
      {isValid ? (
        <CheckIcon className="w-3 h-3 text-green-600" />
      ) : (
        <XMarkIcon className="w-3 h-3 text-gray-400" />
      )}
    </div>
  )

  const formContent = (
    <Card className={`w-full max-w-md ${embedded ? '' : 'shadow-2xl'}`}>
      <div className="p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full mb-4">
              <span className="text-2xl font-bold text-white">🌱</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Únete a Nuwa
            </h1>
            <p className="text-gray-600">
              Crea tu cuenta para acceder a la plataforma de carbono
            </p>
          </motion.div>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center mb-6">
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              1
            </div>
            <div className={`w-16 h-1 mx-2 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              2
            </div>
          </div>
        </div>

        {/* Error Alert */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
            >
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Register Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <AnimatePresence mode="wait">
            {step === 1 ? (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                {/* Email Field */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <AtSymbolIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className={`
                        block w-full pl-10 pr-3 py-3 border rounded-lg 
                        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                        transition-all duration-200
                        ${validationErrors.email 
                          ? 'border-red-300 bg-red-50' 
                          : 'border-gray-300 hover:border-gray-400'
                        }
                      `}
                      placeholder="tu@email.com"
                      disabled={isLoading}
                    />
                  </div>
                  {validationErrors.email && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.email}</p>
                  )}
                </div>

                {/* First Name Field */}
                <div>
                  <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <UserIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="firstName"
                      type="text"
                      value={formData.firstName}
                      onChange={(e) => handleInputChange('firstName', e.target.value)}
                      className={`
                        block w-full pl-10 pr-3 py-3 border rounded-lg 
                        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                        transition-all duration-200
                        ${validationErrors.firstName 
                          ? 'border-red-300 bg-red-50' 
                          : 'border-gray-300 hover:border-gray-400'
                        }
                      `}
                      placeholder="Tu nombre"
                      disabled={isLoading}
                    />
                  </div>
                  {validationErrors.firstName && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.firstName}</p>
                  )}
                </div>

                {/* Last Name Field */}
                <div>
                  <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                    Apellido *
                  </label>
                  <input
                    id="lastName"
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange('lastName', e.target.value)}
                    className={`
                      block w-full px-3 py-3 border rounded-lg 
                      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                      transition-all duration-200
                      ${validationErrors.lastName 
                        ? 'border-red-300 bg-red-50' 
                        : 'border-gray-300 hover:border-gray-400'
                      }
                    `}
                    placeholder="Tu apellido"
                    disabled={isLoading}
                  />
                  {validationErrors.lastName && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.lastName}</p>
                  )}
                </div>

                {/* Username Field (Optional) */}
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de usuario (opcional)
                  </label>
                  <input
                    id="username"
                    type="text"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    className={`
                      block w-full px-3 py-3 border rounded-lg 
                      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                      transition-all duration-200
                      ${validationErrors.username 
                        ? 'border-red-300 bg-red-50' 
                        : 'border-gray-300 hover:border-gray-400'
                      }
                    `}
                    placeholder="nombre_usuario"
                    disabled={isLoading}
                  />
                  {validationErrors.username && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.username}</p>
                  )}
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                {/* Password Field */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Contraseña *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LockClosedIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      className={`
                        block w-full pl-10 pr-10 py-3 border rounded-lg 
                        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                        transition-all duration-200
                        ${validationErrors.password 
                          ? 'border-red-300 bg-red-50' 
                          : 'border-gray-300 hover:border-gray-400'
                        }
                      `}
                      placeholder="••••••••"
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPassword ? (
                        <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                      ) : (
                        <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                      )}
                    </button>
                  </div>

                  {/* Password Requirements */}
                  <div className="mt-2 space-y-2">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center space-x-2">
                        <ValidationIcon isValid={passwordValidation.length} />
                        <span className={passwordValidation.length ? 'text-green-600' : 'text-gray-500'}>
                          8+ caracteres
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <ValidationIcon isValid={passwordValidation.uppercase} />
                        <span className={passwordValidation.uppercase ? 'text-green-600' : 'text-gray-500'}>
                          Mayúscula
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <ValidationIcon isValid={passwordValidation.lowercase} />
                        <span className={passwordValidation.lowercase ? 'text-green-600' : 'text-gray-500'}>
                          Minúscula
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <ValidationIcon isValid={passwordValidation.number} />
                        <span className={passwordValidation.number ? 'text-green-600' : 'text-gray-500'}>
                          Número
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 col-span-2">
                        <ValidationIcon isValid={passwordValidation.special} />
                        <span className={passwordValidation.special ? 'text-green-600' : 'text-gray-500'}>
                          Carácter especial (!@#$%^&*)
                        </span>
                      </div>
                    </div>
                  </div>

                  {validationErrors.password && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.password}</p>
                  )}
                </div>

                {/* Confirm Password Field */}
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmar Contraseña *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LockClosedIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      className={`
                        block w-full pl-10 pr-10 py-3 border rounded-lg 
                        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                        transition-all duration-200
                        ${validationErrors.confirmPassword 
                          ? 'border-red-300 bg-red-50' 
                          : 'border-gray-300 hover:border-gray-400'
                        }
                      `}
                      placeholder="••••••••"
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showConfirmPassword ? (
                        <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                      ) : (
                        <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                      )}
                    </button>
                  </div>
                  {validationErrors.confirmPassword && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.confirmPassword}</p>
                  )}
                </div>

                {/* Terms and Conditions */}
                <div>
                  <div className="flex items-start">
                    <input
                      id="agreeToTerms"
                      type="checkbox"
                      checked={formData.agreeToTerms}
                      onChange={(e) => handleInputChange('agreeToTerms', e.target.checked)}
                      className={`
                        h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1
                        ${validationErrors.agreeToTerms ? 'border-red-300' : ''}
                      `}
                      disabled={isLoading}
                    />
                    <label htmlFor="agreeToTerms" className="ml-3 block text-sm text-gray-700">
                      Acepto los{' '}
                      <Link href="/terms" className="font-medium text-blue-600 hover:text-blue-500">
                        términos y condiciones
                      </Link>{' '}
                      y la{' '}
                      <Link href="/privacy" className="font-medium text-blue-600 hover:text-blue-500">
                        política de privacidad
                      </Link>
                    </label>
                  </div>
                  {validationErrors.agreeToTerms && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.agreeToTerms}</p>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            {step === 2 && (
              <Button
                type="button"
                onClick={() => setStep(1)}
                variant="outline"
                className="flex-1"
                disabled={isLoading}
              >
                Atrás
              </Button>
            )}

            <Button
              type="submit"
              className="flex-1"
              disabled={isLoading}
              size="lg"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Registrando...
                </div>
              ) : step === 1 ? (
                'Continuar'
              ) : (
                'Crear Cuenta'
              )}
            </Button>
          </div>
        </form>

        {/* Login Link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            ¿Ya tienes una cuenta?{' '}
            {onSwitchToLogin ? (
              <button
                onClick={onSwitchToLogin}
                className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
              >
                Inicia sesión aquí
              </button>
            ) : (
              <Link
                href="/auth/login"
                className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
              >
                Inicia sesión aquí
              </Link>
            )}
          </p>
        </div>
      </div>
    </Card>
  )

  if (embedded) {
    return formContent
  }

  return (
    <div className={containerClasses}>
      {formContent}
    </div>
  )
}