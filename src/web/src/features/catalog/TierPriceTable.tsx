/**
 * TierPriceTable.tsx — Vista tabellare comparativa base/medio/top
 */
import type { Product } from './catalogService';

interface TierPriceTableProps {
  products: Product[];
  onEdit: (product: Product) => void;
  onDelete: (id: string) => void;
}

const TIER_CONFIG = {
  base: { label: 'Base', icon: '🟢', color: '#22c55e' },
  medio: { label: 'Medio', icon: '🟡', color: '#eab308' },
  top: { label: 'Top', icon: '🔴', color: '#ef4444' },
};

const UNIT_LABEL: Record<string, string> = {
  mq: 'm²',
  ml: 'ml',
  pz: 'pz',
};

export default function TierPriceTable({ products, onEdit, onDelete }: TierPriceTableProps) {
  if (products.length === 0) {
    return (
      <div className="tier-empty">
        <p>Nessun prodotto nel catalogo. Aggiungi il primo prodotto per iniziare.</p>
      </div>
    );
  }

  return (
    <div className="tier-price-table">
      <table>
        <thead>
          <tr>
            <th>Prodotto</th>
            <th>Fornitore</th>
            <th>
              <span className="tier-header" style={{ color: TIER_CONFIG.base.color }}>
                {TIER_CONFIG.base.icon} Base
              </span>
            </th>
            <th>
              <span className="tier-header" style={{ color: TIER_CONFIG.medio.color }}>
                {TIER_CONFIG.medio.icon} Medio
              </span>
            </th>
            <th>
              <span className="tier-header" style={{ color: TIER_CONFIG.top.color }}>
                {TIER_CONFIG.top.icon} Top
              </span>
            </th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr key={p.id}>
              <td>
                <div className="product-name">{p.name}</div>
                {p.sku && <div className="product-sku">{p.sku}</div>}
              </td>
              <td className="supplier-cell">{p.supplier || '—'}</td>
              <td className={p.tier === 'base' ? 'price-cell active' : 'price-cell'}>
                {p.tier === 'base' ? `€ ${p.price.toFixed(2)}/${UNIT_LABEL[p.unit]}` : '—'}
              </td>
              <td className={p.tier === 'medio' ? 'price-cell active' : 'price-cell'}>
                {p.tier === 'medio' ? `€ ${p.price.toFixed(2)}/${UNIT_LABEL[p.unit]}` : '—'}
              </td>
              <td className={p.tier === 'top' ? 'price-cell active' : 'price-cell'}>
                {p.tier === 'top' ? `€ ${p.price.toFixed(2)}/${UNIT_LABEL[p.unit]}` : '—'}
              </td>
              <td className="actions-cell">
                <button onClick={() => onEdit(p)} className="btn-icon" title="Modifica">✏️</button>
                <button onClick={() => onDelete(p.id)} className="btn-icon btn-danger" title="Disattiva">🗑️</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
