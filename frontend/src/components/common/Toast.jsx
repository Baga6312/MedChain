import { CheckCircle2, XCircle } from 'lucide-react';

export default function Toast({ toast }) {
  if (!toast) return null;
  return (
    <div className={`toast ${toast.tone}`}>
      {toast.tone === 'danger' ? <XCircle size={18} /> : <CheckCircle2 size={18} />}
      {toast.message}
    </div>
  );
}