import { LockKeyhole, ShieldCheck, UserRound } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { resources } from '../../config/resources';
import { useAuth } from '../../context/AuthContext';

export default function Sidebar() {
  const { pathname } = useLocation();
  const { logout, isAdmin, user } = useAuth();
  const navigate = useNavigate();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-mark"><LockKeyhole size={18} /></span>
        <div>
          <strong>MedChain</strong>
          <small>Health Ledger</small>
        </div>
      </div>
      <nav className="side-nav">
        {!isAdmin && (
          <button
            className={pathname === '/dashboard' ? 'active' : ''}
            onClick={() => navigate('/dashboard')}
          >
            <UserRound size={18} />
            <span>Mon espace</span>
          </button>
        )}
        {isAdmin && (
          <button
            className={pathname === '/admin' ? 'active' : ''}
            onClick={() => navigate('/admin')}
          >
            <ShieldCheck size={18} />
            <span>Administration</span>
          </button>
        )}
        {Object.entries(resources)
          .filter(([key]) => {
            if (isAdmin) return true;
            if (user?.role === 'patient') return ['doctors', 'appointments', 'medical-records'].includes(key);
            if (user?.role === 'doctor') return ['patients', 'appointments', 'medical-records'].includes(key);
            return false;
          })
          .map(([key, { label, icon: Icon }]) => (
          <button
            key={key}
            className={pathname === `/${key}` ? 'active' : ''}
            onClick={() => navigate(`/${key}`)}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
          ))}
      </nav>
      <button className="sidebar-logout" onClick={logout}><span>Déconnexion</span></button>
    </aside>
  );
}