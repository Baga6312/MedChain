import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, Circle, Flag, Link2, ShieldAlert, ShieldCheck, UserRound } from 'lucide-react';
import IntegrityDrawer from '../components/treatment/IntegrityDrawer';
import { useAuth } from '../context/AuthContext';
import { request } from '../services/http';
import { useNotify } from '../context/NotifyContext';

const labels = {
  requested: 'Demandé',
  active: 'En cours',
  abandoned: 'Abandonné',
  completed: 'Terminé',
};
const phaseLabels = {
  pending: 'À venir',
  active: 'En cours',
  completed: 'Terminée',
  failed: 'Échec',
  skipped: 'Ignorée',
};
const eventLabels = {
  consultation: 'Consultation',
  diagnosis: 'Diagnostic',
  prescription: 'Prescription',
  test: 'Examen',
  result: 'Résultat',
  follow_up: 'Suivi',
  phase_failed: 'Échec de phase',
  phase_completed: 'Phase terminée',
  note: 'Note',
};

const integrityLabels = {
  verified: 'Enregistrement vérifié',
  pending: 'Vérification en attente',
  unavailable: 'Vérification indisponible',
};

export default function RoleDashboard() {
  const { user, refreshUser } = useAuth();
  const notify = useNotify();
  const [episodes, setEpisodes] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [error, setError] = useState(null);
  const [requestData, setRequestData] = useState({ doctor: '', reason: '' });
  const [timelines, setTimelines] = useState({});
  const [expandedEpisode, setExpandedEpisode] = useState(null);
  const [selectedPhase, setSelectedPhase] = useState({});
  const [phaseData, setPhaseData] = useState({ name: '', summary: '' });
  const [eventData, setEventData] = useState({ title: '', description: '', result: '', event_type: 'note', treatment_phase: '' });
  const [profileData, setProfileData] = useState({ first_name: user.first_name || '', last_name: user.last_name || '', phone: user.phone || '', address: user.address || '', avatar: null });
  const [profileSaving, setProfileSaving] = useState(false);
  const [integrity, setIntegrity] = useState({});
  const [integrityEpisode, setIntegrityEpisode] = useState(null);

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

  async function saveProfile(event) {
    event.preventDefault();
    setProfileSaving(true);
    try {
      const formData = new FormData();
      Object.entries(profileData).forEach(([key, value]) => {
        if (value !== null) formData.append(key, value);
      });
      await request('/auth/profile/', { method: 'PATCH', formData });
      await refreshUser();
      setProfileData((value) => ({ ...value, avatar: null }));
      notify('Profil mis à jour.');
    } catch (requestError) {
      notify(requestError.message, 'danger');
    } finally {
      setProfileSaving(false);
    }
  }

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

  async function toggleTimeline(id) {
      if (expandedEpisode === id) {
        setExpandedEpisode(null);
        return;
      }
      setExpandedEpisode(id);
      if (!timelines[id]) {
        try {
          const timeline = await request(`/treatment-episodes/${id}/timeline/`);
          setTimelines((value) => ({ ...value, [id]: timeline }));
          setIntegrity((value) => ({ ...value, [id]: timeline.integrity }));
        } catch (requestError) {
          notify(requestError.message, 'danger');
        }
      }
      if (!integrity[id]) {
        try {
          const integrityData = await request(`/treatment-episodes/${id}/integrity/`);
          setIntegrity((value) => ({ ...value, [id]: integrityData }));
        } catch (requestError) {
          notify(requestError.message, 'danger');
        }
      }
    }

  async function createPhase(event, episodeId) {
      event.preventDefault();
      try {
        await request(`/treatment-episodes/${episodeId}/phases/`, { method: 'POST', json: phaseData });
        notify('Phase ajoutée.');
        setPhaseData({ name: '', summary: '' });
        const timeline = await request(`/treatment-episodes/${episodeId}/timeline/`);
        setTimelines((value) => ({ ...value, [episodeId]: timeline }));
        setIntegrity((value) => ({ ...value, [episodeId]: timeline.integrity }));
      } catch (requestError) {
        notify(requestError.message, 'danger');
      }
    }

  async function createEvent(event, episodeId) {
      event.preventDefault();
      try {
        await request(`/treatment-episodes/${episodeId}/events/`, {
          method: 'POST',
          json: { ...eventData, treatment_phase: eventData.treatment_phase || null },
        });
        notify('Événement ajouté.');
        setEventData({ title: '', description: '', result: '', event_type: 'note', treatment_phase: '' });
        const timeline = await request(`/treatment-episodes/${episodeId}/timeline/`);
        setTimelines((value) => ({ ...value, [episodeId]: timeline }));
        setIntegrity((value) => ({ ...value, [episodeId]: timeline.integrity }));
      } catch (requestError) {
        notify(requestError.message, 'danger');
    }
  }

  async function failPhase(episodeId, phaseId) {
    const reason = window.prompt('Pourquoi cette phase a-t-elle échoué ?');
    if (!reason || !reason.trim()) return;
    try {
      await request(`/treatment-episodes/${episodeId}/phases/${phaseId}/`, {
        method: 'PATCH',
        json: { status: 'failed', failure_reason: reason.trim() },
      });
      notify('Phase marquée comme échouée.');
      const timeline = await request(`/treatment-episodes/${episodeId}/timeline/`);
      setTimelines((value) => ({ ...value, [episodeId]: timeline }));
      setIntegrity((value) => ({ ...value, [episodeId]: timeline.integrity }));
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
        <form className="profile-settings" onSubmit={saveProfile}>
          <div className="profile-avatar-preview">
            {user.avatar_url ? <img src={user.avatar_url} alt="Avatar du profil" /> : <UserRound size={26} />}
          </div>
          <label><span className="sr-only">Photo de profil</span><input aria-label="Photo de profil" type="file" accept="image/*" onChange={(event) => setProfileData((value) => ({ ...value, avatar: event.target.files[0] || null }))} /></label>
          <div className="profile-fields">
            <label><input aria-label="Prénom" placeholder="Prénom" value={profileData.first_name} onChange={(event) => setProfileData((value) => ({ ...value, first_name: event.target.value }))} /></label>
            <label><input aria-label="Nom" placeholder="Nom" value={profileData.last_name} onChange={(event) => setProfileData((value) => ({ ...value, last_name: event.target.value }))} /></label>
            <label><input aria-label="Email" placeholder="Email" value={user.email} disabled /></label>
            <label><input aria-label="Téléphone" placeholder="Téléphone" value={profileData.phone} onChange={(event) => setProfileData((value) => ({ ...value, phone: event.target.value }))} /></label>
            <label className="profile-wide"><input aria-label="Adresse" placeholder="Adresse" value={profileData.address} onChange={(event) => setProfileData((value) => ({ ...value, address: event.target.value }))} /></label>
          </div>
          <button className="primary-button" disabled={profileSaving}>{profileSaving ? 'Enregistrement…' : 'Enregistrer le profil'}</button>
        </form>
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
            <div className="treatment-card" key={episode.id}>
              <div className="event-row">
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
                  <button className="text-button" onClick={() => toggleTimeline(episode.id)}>
                    Timeline {expandedEpisode === episode.id ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                  </button>
                </div>
              </div>
              {expandedEpisode === episode.id && timelines[episode.id] && (
                <div className="treatment-timeline">
                  {(() => {
                    const integrityData = integrity[episode.id] || timelines[episode.id].integrity || {
                      status: 'pending',
                      errors: [],
                      chains: [],
                    };
                    return (
                    <div className={`integrity-summary ${integrityData.status}`}>
                      <div className="integrity-summary-main">
                        {integrityData.status === 'verified' ? <ShieldCheck size={18} /> : <ShieldAlert size={18} />}
                        <div>
                          <strong>{integrityLabels[integrityData.status]}</strong>
                          <small>
                            {integrityData.status === 'verified'
                              ? 'Les blocs et les ancrages blockchain correspondent.'
                              : integrityData.errors[0] || 'Les données sont conservées, mais nécessitent encore une vérification.'}
                          </small>
                        </div>
                      </div>
                      <button className="secondary-button" type="button" disabled={!integrity[episode.id]} onClick={() => setIntegrityEpisode(episode.id)}>
                        <Link2 size={14} /> Détails
                      </button>
                    </div>
                    );
                  })()}
                  {timelines[episode.id].phases.length === 0 && <p className="timeline-empty">Aucune phase pour le moment.</p>}
                  {timelines[episode.id].phases.length > 0 && (
                    <>
                      <div className="treatment-chain" aria-label="Progression du traitement">
                        {timelines[episode.id].phases.map((phase, index) => (
                          <div className="chain-segment" key={phase.id}>
                            <button
                              className={`chain-node ${phase.status} ${selectedPhase[episode.id] === phase.id ? 'selected' : ''}`}
                              onClick={() => setSelectedPhase((value) => ({ ...value, [episode.id]: phase.id }))}
                              type="button"
                              title={`Afficher ${phase.name}`}
                            >
                              <span className="chain-node-icon">
                                {phase.status === 'completed' ? <CheckCircle2 size={17} /> : phase.status === 'failed' ? <Flag size={16} /> : <Circle size={13} />}
                              </span>
                              <span className="chain-node-number">{phase.sequence_number}</span>
                              <strong>{phase.name}</strong>
                              <small>{phaseLabels[phase.status]}</small>
                            </button>
                            {index < timelines[episode.id].phases.length - 1 && <span className={`chain-connector ${phase.status === 'completed' ? 'passed' : ''}`} aria-hidden="true" />}
                          </div>
                        ))}
                      </div>
                      {(() => {
                        const phase = timelines[episode.id].phases.find((item) => item.id === (selectedPhase[episode.id] || timelines[episode.id].phases[0].id)) || timelines[episode.id].phases[0];
                        const phaseEvents = timelines[episode.id].events.filter((item) => item.treatment_phase === phase.id);
                        return (
                          <div className={`chain-details ${phase.status}`}>
                            <div className="timeline-phase-heading">
                              <strong>Étape {phase.sequence_number} — {phase.name}</strong>
                              <span className={`phase-badge ${phase.status}`}>{phaseLabels[phase.status]}</span>
                            </div>
                            {phase.summary && <p>{phase.summary}</p>}
                            {phase.failure_reason && <p className="timeline-failure"><Flag size={14} /> {phase.failure_reason}</p>}
                            {user.role === 'doctor' && !['failed', 'completed', 'skipped'].includes(phase.status) && (
                              <button className="danger-button phase-failure-button" onClick={() => failPhase(episode.id, phase.id)} type="button">
                                <Flag size={13} /> Marquer en échec
                              </button>
                            )}
                            {phaseEvents.length > 0 ? phaseEvents.map((item) => (
                              <div className="timeline-event" key={item.event_id}>
                                <strong>{eventLabels[item.event_type] || item.event_type}: {item.title}</strong>
                                <p>{item.description}</p>
                                {item.result && <small>Résultat : {item.result}</small>}
                              </div>
                            )) : <p className="timeline-empty">Aucun événement pour cette étape.</p>}
                          </div>
                        );
                      })()}
                    </>
                  )}
                  {user.role === 'doctor' && (
                    <form className="timeline-form" onSubmit={(event) => createPhase(event, episode.id)}>
                      <strong>Ajouter une phase</strong>
                      <input required placeholder="Nom de la phase" value={phaseData.name} onChange={(event) => setPhaseData((value) => ({ ...value, name: event.target.value }))} />
                      <input placeholder="Résumé" value={phaseData.summary} onChange={(event) => setPhaseData((value) => ({ ...value, summary: event.target.value }))} />
                      <button className="quiet-button">Ajouter</button>
                    </form>
                  )}
                  <form className="timeline-form" onSubmit={(event) => createEvent(event, episode.id)}>
                    <strong>{user.role === 'doctor' ? 'Ajouter un événement clinique' : 'Ajouter une note ou un résultat'}</strong>
                    <select value={eventData.event_type} onChange={(event) => setEventData((value) => ({ ...value, event_type: event.target.value }))}>
                      {user.role === 'patient' ? <><option value="note">Note</option><option value="result">Résultat</option></> : Object.entries(eventLabels).filter(([key]) => !['phase_failed', 'phase_completed'].includes(key)).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
                    </select>
                    {timelines[episode.id].phases.length > 0 && <select value={eventData.treatment_phase} onChange={(event) => setEventData((value) => ({ ...value, treatment_phase: event.target.value }))}><option value="">Phase (optionnel)</option>{timelines[episode.id].phases.map((phase) => <option key={phase.id} value={phase.id}>{phase.sequence_number}. {phase.name}</option>)}</select>}
                    <input required placeholder="Titre" value={eventData.title} onChange={(event) => setEventData((value) => ({ ...value, title: event.target.value }))} />
                    <input required placeholder="Description" value={eventData.description} onChange={(event) => setEventData((value) => ({ ...value, description: event.target.value }))} />
                    <input placeholder="Résultat (optionnel)" value={eventData.result} onChange={(event) => setEventData((value) => ({ ...value, result: event.target.value }))} />
                    <button className="primary-button">Ajouter</button>
                  </form>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
      {integrityEpisode && integrity[integrityEpisode] && (
        <IntegrityDrawer data={integrity[integrityEpisode]} onClose={() => setIntegrityEpisode(null)} />
      )}
    </>
  );
}
