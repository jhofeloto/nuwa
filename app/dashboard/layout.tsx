'use client'

import { ProtectedRoute } from '@/app/ui/auth/protected-route'
import { ReactNode } from 'react'

interface DashboardLayoutProps {
  children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <ProtectedRoute>
      {children}
    </ProtectedRoute>
  )
}