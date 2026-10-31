import { Navigate, Route, Routes } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import ProtectedRoute from './components/auth/ProtectedRoute';
import ResourcePage from './pages/ResourcePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OAuthCallbackPage from './pages/OAuthCallbackPage';
import AdminDashboard from './pages/AdminDashboard';
import RoleDashboard from './pages/RoleDashboard';
import { NotifyProvider } from './context/NotifyContext';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/AuthContext';

function HomeRedirect() {
  const { isAdmin } = useAuth();
  return <Navigate to={isAdmin ? '/admin' : '/dashboard'} replace />;
}

export default function App() {
  return (
    <NotifyProvider>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppShell />}>
              <Route path="/" element={<HomeRedirect />} />
              <Route path="/dashboard" element={<RoleDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/:resource" element={<ResourcePage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </NotifyProvider>
  );
}