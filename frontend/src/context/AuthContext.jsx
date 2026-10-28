import { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/authService';
import { request, tokens } from '../services/http';

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(tokens.get());
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    request('/auth/me/')
      .then(setUser)
      .catch(() => setUser(null));
  }, [token]);

  const value = {
    isAuthed: !!token,
    login: async (email, password) => {
      await authService.login(email, password);
      setToken(tokens.get());
    },
    register: authService.register,
    acceptToken: (t) => {
      tokens.set(t);
      setToken(t);
    },
    logout: () => {
      authService.logout();
      setToken(null);
      setUser(null);
    },
  };
  return <Ctx.Provider value={{ ...value, user, isAdmin: user?.role === 'admin' || user?.is_staff }}>
    {children}
  </Ctx.Provider>;
}