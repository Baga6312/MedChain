import {
  ArrowRight,
  Activity,
  ArrowUpRight,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  FileCheck2,
  Fingerprint,
  LockKeyhole,
  LogIn,
  Network,
  ShieldCheck,
  Stethoscope,
  UserCheck,
  UserPlus,
  UserRound,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import ThemeToggle from '../components/common/ThemeToggle';
import { useAuth } from '../context/AuthContext';

const pipeline = [
  {
    number: '01',
    title: 'Consentement patient',
    description: 'Le patient garde le contrôle de ses autorisations médicales.',
    icon: UserRound,
    code: 'did:medchain:patient_8f93',
  },
  {
    number: '02',
    title: 'Acte médical signé',
    description: 'Le praticien ajoute une observation ou un résultat vérifiable.',
    icon: Stethoscope,
    code: 'signature:rpps_10103492819',
  },
  {
    number: '03',
    title: 'Parcours de soins',
    description: 'Chaque étape est organisée dans une timeline claire.',
    icon: Network,
    code: 'timeline:consultation → suivi',
  },
  {
    number: '04',
    title: 'Preuve cryptographique',
    description: 'Le contenu reste chiffré, tandis que son intégrité est prouvée.',
    icon: ShieldCheck,
    code: 'merkle_root:0x9b44c8d2…',
  },
];

export default function HomePage() {
  const { isAuthed, user } = useAuth();

  function scrollToSection(event, sectionId) {
    event.preventDefault();
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  return (
    <div className="public-home">
      <header className="public-header">
        <Link className="public-brand" to="/">
          <span className="brand-mark"><LockKeyhole size={18} /></span>
          <span><strong>MedChain</strong><small>Health Ledger</small></span>
        </Link>
        <nav className="public-nav" aria-label="Navigation principale">
          <a href="#pipeline" onClick={(event) => scrollToSection(event, 'pipeline')}>Comment ça marche</a>
          <a href="#trust" onClick={(event) => scrollToSection(event, 'trust')}>Sécurité</a>
          <a href="#trust" onClick={(event) => scrollToSection(event, 'trust')}>Pour les professionnels</a>
        </nav>
        <div className="public-actions">
          <ThemeToggle />
          {isAuthed ? (
            <Link className="public-account-action" to="/settings" aria-label="Ouvrir mon profil" title="Mon profil">
              {user?.avatar_url ? <img src={user.avatar_url} alt="" /> : (user?.first_name || user?.email || 'M').slice(0, 1).toUpperCase()}
            </Link>
          ) : (
            <>
              <Link className="public-icon-action" to="/login" aria-label="Se connecter" title="Se connecter"><LogIn size={17} /></Link>
              <Link className="public-icon-action primary" to="/register" aria-label="Commencer" title="Commencer"><UserPlus size={17} /></Link>
            </>
          )}
        </div>
      </header>

      <main>
        <section className="public-hero">
          <div className="hero-glow" />
          <div className="public-hero-copy">
            <div className="trust-badge"><CircleDot size={13} /> Infrastructure de santé cryptographique</div>
            <h1>Des dossiers médicaux <em>infalsifiables.</em> Une confiance absolue.</h1>
            <p>
              MedChain connecte patients, médecins et établissements de santé autour d&apos;un
              parcours de soins sécurisé, traçable et respectueux du secret médical.
            </p>
            <div className="hero-actions">
              <Link className="primary-button large" to="/register">Créer mon espace <ArrowRight size={17} /></Link>
              <a className="secondary-button large" href="#pipeline">Explorer la plateforme</a>
            </div>
            <div className="hero-metrics">
              <div><strong>100%</strong><span>Intégrité vérifiable</span></div>
              <div><strong>AES-256</strong><span>Données chiffrées</span></div>
              <div><strong>HDS</strong><span>Conçu pour la santé</span></div>
            </div>
          </div>
          <div className="hero-visual" aria-label="Visualisation de la confiance MedChain">
            <div className="visual-orbit orbit-one" />
            <div className="visual-orbit orbit-two" />
            <div className="hero-core">
              <ShieldCheck size={42} />
              <strong>Intégrité<br />vérifiée</strong>
              <span>Bloc #4,892,104</span>
            </div>
            <div className="floating-proof proof-top"><Fingerprint size={17} /><span><b>Hash validé</b><small>0x9b44c8d2…a719</small></span></div>
            <div className="floating-proof proof-bottom"><FileCheck2 size={17} /><span><b>Dossier chiffré</b><small>Accès autorisé</small></span></div>
          </div>
        </section>

        <section className="public-section" id="pipeline">
          <div className="section-heading">
            <div><span className="eyebrow">Le parcours de confiance</span><h2>De l&apos;acte médical à la preuve</h2></div>
            <p>Une représentation simple d&apos;une architecture technique conçue pour rester lisible par les équipes de soins.</p>
          </div>
          <div className="pipeline-grid">
            {pipeline.map(({ number, title, description, icon: Icon, code }, index) => (
              <div className={`pipeline-card ${index === pipeline.length - 1 ? 'pipeline-card-dark' : ''}`} key={title}>
                <div className="pipeline-top"><span className="pipeline-number">{number}</span><Icon size={20} /></div>
                <h3>{title}</h3>
                <p>{description}</p>
                <code>{code}</code>
                {index < pipeline.length - 1 && <ChevronRight className="pipeline-arrow" size={20} />}
              </div>
            ))}
          </div>
        </section>

        <section className="public-section platform-section">
          <div className="section-heading">
            <div><span className="eyebrow">Une expérience pensée pour le soin</span><h2>Tout le parcours, au même endroit.</h2></div>
            <p>Un espace lisible pour agir rapidement, suivre les étapes et vérifier chaque information importante.</p>
          </div>
          <div className="platform-grid">
            <div className="role-cards">
              <article>
                <span className="platform-icon"><UserCheck size={19} /></span>
                <h3>Patients</h3>
                <p>Demandez une prise en charge, retrouvez vos traitements et gardez une vision claire de votre parcours.</p>
                <Link to={isAuthed ? '/dashboard' : '/register'}>Accéder à mon espace <ArrowUpRight size={15} /></Link>
              </article>
              <article>
                <span className="platform-icon"><Stethoscope size={19} /></span>
                <h3>Professionnels</h3>
                <p>Coordonnez les soins avec une timeline partagée et des événements médicaux signés.</p>
                <a href="#trust" onClick={(event) => scrollToSection(event, 'trust')}>Découvrir la vue métier <ArrowUpRight size={15} /></a>
              </article>
            </div>
            <div className="ledger-preview">
              <div className="ledger-preview-heading"><span><Activity size={17} /> Journal de confiance</span><b>EN DIRECT</b></div>
              <div className="ledger-line"><span className="ledger-dot" /><div><strong>Résultat clinique ajouté</strong><small>Consultation · il y a 2 min</small></div><CheckCircle2 size={16} /></div>
              <div className="ledger-line"><span className="ledger-dot" /><div><strong>Consentement vérifié</strong><small>Dossier patient · il y a 8 min</small></div><CheckCircle2 size={16} /></div>
              <div className="ledger-line"><span className="ledger-dot" /><div><strong>Prochain rendez-vous</strong><small><CalendarDays size={12} /> Suivi médical · demain</small></div><ChevronRight size={16} /></div>
              <div className="ledger-hash"><span>HASH DE SESSION</span><code>0x7f3a…91c2</code></div>
            </div>
          </div>
        </section>

        <section className="public-section trust-section" id="trust">
          <div className="trust-panel">
            <div>
              <span className="eyebrow">Traçabilité sans angle mort</span>
              <h2>La même source de vérité pour chaque acteur.</h2>
              <p>Les événements restent privés et chiffrés. Seule leur empreinte d&apos;intégrité est partagée pour garantir qu&apos;aucune information n&apos;a été altérée.</p>
            </div>
            <div className="trust-checks">
              <span><CheckCircle2 size={17} /> Consentements explicites</span>
              <span><CheckCircle2 size={17} /> Historique horodaté</span>
              <span><CheckCircle2 size={17} /> Ancrage blockchain vérifiable</span>
            </div>
          </div>
        </section>

      </main>
      <footer className="public-footer"><strong>MedChain</strong><span>Health Ledger · Sécurité clinique par conception</span></footer>
    </div>
  );
}
