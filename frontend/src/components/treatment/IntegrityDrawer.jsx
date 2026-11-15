import { AlertTriangle, X } from 'lucide-react';

function shorten(value) {
  if (!value) return '—';
  return `${value.slice(0, 12)}…${value.slice(-8)}`;
}

export default function IntegrityDrawer({ data, onClose }) {
  return (
    <div className="integrity-overlay" role="presentation" onClick={onClose}>
      <aside className="integrity-drawer" role="dialog" aria-modal="true" aria-labelledby="integrity-title" onClick={(event) => event.stopPropagation()}>
        <div className="panel-heading">
          <div><h2 id="integrity-title">Détails d’intégrité</h2><p>Les données médicales restent chiffrées.</p></div>
          <button className="icon-button" type="button" aria-label="Fermer" onClick={onClose}><X size={18} /></button>
        </div>
        {data.chains.map((chainData) => (
          <section className="integrity-chain" key={chainData.name}>
            <div className="integrity-chain-heading">
              <strong>{chainData.label}</strong>
              <span>{chainData.block_count} blocs</span>
            </div>
            {chainData.latest_block ? (
              <dl className="integrity-details">
                <dt>Bloc actuel</dt><dd>#{chainData.latest_block.index}</dd>
                <dt>Hash du bloc</dt><dd className="mono">{shorten(chainData.latest_block.hash)}</dd>
                <dt>Bloc précédent</dt><dd className="mono">{shorten(chainData.latest_block.prev_hash)}</dd>
                <dt>Racine Merkle</dt><dd className="mono">{shorten(chainData.latest_block.merkle_root)}</dd>
                <dt>Nonce</dt><dd>{chainData.latest_block.nonce}</dd>
                <dt>Ancrage</dt><dd>{chainData.anchor ? `Bloc #${chainData.anchor.block_index}` : 'En attente'}</dd>
                {chainData.anchor && <><dt>Transaction</dt><dd className="mono">{shorten(chainData.anchor.tx_hash)}</dd></>}
              </dl>
            ) : <p className="timeline-empty">Aucun bloc créé pour cette chaîne.</p>}
            {chainData.errors.length > 0 && <p className="integrity-error"><AlertTriangle size={14} /> {chainData.errors[0]}</p>}
          </section>
        ))}
      </aside>
    </div>
  );
}
