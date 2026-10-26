import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { AlertTriangle, LockKeyhole } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import OAuthButtons from '../components/auth/OAuthButtons';

export default function LoginPage() {
  const { isAuthed, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  if (isAuthed) return <Navigate to="/" replace />;

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <span className="brand-mark"><LockKeyhole size={18} /></span>
        <h1>MedChain</h1>
        <label className="field">Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="field">Mot de passe
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <div className="inline-error"><AlertTriangle size={16} /> {error}</div>}
        <button className="primary-button" disabled={busy}>{busy ? 'Connexion…' : 'Se connecter'}</button>
        <OAuthButtons />
        <p>Pas de compte ? <Link to="/register">Créer un compte</Link></p>
      </form>
    </div>
  );
}