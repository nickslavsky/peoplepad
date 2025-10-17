const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';
export const API_ORIGIN = new URL(API_BASE).origin

// Helper: Decode JWT payload (lightweight, no external deps)
const decodeJwtPayload = (token: string | null): any => {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
};

// Helper: Check if token is expired (client-side, for proactive if needed)
const isTokenExpired = (token: string | null): boolean => {
  const payload = decodeJwtPayload(token);
  if (!payload?.exp) return true;
  return Date.now() >= payload.exp * 1000;
};

// Refresh function (shared)
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;
let authTokenSetter: ((token: string | null) => void) | null = null;

export const setAuthTokenSetter = (setter: (token: string | null) => void) => {
  authTokenSetter = setter;
};

export const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }), // Adjust key if backend expects differently
  });

  if (!response.ok) {
    throw new Error('Refresh failed');
  }

  const data = await response.json();
  const newAccessToken = data.access_token;
  localStorage.setItem('access_token', newAccessToken);
  if (authTokenSetter) authTokenSetter(newAccessToken);
  return newAccessToken;
};

// Main apiFetch with auto-refresh on 401
async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  let token = localStorage.getItem('access_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  let response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (response.status === 401 && token) {
    // Token likely expired; attempt refresh and retry
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = refreshAccessToken() // Assign the promise here
        .then((newToken) => {
          isRefreshing = false;
          return newToken;
        })
        .catch((err) => {
          isRefreshing = false;
          console.error('Token refresh failed:', err);
          // Force logout on refresh failure
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          if (authTokenSetter) authTokenSetter(null);
          return null; // Resolve to null on error
        })
        .finally(() => {
          refreshPromise = null; // Reset after completion (add this for cleanliness)
        });
    }

    // Await the promise (TS now knows it could be null, but since we start it above, it's set)
    const newToken = refreshPromise ? await refreshPromise : null;
    if (!newToken) {
      const error = await response.json().catch(() => ({ message: 'Authentication failed' }));
      throw new Error(error.message || 'API error after refresh');
    }

    // Retry original request with new token
    const retryHeaders: HeadersInit = {
      ...headers,
      Authorization: `Bearer ${newToken}`,
    };
    response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers: retryHeaders });
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'API error' }));
    throw new Error(error.message || 'API error');
  }
  return response.json();
}

export interface RecordCreate {
  name: string
  notes?: string
  tags: string[]
}

export interface RecordUpdate extends RecordCreate {}

export interface RecordResponse {
  id: string
  user_id: string
  name: string
  notes?: string
  tags: string[]
  created_at: string
  updated_at: string
}

export interface SearchRequest {
  query: string
  start_date?: string
  end_date?: string
  tags: string[]
}

export interface SearchResponse extends Omit<RecordResponse, 'user_id'> {
  distance: number
}

interface TagResponse {
  id: string
  name: string
}

export const getRecord = (id: string): Promise<RecordResponse> =>
  apiFetch(`/records/${id}`)

export const addRecord = (data: RecordCreate): Promise<RecordResponse> =>
  apiFetch(`/records/`, { method: 'POST', body: JSON.stringify(data) })

export const updateRecord = (id: string, data: RecordUpdate): Promise<RecordResponse> =>
  apiFetch(`/records/${id}`, { method: 'PATCH', body: JSON.stringify(data) })

export const searchRecords = (params: SearchRequest): Promise<SearchResponse[]> =>
  apiFetch(`/search/`, { method: 'POST', body: JSON.stringify(params) })

export const getTags = (): Promise<string[]> =>
  apiFetch<TagResponse[]>('/tags/').then(tags => tags.map(t => t.name))