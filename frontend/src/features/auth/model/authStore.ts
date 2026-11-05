import { create } from 'zustand';
import { setAuthContext } from '../../../shared/api/client';

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
  setSession: (token: string, user: UserSession) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,

  setSession: (token: string, user: UserSession) => {
    setAuthContext(token, user.tenantId);
    set({
      token,
      user,
      isAuthenticated: true,
    });
  },

  logout: () => {
    setAuthContext(null, null);
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },
}));
