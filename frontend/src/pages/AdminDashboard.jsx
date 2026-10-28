import { useCallback, useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  UserRound,
  UsersRound,
  Plus,
  Search,
  X,
} from 'lucide-react';
import { Navigate } from 'react-router-dom';
import { adminService } from '../services/adminService';
import { useAuth } from '../context/AuthContext';
import { useNotify } from '../context/NotifyContext';

const cards = [
  ['users', 'Utilisateurs', UsersRound],
  ['patients', 'Patients', UserRound],
  ['doctors', 'Médecins', ShieldCheck],
  ['open_alerts', 'Alertes ouvertes', AlertTriangle],
  ['new_users', 'Nouveaux comptes', UsersRound],
  ['pending_users', 'Comptes à valider', AlertTriangle],
];

export default function AdminDashboard() {
  const { isAdmin } = useAuth();
  const notify = useNotify();
  const [data, setData] = useState(null);
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const load = useCallback(async () => {
    try {
      const [dashboard, userRows, auditRows, alertRows] = await Promise.all([
        adminService.dashboard(),
        adminService.users(query),
        adminService.auditLogs(),
        adminService.securityAlerts(),
      ]);
      setData(dashboard);
      setUsers(userRows);
      setLogs(auditRows);
      setAlerts(alertRows);
    } catch (requestError) {
      setError(requestError.message);
    }
  }, [query]);

  useEffect(() => {
    if (isAdmin) load();
  }, [isAdmin, load]);

  if (!isAdmin) return <Navigate to="/patients" replace />;
  if (error) return <div className="inline-error"><AlertTriangle size={16} /> {error}</div>;
  if (!data) return <p>Chargement du tableau de bord…</p>;

  async function toggleUser(user) {
    try {
      await adminService.updateUser({ user_id: user.id, is_active: !user.is_active });
      notify(user.is_active ? 'Compte désactivé.' : 'Compte activé.');
      load();
    } catch (requestError) {
      notify(requestError.message, 'danger');
    }
  }

  async function changeRole(user, role) {
    try {
      await adminService.updateUser({ user_id: user.id, role });
      notify('Rôle modifié.');
      load();
    } catch (requestError) {
      notify(requestError.message, 'danger');
    }
  }

  async function createUser(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await adminService.createUser(Object.fromEntries(form.entries()));
      notify('Compte créé avec le rôle patient par défaut.');
      setShowCreate(false);
      load();
    } catch (requestError) {
      notify(requestError.message, 'danger');
    }
  }

  async function resolveAlert(id) {
    try {
      await adminService.resolveAlert(id);
      notify('Alerte marquée comme résolue.');
      load();
    } catch (requestError) {
      notify(requestError.message, 'danger');
    }
  }

  return (
    <>
      <div className="page-header">
        <div>
          <span className="eyebrow">Supervision</span>
          <h1>Administration</h1>
          <p>Vue globale de l’activité et de la sécurité de MedChain.</p>
        </div>
        <div className="admin-header-actions">
          <div className="api-status"><Activity size={15} /> API opérationnelle</div>
          <button className="primary-button" onClick={() => setShowCreate(true)}><Plus size={16} /> Ajouter un utilisateur</button>
        </div>
      </div>

      <div className="metrics-grid four">
        {cards.map(([key, label, Icon]) => (
          <div className={`metric-card ${key === 'open_alerts' ? 'danger' : 'teal'}`} key={key}>
            <div className="metric-top"><span>{label}</span><Icon size={18} /></div>
            <strong>{data[key]}</strong>
            <small>{key === 'open_alerts' ? 'À traiter' : 'Enregistrés'}</small>
          </div>
        ))}
      </div>

      <div className="admin-grid">
        <section className="panel span-2">
          <div className="panel-heading">
            <div><h2>Utilisateurs</h2><p>Activation, rôles et supervision des comptes.</p></div>
            <label className="search-field"><Search size={15} /><input placeholder="Rechercher..." value={query} onChange={(event) => setQuery(event.target.value)} /></label>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Utilisateur</th><th>Rôle</th><th>Inscription</th><th>Statut</th><th /></tr></thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.first_name} {user.last_name}<br /><small>{user.email}</small></td>
                    <td>
                      <select value={user.role} onChange={(event) => changeRole(user, event.target.value)}>
                        <option value="patient">Patient</option>
                        <option value="doctor">Médecin</option>
                        <option value="admin">Administrateur</option>
                      </select>
                    </td>
                    <td>{new Date(user.date_joined).toLocaleDateString('fr-FR')}</td>
                    <td>{user.is_active ? 'Actif' : 'Désactivé'}</td>
                    <td><button className={user.is_active ? 'danger-button' : 'quiet-button'} onClick={() => toggleUser(user)}>
                      {user.is_active ? 'Désactiver' : 'Activer'}
                    </button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading"><div><h2>Alertes de sécurité</h2><p>Événements nécessitant une action.</p></div></div>
          <div className="event-list">
            {alerts.length === 0 && <p>Aucune alerte.</p>}
            {alerts.map((alert) => (
              <div className="event-row" key={alert.id}>
                <AlertTriangle size={16} />
                <div><strong>{alert.title}</strong><small>{alert.detail}</small></div>
                {alert.status === 'open' && <button className="text-button" onClick={() => resolveAlert(alert.id)}>Résoudre</button>}
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading"><div><h2>Dernières activités</h2><p>Traçabilité des actions sensibles.</p></div></div>
          <div className="event-list">
            {logs.slice(0, 6).map((log) => (
              <div className="event-row" key={log.id}>
                <CheckCircle2 size={16} />
                <div><strong>{log.action}</strong><small>{log.actor} · {log.target}</small></div>
              </div>
            ))}
          </div>
        </section>
      </div>
      {showCreate && (
        <div className="modal-backdrop" onClick={() => setShowCreate(false)}>
          <form className="modal" onClick={(event) => event.stopPropagation()} onSubmit={createUser}>
            <div className="modal-heading"><h2>Créer un utilisateur</h2><button type="button" className="icon-button" onClick={() => setShowCreate(false)}><X size={18} /></button></div>
            <label className="field">Prénom<input name="first_name" required /></label>
            <label className="field">Nom<input name="last_name" required /></label>
            <label className="field">Email<input name="email" type="email" required /></label>
            <label className="field">Mot de passe<input name="password" type="password" required /></label>
            <p className="form-hint">Le compte sera créé avec le rôle Patient. Vous pourrez ensuite modifier son rôle dans le tableau.</p>
            <div className="modal-actions"><button type="button" className="quiet-button" onClick={() => setShowCreate(false)}>Annuler</button><button className="primary-button">Créer le compte</button></div>
          </form>
        </div>
      )}
    </>
  );
}
