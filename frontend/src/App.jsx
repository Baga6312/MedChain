import { useState } from 'react';
import { CheckCircle2, LockKeyhole, XCircle } from 'lucide-react';
import CrudPage from './crudPage';
import { resources } from './resources';
import './crud.css';

export default function App() {
  const [page, setPage] = useState('patients');
  const [toast, setToast] = useState(null);

  function notify(message, tone = 'success') {
    setToast({ message, tone });
    window.setTimeout(() => setToast(null), 3200);
  }

  return (
    <div className="app-shell">
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
            <button key={key} className={page === key ? 'active' : ''} onClick={() => setPage(key)}>
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        <div className="page-wrap">
          <CrudPage key={page} resource={page} notify={notify} />
        </div>
      </main>
      {toast && (
        <div className={`toast ${toast.tone}`}>
          {toast.tone === 'danger' ? <XCircle size={18} /> : <CheckCircle2 size={18} />}
          {toast.message}
        </div>
      )}
    </div>
  );
}