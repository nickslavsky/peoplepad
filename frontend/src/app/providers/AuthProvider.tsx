import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { API_ORIGIN } from '@/lib/api'
import { setAuthTokenSetter } from '@/lib/api' // Import to link setter

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
    setAuthTokenSetter(setToken);
    return () => setAuthTokenSetter(() => {}); // Cleanup
  }, []);

  const login = async () => {
    try {
      // Fetch the Google OAuth URL from your backend
      const response = await fetch('/api/auth/login')
      const data = await response.json()
      
      // Open the Google OAuth URL in a popup
      const popup = window.open(
        data.url, 
        'google-oauth',
        'width=500,height=600,left=100,top=100'
      )
      
      // Optional: Check if popup was blocked
      if (!popup) {
        alert('Please allow popups for this site to sign in with Google')
      }
    } catch (error) {
      console.error('Login failed:', error)
    }
  }

  const logout = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      }
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setToken(null)
    }
  }

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Security: Verify the message is from your backend's domain
      if (event.origin !== API_ORIGIN) {
        console.warn('Received message from unauthorized origin:', event.origin)
        return
      }
      const { access_token, refresh_token } = event.data;
      if (access_token && refresh_token) {
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
        setToken(access_token)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [])

  // Optional proactive expiry check (runs every minute; fallback if no API calls)
  useEffect(() => {
    const checkExpiry = () => {
      if (token && isTokenExpired(token)) {
        logout();
      }
    };
    const interval = setInterval(checkExpiry, 60000);
    return () => clearInterval(interval);
  }, [token]);

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

// Helper for expiry check (duplicated from api.ts to avoid cyclic import; or move to shared util)
const isTokenExpired = (token: string | null): boolean => {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return Date.now() >= payload.exp * 1000;
  } catch {
    return true;
  }
};