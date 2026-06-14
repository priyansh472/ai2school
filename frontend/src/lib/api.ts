import { useAuthStore } from '../store/authStore';

const BASE_URL = '/api/v1';

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = useAuthStore.getState().token;
  
  // Default headers
  let headers: Record<string, string> = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  // Only set Content-Type to JSON if it's not explicitly removed or overridden
  if (options.headers) {
    headers = { ...headers, ...(options.headers as Record<string, string>) };
  } else {
    headers['Content-Type'] = 'application/json';
  }

  // If a header is explicitly set to empty string or null-like, remove it
  // This allows the browser to auto-set boundaries for FormData
  if (headers['Content-Type'] === '') {
    delete headers['Content-Type'];
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    useAuthStore.getState().logout();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  let data;
  try {
    const text = await response.text();
    data = text ? JSON.parse(text) : {};
  } catch (e) {
    data = { detail: `Server error (${response.status})` };
  }

  if (!response.ok) {
    throw new Error(data.detail || data.message || 'API Error');
  }

  return data;
}

export const api = {
  get: (endpoint: string, options?: RequestInit) => 
    fetchWithAuth(endpoint, { ...options, method: 'GET' }),
    
  post: (endpoint: string, body: any, options?: RequestInit) => {
    const isFormData = body instanceof FormData;
    const isUrlEncoded = body instanceof URLSearchParams;
    
    let headers: Record<string, string> = {};
    if (isFormData) {
      headers['Content-Type'] = ''; // Let browser set multipart/form-data with boundary
    } else if (isUrlEncoded) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded';
    } else {
      headers['Content-Type'] = 'application/json';
    }

    return fetchWithAuth(endpoint, { 
      ...options, 
      method: 'POST', 
      body: isFormData || isUrlEncoded ? body : JSON.stringify(body),
      headers: { ...headers, ...(options?.headers as Record<string, string>) }
    });
  },
    
  put: (endpoint: string, body: any, options?: RequestInit) => 
    fetchWithAuth(endpoint, { 
      ...options, 
      method: 'PUT', 
      body: JSON.stringify(body),
      headers: { 'Content-Type': 'application/json', ...(options?.headers as Record<string, string>) }
    }),
    
  delete: (endpoint: string, options?: RequestInit) => 
    fetchWithAuth(endpoint, { ...options, method: 'DELETE' }),
};
