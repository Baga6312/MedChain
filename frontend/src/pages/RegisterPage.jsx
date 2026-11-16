import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertTriangle, LockKeyhole } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNotify } from '../context/NotifyContext';
import OAuthButtons from '../components/auth/OAuthButtons';
import ThemeToggle from '../components/common/ThemeToggle';

const FIELDS = [
  ['first_name', 'Prénom', 'text'],
  ['last_name', 'Nom', 'text'],
  ['email', 'Email', 'email'],
  ['phone', 'Téléphone', 'tel'],
  ['address', 'Adresse', 'text'],
  ['password', 'Mot de passe', 'password'],
  ['password2', 'Confirmer le mot de passe', 'password'],
];

export default function RegisterPage() {
  const { register } = useAuth();
  const notify = useNotify();
  const navigate = useNavigate();
  const [v, setV] = useState(Object.fromEntries(FIELDS.map(([k]) => [k, ''])));
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    if (v.password !== v.password2) return setError('Les mots de passe ne correspondent pas.');
    setBusy(true);
    setError(null);
    try {
      await register(v);
      notify('Compte créé. Connectez-vous.');
      navigate('/login');
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <ThemeToggle />
      <form className="auth-card" onSubmit={submit}>
        <span className="brand-mark"><LockKeyhole size={18} /></span>
        <h1>Créer un compte</h1>
        {FIELDS.map(([k, label, type]) => (
          <label className="field" key={k}>
            <input aria-label={label} placeholder={label} type={type} required={k !== 'phone'} value={v[k]}
              onChange={(e) => setV({ ...v, [k]: e.target.value })} />
          </label>
        ))}
        {error && <div className="inline-error"><AlertTriangle size={16} /> {error}</div>}
        <button className="primary-button" disabled={busy}>{busy ? 'Envoi…' : "S'inscrire"}</button>
        <OAuthButtons />
        <p>Déjà inscrit ? <Link to="/login">Se connecter</Link></p>
      </form>
    </div>
  );
}