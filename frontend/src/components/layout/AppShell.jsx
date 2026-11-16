import { Outlet } from 'react-router-dom';
import { Bell, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useAuth } from '../../context/AuthContext';
import ThemeToggle from '../common/ThemeToggle';

export default function AppShell() {
  const { user } = useAuth();
  const navigate = useNavigate();
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>MedChain</span><ChevronRight size={14} /><strong>Console clinique</strong></div>
          <div className="topbar-actions">
            <span className="network-status"><span /> Réseau sécurisé</span>
            <ThemeToggle />
            <button className="icon-button" type="button" aria-label="Notifications"><Bell size={17} /><span className="notification-badge">2</span></button>
            <button className="shell-user" type="button" aria-label="Ouvrir les paramètres du compte" onClick={() => navigate('/settings')}><span className="avatar avatar-image">{user?.avatar_url ? <img src={user.avatar_url} alt="" /> : (user?.first_name || user?.email || 'M').slice(0, 1).toUpperCase()}</span><span><strong>{user?.first_name || user?.email}</strong><small>{user?.role === 'admin' ? 'Administrateur' : user?.role === 'doctor' ? 'Praticien vérifié' : 'Espace patient'}</small></span></button>
          </div>
        </header>
        <div className="page-wrap">
          <Outlet />
        </div>
      </main>
    </div>
  );
}