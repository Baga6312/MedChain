import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, UserRound } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { request } from '../services/http';
import { useNotify } from '../context/NotifyContext';

const labels = {
  requested: 'Demandé',
  active: 'En cours',
  abandoned: 'Abandonné',
  completed: 'Terminé',
};

export default function RoleDashboard() {
  const { user } = useAuth();
  const notify = useNotify();
  const [episodes, setEpisodes] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [error, setError] = useState(null);
  const [requestData, setRequestData] = useState({ doctor: '', reason: '' });

  const load = useCallback(async () => {
    try {
      const episodeRows = await request('/treatment-episodes/');
      setEpisodes(episodeRows);
      if (user.role === 'patient') setDoctors(await request('/doctors/'));
    } catch (requestError) {
      setError(requestError.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function changeStatus(id, status) {
    try {
      await request(`/treatment-episodes/${id}/`, {
        method: 'PATCH',
        json: { status },
      });
      notify('Traitement mis à jour.');
      load();
    } catch (requestError) {
      notify(requestError.message, 'danger');
    }
  }

  async function requestTreatment(event) {
    event.preventDefault();
    try {
      await request('/treatment-episodes/', {
        method: 'POST',
        json: {
          doctor: Number(requestData.doctor),
          reason: requestData.reason,
        },
      });
      notify('Demande de traitement envoyée.');
      setRequestData({ doctor: '', reason: '' });
      load();
    } catch (requestError) {
      notify(requestError.message, 'danger');
    }
  }

  return (
    <>
      <div className="page-header">
        <div>
          <span className="eyebrow">{user.role === 'doctor' ? 'Espace médecin' : 'Espace patient'}</span>
          <h1>Bonjour {user.first_name || user.email}</h1>
          <p>Vos informations personnelles et vos traitements associés.</p>
        </div>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <div><h2>Mon profil</h2><p>Informations personnelles, hors dossier médical.</p></div>
          <UserRound size={20} />
        </div>
        <div className="content-grid">
          <p><strong>Nom</strong><br />{user.first_name} {user.last_name}</p>
          <p><strong>Email</strong><br />{user.email}</p>
          <p><strong>Téléphone</strong><br />{user.phone || '—'}</p>
          <p><strong>Adresse</strong><br />{user.address || '—'}</p>
        </div>
      </section>

      {error && <div className="inline-error"><AlertTriangle size={16} /> {error}</div>}
      {user.role === 'patient' && (
        <section className="panel">
          <div className="panel-heading">
            <div><h2>Demander un traitement</h2><p>Un médecin devra activer la prise en charge.</p></div>
          </div>
          <form className="modal-actions" onSubmit={requestTreatment}>
            <select
              required
              value={requestData.doctor}
              onChange={(event) => setRequestData((value) => ({ ...value, doctor: event.target.value }))}
            >
              <option value="">Choisir un médecin</option>
              {doctors.map((doctor) => (
                <option key={doctor.id} value={doctor.id}>{doctor.name} — {doctor.specialty}</option>
              ))}
            </select>
            <input
              required
              placeholder="Motif"
              value={requestData.reason}
              onChange={(event) => setRequestData((value) => ({ ...value, reason: event.target.value }))}
            />
            <button className="primary-button">Envoyer la demande</button>
          </form>
        </section>
      )}
      <section className="panel">
        <div className="panel-heading">
          <div><h2>{user.role === 'doctor' ? 'Mes patients' : 'Mes traitements'}</h2><p>Historique des prises en charge.</p></div>
        </div>
        <div className="event-list">
          {episodes.length === 0 && <p>Aucun traitement associé.</p>}
          {episodes.map((episode) => (
            <div className="event-row" key={episode.id}>
              {episode.status === 'active' ? <CheckCircle2 size={16} /> : <UserRound size={16} />}
              <div>
                <strong>{user.role === 'doctor' ? episode.patient_name : episode.doctor_name}</strong>
                <small>{episode.reason || 'Traitement'} · {labels[episode.status]}</small>
              </div>
              <div className="row-actions">
                {user.role === 'doctor' && episode.status === 'requested' && (
                  <button className="quiet-button" onClick={() => changeStatus(episode.id, 'active')}>Activer</button>
                )}
                {user.role === 'doctor' && episode.status === 'active' && (
                  <button className="quiet-button" onClick={() => changeStatus(episode.id, 'completed')}>Terminer</button>
                )}
                {user.role === 'patient' && ['requested', 'active'].includes(episode.status) && (
                  <button className="danger-button" onClick={() => changeStatus(episode.id, 'abandoned')}>Abandonner</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
