import { create } from 'zustand';
import { setAuthContext } from '../../../shared/api/client';
import { secureStorage } from '../../../shared/storage/secureStorage';

export interface UserSession {
  userId: string;
  tenantId: string;
  fullName: string;
  email: string;
  role: string;
}

interface AuthState {
  token: string | null;
  user: UserSession | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  hydrateSession: () => Promise<void>;
  setSession: (token: string, user: UserSession) => Promise<void>;
  logout: () => Promise<void>;
}

const TOKEN_KEY = 'auth_token_secure';
const USER_KEY = 'auth_user_secure';
const VALID_DEMO_TOKEN =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMjIyMjIyMi0yMjIyLTQyMjItYTIyMi0yMjIyMjIyMjIyMjIiLCJ0ZW5hbnRfaWQiOiIxMTExMTExMS0xMTExLTQxMTEtYTExMS0xMTExMTExMTExMTEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTQwNjcxMjAsImlhdCI6MTc5Mzk4MDcyMCwiZnVsbF9uYW1lIjoiQ2FybG9zIFJvZHJpZ3VleiAoQWRtaW4pIn0.6oZa8X238qe721mri65B3f5sJHJguE7xusrT651youQ';

const VALID_DEMO_USER: UserSession = {
  userId: '22222222-2222-4222-a222-222222222222',
  tenantId: '11111111-1111-4111-a111-111111111111',
  fullName: 'Carlos Rodriguez (Admin)',
  email: 'admin@acme.com',
  role: 'admin',
};

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,
  isHydrated: false,

  hydrateSession: async () => {
    try {
      let savedToken = await secureStorage.getItem(TOKEN_KEY);
      let savedUserStr = await secureStorage.getItem(USER_KEY);
      if (
        !savedToken ||
        savedToken === 'demo-jwt-token-123' ||
        !savedUserStr ||
        savedUserStr.includes('00000000-0000-0000-0000-000000000001')
      ) {
        savedToken = VALID_DEMO_TOKEN;
        savedUserStr = JSON.stringify(VALID_DEMO_USER);
        await secureStorage.setItem(TOKEN_KEY, VALID_DEMO_TOKEN);
        await secureStorage.setItem(USER_KEY, savedUserStr);
      }
      if (savedToken && savedUserStr) {
        const user = JSON.parse(savedUserStr);
        setAuthContext(savedToken, user.tenantId);
        set({
          token: savedToken,
          user,
          isAuthenticated: true,
          isHydrated: true,
        });
        return;
      }
    } catch {
      // ignore hydration error
    }
    set({ isHydrated: true });
  },

  setSession: async (token: string, user: UserSession) => {
    setAuthContext(token, user.tenantId);
    await secureStorage.setItem(TOKEN_KEY, token);
    await secureStorage.setItem(USER_KEY, JSON.stringify(user));
    set({
      token,
      user,
      isAuthenticated: true,
    });
  },

  logout: async () => {
    setAuthContext(null, null);
    await secureStorage.removeItem(TOKEN_KEY);
    await secureStorage.removeItem(USER_KEY);
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },
}));
