import { LockKeyhole } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { resources } from '../../config/resources';
import { useAuth } from '../../context/AuthContext';

export default function Sidebar() {
  const { pathname } = useLocation();
  const { logout } = useAuth();
  const navigate = useNavigate();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-mark"><LockKeyhole size={18} /></span>
        <div>
          <strong>MedChain</strong>
          <small>Healthcare API</small>
        </div>
      </div>
      <nav className="side-nav">
        {Object.entries(resources).map(([key, { label, icon: Icon }]) => (
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
      <button className="quiet-button" onClick={logout}>Déconnexion</button>
    </aside>
  );
}