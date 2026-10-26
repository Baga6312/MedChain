import { createContext, useContext, useState } from 'react';
import { authService } from '../services/authService';
import { tokens } from '../services/http';

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(tokens.get());

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
    },
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}