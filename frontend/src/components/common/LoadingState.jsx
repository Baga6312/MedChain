import { LoaderCircle } from 'lucide-react';

export default function LoadingState({ label = 'Chargement…' }) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <LoaderCircle className="loading-icon" size={38} />
      <span>{label}</span>
    </div>
  );
}
