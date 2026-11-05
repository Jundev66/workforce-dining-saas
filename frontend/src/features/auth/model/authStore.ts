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

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,
  isHydrated: false,

  hydrateSession: async () => {
    try {
      const savedToken = await secureStorage.getItem(TOKEN_KEY);
      const savedUserStr = await secureStorage.getItem(USER_KEY);
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
