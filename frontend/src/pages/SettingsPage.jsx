import { Settings } from 'lucide-react';
import ProfileSettings from '../components/profile/ProfileSettings';

export default function SettingsPage() {
  return (
    <>
      <div className="page-header">
        <div><span className="eyebrow">Préférences</span><h1>Paramètres du compte</h1><p>Gérez votre identité et vos informations personnelles.</p></div>
        <Settings className="page-header-icon" size={28} />
      </div>
      <ProfileSettings />
    </>
  );
}
