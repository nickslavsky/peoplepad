import { Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import LandingPage from '@/features/auth/LandingPage'
import DashboardPage from '@/features/records/DashboardPage'
import { useAuth } from '@/app/providers/AuthProvider'

const AddRecordPage = lazy(() => import('@/features/records/AddRecordPage'))
const EditRecordPage = lazy(() => import('@/features/records/EditRecordPage'))
const ViewRecordPage = lazy(() => import('@/features/records/ViewRecordPage'))

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? children : <Navigate to="/" />
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
        <Route path="/add" element={<PrivateRoute><AddRecordPage /></PrivateRoute>} />
        <Route path="/edit/:id" element={<PrivateRoute><EditRecordPage /></PrivateRoute>} />
        <Route path="/view/:id" element={<PrivateRoute><ViewRecordPage /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Suspense>
  )
}