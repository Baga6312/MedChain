import { Outlet } from 'react-router-dom';
import { Bell, ChevronRight, Search } from 'lucide-react';
import Sidebar from './Sidebar';
import { useAuth } from '../../context/AuthContext';
import ThemeToggle from '../common/ThemeToggle';

export default function AppShell() {
  const { user } = useAuth();
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>MedChain</span><ChevronRight size={14} /><strong>Console clinique</strong></div>
          <div className="topbar-actions">
            <label className="shell-search"><Search size={15} /><input placeholder="Rechercher un dossier..." /></label>
            <span className="network-status"><span /> Réseau sécurisé</span>
            <ThemeToggle />
            <button className="icon-button" type="button" aria-label="Notifications"><Bell size={17} /><span className="notification-badge">2</span></button>
            <div className="shell-user"><span className="avatar">{(user?.first_name || user?.email || 'M').slice(0, 1).toUpperCase()}</span><span><strong>{user?.first_name || user?.email}</strong><small>{user?.role === 'admin' ? 'Administrateur' : user?.role === 'doctor' ? 'Praticien vérifié' : 'Espace patient'}</small></span></div>
          </div>
        </header>
        <div className="page-wrap">
          <Outlet />
        </div>
      </main>
    </div>
  );
}