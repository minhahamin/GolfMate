import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

import { getMe } from '../api/users';
import { clearStoredToken, getStoredToken, setStoredToken } from '../api/client';
import type { AuthResponse, User } from '../types/auth';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  loginWithAuthResponse: (response: AuthResponse) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// 앱 시작 시 저장된 토큰으로 /users/me를 호출해 로그인 상태를 복원한다.
// 토큰이 없거나 만료됐으면(401) 로그아웃 상태로 취급한다.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    getMe()
      .then(setUser)
      .catch(() => clearStoredToken())
      .finally(() => setIsLoading(false));
  }, []);

  function loginWithAuthResponse(response: AuthResponse) {
    setStoredToken(response.access_token);
    setUser(response.user);
  }

  function logout() {
    clearStoredToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, loginWithAuthResponse, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth는 AuthProvider 안에서만 사용할 수 있다.');
  }
  return context;
}
