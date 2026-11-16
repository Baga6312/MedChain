import { useState } from 'react';
import { AlertTriangle, Camera, Check, UserRound } from 'lucide-react';
import { request } from '../../services/http';
import { useAuth } from '../../context/AuthContext';
import { useNotify } from '../../context/NotifyContext';

export default function ProfileSettings() {
  const { user, refreshUser } = useAuth();
  const notify = useNotify();
  const [values, setValues] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    phone: user.phone || '',
    address: user.address || '',
    avatar: null,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const formData = new FormData();
      Object.entries(values).forEach(([key, value]) => {
        if (value !== null) formData.append(key, value);
      });
      await request('/auth/profile/', { method: 'PATCH', formData });
      await refreshUser();
      setValues((current) => ({ ...current, avatar: null }));
      notify('Profil mis à jour.');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="settings-card panel">
      <div className="settings-identity">
        <div className="settings-avatar">
          {user.avatar_url ? <img src={user.avatar_url} alt="" /> : <UserRound size={32} />}
          <label className="avatar-upload" title="Changer la photo">
            <Camera size={14} />
            <span className="sr-only">Changer la photo</span>
            <input aria-label="Changer la photo" type="file" accept="image/*" onChange={(event) => setValues((current) => ({ ...current, avatar: event.target.files[0] || null }))} />
          </label>
        </div>
        <div><span className="eyebrow">Compte personnel</span><h2>{user.first_name || user.email}</h2><p>{user.role === 'doctor' ? 'Profil praticien' : user.role === 'admin' ? 'Profil administrateur' : 'Profil patient'}</p></div>
      </div>
      <form className="settings-form" onSubmit={submit}>
        <div className="settings-form-grid">
          <input aria-label="Prénom" placeholder="Prénom" value={values.first_name} onChange={(event) => setValues((current) => ({ ...current, first_name: event.target.value }))} />
          <input aria-label="Nom" placeholder="Nom" value={values.last_name} onChange={(event) => setValues((current) => ({ ...current, last_name: event.target.value }))} />
          <input aria-label="Email" placeholder="Email" value={user.email} disabled />
          <input aria-label="Téléphone" placeholder="Téléphone" value={values.phone} onChange={(event) => setValues((current) => ({ ...current, phone: event.target.value }))} />
          <input className="settings-wide" aria-label="Adresse" placeholder="Adresse" value={values.address} onChange={(event) => setValues((current) => ({ ...current, address: event.target.value }))} />
        </div>
        {error && <div className="inline-error"><AlertTriangle size={16} /> {error}</div>}
        <button className="primary-button" disabled={saving}><Check size={16} /> {saving ? 'Enregistrement…' : 'Enregistrer les changements'}</button>
      </form>
    </section>
  );
}
