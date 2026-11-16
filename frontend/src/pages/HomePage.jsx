import {
  ArrowRight,
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
  UserPlus,
  UserRound,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import ThemeToggle from '../components/common/ThemeToggle';

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
          <Link className="public-icon-action" to="/login" aria-label="Se connecter" title="Se connecter"><LogIn size={17} /></Link>
          <Link className="public-icon-action primary" to="/register" aria-label="Commencer" title="Commencer"><UserPlus size={17} /></Link>
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
