import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { API_ORIGIN, setAuthTokenSetter, refreshAccessToken } from '@/lib/api'

interface AuthContextType {
  isAuthenticated: boolean
  login: () => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'))
  const isAuthenticated = !!token

  // Link the setter to api.ts for refresh callbacks
  useEffect(() => {
    setAuthTokenSetter(setToken)
    return () => setAuthTokenSetter(() => {})
  }, [])

  const login = async () => {
    try {
      const response = await fetch('/api/auth/login')
      const data = await response.json()
      
      const popup = window.open(
        data.url,
        'google-oauth',
        'width=500,height=600,left=100,top=100'
      )
      
      if (!popup) {
        alert('Please allow popups for this site to sign in with Google')
      }
    } catch (error) {
      console.error('Login failed:', error)
    }
  }

  const logout = async () => {
    // Get tokens before clearing them
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    
    // Clear tokens immediately to prevent further API calls
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setToken(null)

    // Try to notify backend, but don't block on failure
    if (accessToken) {
      try {
        // Use a timeout to prevent hanging
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 3000)
        
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`
          },
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)
      } catch (error) {
        // Ignore logout errors - tokens already cleared
        console.debug('Logout API call failed (non-critical):', error)
      }
    }
  }

  // Handle OAuth callback messages
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== API_ORIGIN) {
        console.warn('Received message from unauthorized origin:', event.origin)
        return
      }

      const { access_token, refresh_token } = event.data
      if (access_token && refresh_token) {
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        setToken(access_token)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [])

  // Proactive token refresh before expiry (better UX than waiting for 401)
  useEffect(() => {
    if (!token) return

    const scheduleRefresh = () => {
      const payload = decodeJwtPayload(token)
      if (!payload?.exp) return

      const expiresAt = payload.exp * 1000
      const now = Date.now()
      const timeUntilExpiry = expiresAt - now

      // Refresh 60 seconds before expiry (or immediately if already expired/close)
      const refreshIn = Math.max(0, timeUntilExpiry - 60000)

      const timeoutId = setTimeout(async () => {
        try {
          await refreshAccessToken()
          // Token will be updated via setAuthTokenSetter callback
        } catch (error) {
          console.error('Proactive token refresh failed:', error)
          // Logout on refresh failure
          logout()
        }
      }, refreshIn)

      return timeoutId
    }

    const timeoutId = scheduleRefresh()
    return () => {
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [token])

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}

// Helper: Decode JWT payload
const decodeJwtPayload = (token: string | null): any => {
  if (!token) return null
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}