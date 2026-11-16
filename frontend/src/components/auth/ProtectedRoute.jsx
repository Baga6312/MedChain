import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoadingState from '../common/LoadingState';

export default function ProtectedRoute() {
  const { isAuthed, authReady } = useAuth();
  if (!isAuthed) return <Navigate to="/login" replace />;
  if (!authReady) return <LoadingState label="Chargement du profil…" />;
  return <Outlet />;
}