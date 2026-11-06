import { Platform } from 'react-native';

export interface ApiErrorResponse {
  detail: string;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

const DEFAULT_PORT = '8001';
const DEFAULT_HOST = Platform.OS === 'android' ? `http://10.0.2.2:${DEFAULT_PORT}` : `http://localhost:${DEFAULT_PORT}`;
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || `${DEFAULT_HOST}/api/v1`;

let authToken: string | null = null;
let activeTenantId: string | null = null;

export const setAuthContext = (token: string | null, tenantId: string | null) => {
  authToken = token;
  activeTenantId = tenantId;
};

function generateUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const method = (options.method || 'GET').toUpperCase();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  if (activeTenantId) {
    headers['X-Tenant-ID'] = activeTenantId;
  }

  // Idempotency protection for mutations
  if (['POST', 'PUT', 'PATCH'].includes(method) && !headers['X-Idempotency-Key']) {
    headers['X-Idempotency-Key'] = generateUUID();
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      // ignore json parse error
    }
    throw new ApiError(response.status, errorMsg);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
