// API Configuration for Valkyrie PTaaS Platform
// Handles both development (proxy) and production (direct) API calls

const getApiBaseUrl = (): string => {
  // In production, use the VITE_API_URL environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // In development, use the Vite proxy (empty string = same origin)
  // The proxy is configured in vite.config.ts to forward /api/* to localhost:8000
  if (import.meta.env.DEV) {
    return '/api';
  }

  // Fallback for production if env var not set
  // This allows the app to work if deployed on same domain as API
  return '/api';
};

export const API_BASE_URL = getApiBaseUrl();

// Helper to construct full API URLs
export const apiUrl = (path: string): string => {
  // Remove leading slash from path if present to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_BASE_URL}/${cleanPath}`;
};

export default API_BASE_URL;
