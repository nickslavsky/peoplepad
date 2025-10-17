import { Button } from '@/components/ui/button'
import { useAuth } from '@/app/providers/AuthProvider'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'

export default function LandingPage() {
  const { isAuthenticated, login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard')
  }, [isAuthenticated, navigate])

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-4xl font-bold mb-8">PeoplePad</h1>
      <Button onClick={login}>Sign in with Google</Button>
    </div>
  )
}