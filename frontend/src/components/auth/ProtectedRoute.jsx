import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute() {
  const { isAuthed, authReady } = useAuth();
  if (!isAuthed) return <Navigate to="/login" replace />;
  if (!authReady) return <p>Chargement du profil…</p>;
  return <Outlet />;
}