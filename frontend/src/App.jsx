import { useState } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronRight,
  ClipboardList,
  Clock3,
  FileClock,
  FileHeart,
  LayoutDashboard,
  LockKeyhole,
  LogOut,
  Menu,
  Plus,
  Search,
  ShieldCheck,
  Stethoscope,
  UserRound,
  UsersRound,
  X,
  XCircle,
} from 'lucide-react';

const roles = {
  patient: { label: 'Patient', user: 'Marc Durand', username: 'patient1', subtitle: 'Dossier personnel', icon: UserRound },
  doctor: { label: 'Médecin', user: 'Dr. Priya Patel', username: 'doctor1', subtitle: 'Cardiologie clinique', icon: Stethoscope },
  admin: { label: 'Administrateur', user: 'Sophie Martin', username: 'admin', subtitle: 'Supervision sécurité', icon: ShieldCheck },
};

const patientData = {
  appointments: [
    { date: '26 mars 2025', time: '14:30', doctor: 'Dr. Priya Patel', type: 'Consultation cardiologie', status: 'Confirmé' },
    { date: '02 avril 2025', time: '09:00', doctor: 'Dr. Julien Martin', type: 'Suivi général', status: 'À venir' },
    { date: '18 avril 2025', time: '11:15', doctor: 'Dr. Sarah Benali', type: 'Imagerie médicale', status: 'À confirmer' },
  ],
  doctors: [
    { initials: 'PP', name: 'Dr. Priya Patel', specialty: 'Cardiologie', scope: 'Dossier complet', active: true },
    { initials: 'JM', name: 'Dr. Julien Martin', specialty: 'Médecine générale', scope: 'Consultations seules', active: true },
    { initials: 'SB', name: 'Dr. Sarah Benali', specialty: 'Radiologie', scope: 'Biologie & échographies', active: false },
  ],
};

const doctorPatients = [
  { initials: 'MD', name: 'Marc Durand', id: '#PT-84920', access: 'Complet', lastAccess: 'Aujourd’hui, 09:42', state: 'Actif' },
  { initials: 'EM', name: 'Éléonore Mercier', id: '#PT-39102', access: 'Biologie & ECG', lastAccess: 'Hier, 16:20', state: 'Actif' },
  { initials: 'TL', name: 'Thomas Leroy', id: '#PT-55214', access: 'Consultations', lastAccess: '12 mars 2025', state: 'Actif' },
];

const auditEvents = [
  { actor: 'Dr. Priya Patel', role: 'Médecin', action: 'Consultation dossier', date: 'Aujourd’hui, 09:42', result: 'Autorisé', tone: 'success' },
  { actor: 'Marc Durand', role: 'Patient', action: 'Autorisation médecin', date: 'Aujourd’hui, 08:15', result: 'Enregistré', tone: 'success' },
  { actor: 'Dr. L. Vasseur', role: 'Médecin', action: 'Tentative consultation', date: 'Hier, 18:03', result: 'Refusé · 403', tone: 'danger' },
  { actor: 'Marc Durand', role: 'Patient', action: 'Révocation accès', date: '12 mars 2025, 14:20', result: 'Enregistré', tone: 'warning' },
];

function App() {
  const [session, setSession] = useState(null);
  const [selectedRole, setSelectedRole] = useState('patient');
  const [activePage, setActivePage] = useState('dashboard');
  const [toast, setToast] = useState(null);

  function login(role) {
    setSession(roles[role]);
    setActivePage('dashboard');
  }

  function notify(message, tone = 'success') {
    setToast({ message, tone });
    window.setTimeout(() => setToast(null), 3200);
  }

  if (!session) {
    return <LoginScreen selectedRole={selectedRole} setSelectedRole={setSelectedRole} onLogin={login} />;
  }

  return (
    <div className="app-shell">
      <Sidebar session={session} activePage={activePage} setActivePage={setActivePage} onLogout={() => setSession(null)} />
      <main className="main-content">
        <Topbar session={session} onMenu={() => document.body.classList.toggle('nav-open')} />
        <div className="page-wrap">
          {activePage === 'dashboard' && <Dashboard session={session} notify={notify} setActivePage={setActivePage} />}
          {activePage === 'history' && <AuditPage />}
          {activePage === 'records' && <RecordsPage session={session} notify={notify} />}
          {activePage === 'settings' && <SettingsPage session={session} />}
        </div>
      </main>
      {toast && <Toast {...toast} />}
    </div>
  );
}

function LoginScreen({ selectedRole, setSelectedRole, onLogin }) {
  const [password, setPassword] = useState('DemoPass123!');
  const [error, setError] = useState(false);
  const current = roles[selectedRole];
  const Icon = current.icon;

  function submit(event) {
    event.preventDefault();
    if (!password) {
      setError(true);
      return;
    }
    onLogin(selectedRole);
  }

  return (
    <main className="login-page">
      <div className="login-ambient" />
      <section className="login-panel">
        <div className="brand-lockup"><span className="brand-mark"><LockKeyhole size={20} /></span><span>MedChain</span></div>
        <div className="eyebrow"><span className="status-dot" /> Portail sécurisé · Mode démonstration</div>
        <h1>Votre espace de confiance médicale.</h1>
        <p className="login-intro">Accédez aux données autorisées et gardez une trace de chaque opération sensible.</p>
        <div className="role-picker" aria-label="Choisir un rôle">
          {Object.entries(roles).map(([key, role]) => {
            const RoleIcon = role.icon;
            return <button key={key} className={`role-card ${selectedRole === key ? 'selected' : ''}`} onClick={() => { setSelectedRole(key); setError(false); }} type="button"><RoleIcon size={17} /><span>{role.label}</span><small>{role.subtitle}</small></button>;
          })}
        </div>
        <form onSubmit={submit} className="login-form">
          <label>Identifiant <span>Démo : {current.username}</span><input value={current.username} readOnly /></label>
          <label>Mot de passe<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
          {error && <div className="inline-error"><AlertTriangle size={16} /> Renseignez votre mot de passe pour continuer.</div>}
          <button className="primary-button full-width" type="submit">Ouvrir la session <ArrowRight size={17} /></button>
        </form>
        <div className="login-foot"><ShieldCheck size={16} /> Données fictives · Accès contrôlé par le backend Django</div>
      </section>
      <aside className="login-aside"><div className="aside-grid" /><div className="aside-content"><span className="aside-kicker">Clinical integrity</span><h2>Chaque accès laisse une preuve.</h2><p>Une interface pensée pour le consentement, la traçabilité et la confidentialité des données de santé.</p><div className="aside-proof"><CheckCircle2 size={18} /><span>Journal d’audit actif<br /><strong>SHA-256 · Synchronisé</strong></span></div></div></aside>
    </main>
  );
}

function Sidebar({ session, activePage, setActivePage, onLogout }) {
  const links = session.label === 'Patient' ? [['dashboard', 'Tableau de bord', LayoutDashboard], ['records', 'Mes données médicales', FileHeart], ['history', 'Historique des accès', FileClock], ['settings', 'Mes informations', UserRound]] : session.label === 'Médecin' ? [['dashboard', 'Tableau de bord', LayoutDashboard], ['records', 'Patients autorisés', UsersRound], ['history', 'Historique des accès', FileClock], ['settings', 'Mon profil', UserRound]] : [['dashboard', 'Vue générale', LayoutDashboard], ['history', 'Journaux de sécurité', FileClock], ['records', 'Utilisateurs', UsersRound], ['settings', 'Configuration', ClipboardList]];
  return <aside className="sidebar"><div className="sidebar-brand"><span className="brand-mark"><LockKeyhole size={18} /></span><div><strong>MedChain</strong><small>Secure health data</small></div><button className="mobile-close" onClick={() => document.body.classList.remove('nav-open')}><X size={18} /></button></div><div className="profile-mini"><span className="avatar">{session.user.split(' ').map((part) => part[0]).join('').slice(0, 2)}</span><div><strong>{session.user}</strong><small>{session.label} · Session active</small></div><span className="online-dot" /></div><nav className="side-nav">{links.map(([key, label, Icon]) => <button key={key} className={activePage === key ? 'active' : ''} onClick={() => { setActivePage(key); document.body.classList.remove('nav-open'); }}><Icon size={18} /><span>{label}</span>{activePage === key && <ChevronRight size={15} />}</button>)}</nav><div className="sidebar-bottom"><div className="integrity-chip"><ShieldCheck size={16} /><div><strong>Intégrité vérifiée</strong><small>Dernier contrôle · à l’instant</small></div></div><button className="logout-button" onClick={onLogout}><LogOut size={17} /> Se déconnecter</button></div></aside>;
}

function Topbar({ session, onMenu }) {
  return <header className="topbar"><button className="menu-button" onClick={onMenu}><Menu size={21} /></button><div className="breadcrumb"><span>MedChain</span><ChevronRight size={15} /><strong>{session.label}</strong></div><div className="topbar-actions"><div className="api-status"><span className="status-dot" /> API connectée</div><button className="icon-button" aria-label="Notifications"><AlertTriangle size={18} /><span className="notification-badge">2</span></button><span className="date-label">01 octobre 2026</span></div></header>;
}

function Dashboard({ session, notify, setActivePage }) {
  if (session.label === 'Patient') return <PatientDashboard notify={notify} setActivePage={setActivePage} />;
  if (session.label === 'Médecin') return <DoctorDashboard notify={notify} setActivePage={setActivePage} />;
  return <AdminDashboard setActivePage={setActivePage} />;
}

function PatientDashboard({ notify, setActivePage }) {
  const [doctors, setDoctors] = useState(patientData.doctors);
  const [modal, setModal] = useState(false);
  function revoke(index) { setDoctors((current) => current.map((doctor, item) => item === index ? { ...doctor, active: false } : doctor)); notify('Accès médecin révoqué et journalisé.', 'warning'); }
  return <><PageHeader kicker="Espace patient" title="Bonjour, Marc" subtitle="Voici l’état de vos données et de vos consentements." action={<button className="primary-button" onClick={() => setModal(true)}><Plus size={17} /> Autoriser un médecin</button>} /><div className="metrics-grid"><Metric icon={FileHeart} label="Données médicales" value="12" detail="Toutes protégées" /><Metric icon={CalendarDays} label="Rendez-vous à venir" value="3" detail="Prochain · 26 mars" /><Metric icon={UsersRound} label="Médecins autorisés" value={doctors.filter((doctor) => doctor.active).length} detail="Accès actifs" tone="teal" /></div><div className="content-grid"><section className="panel span-2"><PanelHeading title="Mes médecins autorisés" caption="Vous contrôlez les accès à vos données." action={<button className="text-button" onClick={() => setActivePage('history')}>Voir l’historique <ArrowRight size={15} /></button>} /><div className="doctor-list">{doctors.map((doctor, index) => <div className="doctor-row" key={doctor.name}><span className="avatar soft">{doctor.initials}</span><div className="row-main"><strong>{doctor.name}</strong><small>{doctor.specialty} · {doctor.scope}</small></div><StatusBadge label={doctor.active ? 'Actif' : 'Révoqué'} tone={doctor.active ? 'success' : 'danger'} />{doctor.active ? <button className="danger-button" onClick={() => revoke(index)}>Révoquer</button> : <button className="quiet-button" onClick={() => setModal(true)}>Autoriser</button>}</div>)}</div></section><section className="panel"><PanelHeading title="Mes informations" caption="Identité vérifiée" /><div className="info-list"><Info label="Nom complet" value="Marc Durand" /><Info label="Identifiant patient" value="#PT-84920" mono /><Info label="Téléphone" value="+33 6 12 34 56 78" /><Info label="Dernière mise à jour" value="Aujourd’hui, 08:12" /></div></section><section className="panel"><PanelHeading title="Prochains rendez-vous" caption="Agenda partagé" /><div className="appointment-list">{patientData.appointments.map((appointment) => <div className="appointment" key={appointment.date}><div className="date-tile"><strong>{appointment.date.split(' ')[0]}</strong><small>{appointment.date.split(' ')[1]}</small></div><div><strong>{appointment.type}</strong><small>{appointment.doctor} · {appointment.time}</small></div><span className="appointment-dot" /></div>)}</div></section></div>{modal && <ConsentModal doctors={doctors} onClose={() => setModal(false)} onConfirm={(name) => { setDoctors((current) => current.map((doctor) => doctor.name === name ? { ...doctor, active: true } : doctor)); setModal(false); notify(`Accès autorisé pour ${name}.`); }} />}</>;
}

function DoctorDashboard({ notify, setActivePage }) {
  const [selectedPatient, setSelectedPatient] = useState(doctorPatients[0]);
  const [forbidden, setForbidden] = useState(false);
  return <><PageHeader kicker="Espace médecin" title="Bonjour, Dr. Patel" subtitle="Consultez uniquement les dossiers dont le consentement est actif." action={<button className="secondary-button" onClick={() => setActivePage('history')}><FileClock size={17} /> Voir les accès</button>} /><div className="notice-bar"><ShieldCheck size={18} /><span><strong>Règle d’accès active</strong> · Chaque consultation est vérifiée par le serveur et inscrite dans le journal d’audit.</span><span className="mono">RBAC / CONSENT</span></div><div className="metrics-grid four"><Metric icon={UsersRound} label="Patients autorisés" value="42" detail="+3 cette semaine" /><Metric icon={CalendarDays} label="Rendez-vous aujourd’hui" value="6" detail="Prochain · 14:30" tone="teal" /><Metric icon={FileHeart} label="Dossiers consultés" value="18" detail="Ce mois-ci" /><Metric icon={ShieldCheck} label="Incidents d’accès" value="0" detail="Aucun signalement" /></div><div className="doctor-workspace"><section className="panel patient-table-panel"><PanelHeading title="Patients autorisés" caption="Liste filtrée par le contrôle d’accès serveur" /><div className="table-toolbar"><div className="search-box"><Search size={16} /><input placeholder="Rechercher un patient..." /></div><button className="quiet-button"><ClipboardList size={15} /> Exporter</button></div><div className="table-wrap"><table><thead><tr><th>Patient</th><th>Périmètre</th><th>Dernier accès</th><th>Statut</th><th /></tr></thead><tbody>{doctorPatients.map((patient) => <tr className={selectedPatient.id === patient.id ? 'selected-row' : ''} key={patient.id} onClick={() => { setSelectedPatient(patient); setForbidden(false); }}><td><div className="table-person"><span className="avatar soft">{patient.initials}</span><span><strong>{patient.name}</strong><small>{patient.id}</small></span></div></td><td>{patient.access}</td><td>{patient.lastAccess}</td><td><StatusBadge label={patient.state} tone="success" /></td><td><ChevronRight size={16} /></td></tr>)}</tbody></table></div></section><section className="panel record-panel">{forbidden ? <ForbiddenState onBack={() => setForbidden(false)} /> : <><div className="record-top"><div><span className="eyebrow">Dossier autorisé</span><h2>{selectedPatient.name}</h2><p>{selectedPatient.id} · Accès {selectedPatient.access}</p></div><StatusBadge label="Consentement actif" tone="success" /></div><div className="record-section"><h3>Données accessibles</h3><div className="record-item"><Activity size={17} /><div><strong>Dernière consultation</strong><small>Cardiologie · 26 mars 2025 à 14:30</small></div><CheckCircle2 size={17} className="icon-success" /></div><div className="record-item"><FileHeart size={17} /><div><strong>Observations médicales</strong><small>3 observations disponibles dans le périmètre autorisé</small></div><CheckCircle2 size={17} className="icon-success" /></div></div><button className="danger-outline" onClick={() => { setForbidden(true); notify('Accès refusé : le contrôle serveur a bloqué la consultation.', 'danger'); }}>Simuler un accès non autorisé (403)</button></>}</section></div></>;
}

function AdminDashboard({ setActivePage }) {
  return <><PageHeader kicker="Console d’administration" title="Supervision globale" subtitle="Un aperçu opérationnel des utilisateurs, rendez-vous et événements de sécurité." action={<button className="secondary-button" onClick={() => setActivePage('history')}><FileClock size={17} /> Journaux d’audit</button>} /><div className="metrics-grid four"><Metric icon={UserRound} label="Patients" value="1 248" detail="+42 ce mois" /><Metric icon={Stethoscope} label="Médecins" value="186" detail="Tous vérifiés" tone="teal" /><Metric icon={CalendarDays} label="Rendez-vous" value="3 492" detail="328 aujourd’hui" /><Metric icon={AlertTriangle} label="Alertes sécurité" value="3" detail="1 critique" tone="danger" /></div><div className="admin-grid"><section className="panel span-2"><PanelHeading title="Derniers événements de sécurité" caption="Surveillance des opérations sensibles" action={<button className="text-button" onClick={() => setActivePage('history')}>Voir tout <ArrowRight size={15} /></button>} /><div className="event-list">{auditEvents.slice(0, 3).map((event) => <AuditRow event={event} key={`${event.actor}-${event.date}`} />)}</div></section><section className="panel"><PanelHeading title="État des services" caption="Contrôles en temps réel" /><div className="service-list"><Service name="API MedChain" detail="Django REST" /><Service name="Base de données" detail="PostgreSQL 16" /><Service name="Authentification" detail="Token / RBAC" /><Service name="Journal d’audit" detail="Synchronisé" /></div></section></div></>;
}

function AuditPage() { return <><PageHeader kicker="Traçabilité" title="Historique des accès" subtitle="Chaque opération sensible est conservée avec son acteur, sa date et son résultat." action={<button className="secondary-button"><FileClock size={17} /> Exporter le journal</button>} /><section className="panel"><div className="table-toolbar"><div className="search-box"><Search size={16} /><input placeholder="Rechercher un utilisateur ou une action..." /></div><div className="filter-group"><button className="filter active">Tous</button><button className="filter">Autorisés</button><button className="filter">Refusés</button></div></div><div className="table-wrap"><table><thead><tr><th>Utilisateur</th><th>Rôle</th><th>Action</th><th>Date</th><th>Résultat</th></tr></thead><tbody>{auditEvents.map((event) => <tr key={`${event.actor}-${event.date}`}><td><strong>{event.actor}</strong></td><td>{event.role}</td><td>{event.action}</td><td className="mono">{event.date}</td><td><StatusBadge label={event.result} tone={event.tone} /></td></tr>)}</tbody></table></div></section></>; }

function RecordsPage({ session, notify }) { return <><PageHeader kicker={session.label === 'Médecin' ? 'Patients autorisés' : 'Données médicales'} title={session.label === 'Médecin' ? 'Dossiers accessibles' : 'Mes données médicales'} subtitle="Données de démonstration filtrées selon les permissions actives." /><section className="panel empty-friendly"><div className="record-hero"><span className="large-icon"><FileHeart size={28} /></span><div><h2>Protection active</h2><p>Les données sont visibles uniquement dans le périmètre de consentement accordé.</p></div></div><div className="record-cards"><div><span className="eyebrow">Dossier #PT-84920</span><strong>Consultation cardiologie</strong><small>26 mars 2025 · Donnée fictive</small></div><div><span className="eyebrow">Intégrité</span><strong className="success-text">Hash vérifié</strong><small>SHA-256 · il y a 2 min</small></div></div><button className="primary-button" onClick={() => notify('Données médicales chargées depuis le périmètre autorisé.')}>Charger les données <ArrowRight size={16} /></button></section></>; }

function SettingsPage({ session }) { return <><PageHeader kicker="Configuration du profil" title="Mes informations" subtitle="Les données affichées ici sont issues de l’utilisateur de démonstration connecté." /><section className="panel settings-panel"><div className="profile-large"><span className="avatar large">{session.user.split(' ').map((part) => part[0]).join('').slice(0, 2)}</span><div><h2>{session.user}</h2><p>{session.label} · Compte de démonstration</p></div><StatusBadge label="Session active" tone="success" /></div><div className="settings-grid"><Info label="Identifiant" value={session.username} mono /><Info label="Rôle applicatif" value={session.label} /><Info label="Dernière connexion" value="Aujourd’hui, 09:42" /><Info label="Méthode d’authentification" value="Token sécurisé" /></div></section></>; }

function ConsentModal({ doctors, onClose, onConfirm }) { const [selected, setSelected] = useState(doctors.find((doctor) => !doctor.active)?.name || doctors[0].name); return <div className="modal-backdrop" onClick={onClose}><div className="modal" onClick={(event) => event.stopPropagation()}><div className="modal-heading"><div><span className="eyebrow">Nouvelle permission</span><h2>Autoriser un médecin</h2></div><button className="icon-button" onClick={onClose}><X size={18} /></button></div><p className="modal-copy">Le médecin pourra consulter uniquement les données incluses dans votre périmètre de consentement.</p><label className="select-label">Médecin<select value={selected} onChange={(event) => setSelected(event.target.value)}>{doctors.map((doctor) => <option key={doctor.name}>{doctor.name}</option>)}</select></label><div className="consent-check"><ShieldCheck size={18} /><span>Cette action sera enregistrée dans votre historique d’accès.</span></div><div className="modal-actions"><button className="quiet-button" onClick={onClose}>Annuler</button><button className="primary-button" onClick={() => onConfirm(selected)}>Confirmer l’autorisation</button></div></div></div>; }

function ForbiddenState({ onBack }) { return <div className="forbidden-state"><span className="forbidden-icon"><XCircle size={28} /></span><span className="eyebrow danger-text">Erreur 403 · Accès refusé</span><h2>Consentement requis</h2><p>Vous n’êtes pas autorisé à consulter les données de ce patient. Le serveur a bloqué la requête et enregistré l’événement.</p><button className="secondary-button" onClick={onBack}>Retour aux patients autorisés</button></div>; }
function PageHeader({ kicker, title, subtitle, action }) { return <div className="page-header"><div><span className="eyebrow">{kicker}</span><h1>{title}</h1><p>{subtitle}</p></div>{action}</div>; }
function PanelHeading({ title, caption, action }) { return <div className="panel-heading"><div><h2>{title}</h2><p>{caption}</p></div>{action}</div>; }
function Metric({ icon: Icon, label, value, detail, tone = 'default' }) { return <div className={`metric-card ${tone}`}><div className="metric-top"><span>{label}</span><Icon size={18} /></div><strong>{value}</strong><small>{detail}</small></div>; }
function Info({ label, value, mono = false }) { return <div className="info-row"><span>{label}</span><strong className={mono ? 'mono' : ''}>{value}</strong></div>; }
function StatusBadge({ label, tone }) { return <span className={`status-badge ${tone}`}><span />{label}</span>; }
function AuditRow({ event }) { return <div className="audit-row"><span className={`event-icon ${event.tone}`}><Activity size={16} /></span><div><strong>{event.action}</strong><small>{event.actor} · {event.date}</small></div><StatusBadge label={event.result} tone={event.tone} /></div>; }
function Service({ name, detail }) { return <div className="service-row"><span className="service-dot" /><div><strong>{name}</strong><small>{detail}</small></div><span className="success-text">Opérationnel</span></div>; }
function Toast({ message, tone }) { return <div className={`toast ${tone}`}><CheckCircle2 size={18} />{message}</div>; }

export default App;