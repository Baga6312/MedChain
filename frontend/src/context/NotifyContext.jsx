import { createContext, useCallback, useContext, useState } from 'react';
import Toast from '../components/common/Toast';

const Ctx = createContext(() => {});
export const useNotify = () => useContext(Ctx);

export function NotifyProvider({ children }) {
  const [toast, setToast] = useState(null);

  const notify = useCallback((message, tone = 'success') => {
    setToast({ message, tone });
    window.setTimeout(() => setToast(null), 3200);
  }, []);

  return (
    <Ctx.Provider value={notify}>
      {children}
      <Toast toast={toast} />
    </Ctx.Provider>
  );
}