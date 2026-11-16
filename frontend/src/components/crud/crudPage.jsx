import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, Plus, X } from 'lucide-react';
import { api } from '../../services/resourceService';
import { resources } from '../../config/resources';

const toInput = (f, v) => (v == null ? '' : f.type === 'datetime-local' ? String(v).slice(0, 16) : v);
const fromInput = (f, v) => (f.ref ? Number(v) : v === '' && f.nullable ? null : v);

export default function CrudPage({ resource, notify }) {
  const cfg = resources[resource];
  const [rows, setRows] = useState([]);
  const [lookups, setLookups] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null); // null | {} (new) | row

  const load = useCallback(async () => {
    const refs = [...new Set(cfg.fields.filter((f) => f.ref).map((f) => f.ref))];
    setLoading(true);
    setError(null);
    try {
      const [data, ...rest] = await Promise.all([api.list(resource), ...refs.map((r) => api.list(r))]);
      setRows(data);
      setLookups(Object.fromEntries(refs.map((r, i) => [r, rest[i]])));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [resource, cfg]);

  useEffect(() => {
    setEditing(null);
    load();
  }, [load]);

  const display = (f, v) => {
    if (v == null || v === '') return '—';
    if (f.ref) return lookups[f.ref]?.find((o) => o.id === v)?.name ?? `#${v}`;
    return String(v);
  };

  async function remove(row) {
    if (!window.confirm(`Supprimer ce ${cfg.singular} (#${row.id}) ?`)) return;
    try {
      await api.remove(resource, row.id);
      notify('Supprimé.');
      load();
    } catch (e) {
      notify(e.message, 'danger');
    }
  }

  return (
    <>
      <div className="page-header">
        <div>
          <span className="eyebrow">Gestion</span>
          <h1>{cfg.label}</h1>
          <p>{rows.length} enregistrement(s)</p>
        </div>
        <button className="primary-button" onClick={() => setEditing({})}>
          <Plus size={17} /> Ajouter
        </button>
      </div>

      {error && (
        <div className="inline-error">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      <section className="panel">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                {cfg.fields.map((f) => (
                  <th key={f.name}>{f.label}</th>
                ))}
                <th />
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td className="empty-row" colSpan={cfg.fields.length + 2}>Chargement…</td>
                </tr>
              )}
              {!loading && rows.length === 0 && (
                <tr>
                  <td className="empty-row" colSpan={cfg.fields.length + 2}>Aucun enregistrement.</td>
                </tr>
              )}
              {!loading &&
                rows.map((row) => (
                  <tr key={row.id}>
                    <td className="mono">{row.id}</td>
                    {cfg.fields.map((f) => (
                      <td key={f.name} className={f.type === 'textarea' ? 'truncate' : ''}>
                        {display(f, row[f.name])}
                      </td>
                    ))}
                    <td>
                      <div className="row-actions">
                        <button className="quiet-button" onClick={() => setEditing(row)}>Modifier</button>
                        <button className="danger-button" onClick={() => remove(row)}>Supprimer</button>
                      </div>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>

      {editing && (
        <Form
          cfg={cfg}
          resource={resource}
          row={editing.id ? editing : null}
          lookups={lookups}
          onClose={() => setEditing(null)}
          onSaved={(msg) => {
            setEditing(null);
            notify(msg);
            load();
          }}
        />
      )}
    </>
  );
}

function Form({ cfg, resource, row, lookups, onClose, onSaved }) {
  const [values, setValues] = useState(() =>
    Object.fromEntries(cfg.fields.map((f) => [f.name, toInput(f, row?.[f.name])]))
  );
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const payload = Object.fromEntries(cfg.fields.map((f) => [f.name, fromInput(f, values[f.name])]));
    try {
      if (row) await api.update(resource, row.id, payload);
      else await api.create(resource, payload);
      onSaved(row ? 'Modifié.' : 'Créé.');
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  }

  const set = (name) => (event) => setValues((v) => ({ ...v, [name]: event.target.value }));

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <div className="modal-heading">
          <h2>{row ? `Modifier ${cfg.singular} #${row.id}` : `Nouveau ${cfg.singular}`}</h2>
          <button type="button" className="icon-button" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {cfg.fields.map((f) => (
          <label className="field" key={f.name}>
            {f.ref ? (
              <select aria-label={f.label} required value={values[f.name]} onChange={set(f.name)}>
                <option value="" disabled>Choisir…</option>
                {(lookups[f.ref] ?? []).map((o) => (
                  <option key={o.id} value={o.id}>{o.name} (#{o.id})</option>
                ))}
              </select>
            ) : f.type === 'textarea' ? (
              <textarea aria-label={f.label} placeholder={f.label} required value={values[f.name]} onChange={set(f.name)} />
            ) : (
              <input aria-label={f.label} placeholder={f.label} type={f.type} required={!f.nullable} value={values[f.name]} onChange={set(f.name)} />
            )}
          </label>
        ))}

        {error && (
          <div className="inline-error">
            <AlertTriangle size={16} /> {error}
          </div>
        )}

        <div className="modal-actions">
          <button type="button" className="quiet-button" onClick={onClose}>Annuler</button>
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? 'Envoi…' : 'Enregistrer'}
          </button>
        </div>
      </form>
    </div>
  );
}