'use client'

import { useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { LoginForm } from './login-form'
import { RegisterForm } from './register-form'
import { motion, AnimatePresence } from 'framer-motion'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  defaultView?: 'login' | 'register'
  onAuthSuccess?: () => void
}

export function AuthModal({ 
  isOpen, 
  onClose, 
  defaultView = 'login', 
  onAuthSuccess 
}: AuthModalProps) {
  const [currentView, setCurrentView] = useState<'login' | 'register'>(defaultView)

  const handleAuthSuccess = () => {
    onAuthSuccess?.()
    onClose()
  }

  const handleSwitchView = () => {
    setCurrentView(currentView === 'login' ? 'register' : 'login')
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                {/* Close Button */}
                <div className="absolute right-4 top-4 z-10">
                  <button
                    onClick={onClose}
                    className="rounded-full bg-white/80 p-2 text-gray-400 hover:text-gray-600 hover:bg-white transition-all duration-200"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>

                {/* Form Content */}
                <AnimatePresence mode="wait">
                  {currentView === 'login' ? (
                    <motion.div
                      key="login"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <LoginForm
                        onSuccess={handleAuthSuccess}
                        onSwitchToRegister={handleSwitchView}
                        embedded
                      />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="register"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <RegisterForm
                        onSuccess={handleAuthSuccess}
                        onSwitchToLogin={handleSwitchView}
                        embedded
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}