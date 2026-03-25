/**
 * ProductForm.tsx — Form creazione/modifica prodotto
 */
import { useState } from 'react';
import type { Product, ProductCategory } from './catalogService';

interface ProductFormProps {
  product?: Product | null;
  categories: ProductCategory[];
  onSubmit: (data: Omit<Product, 'id' | 'company_id' | 'is_active' | 'created_at' | 'updated_at'>) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const UNITS = [
  { value: 'mq', label: 'm²' },
  { value: 'ml', label: 'ml' },
  { value: 'pz', label: 'pz' },
];

const TIERS = [
  { value: 'base', label: '🟢 Base', color: '#22c55e' },
  { value: 'medio', label: '🟡 Medio', color: '#eab308' },
  { value: 'top', label: '🔴 Top', color: '#ef4444' },
];

const WINDOW_TYPES = ['battente', 'scorrevole', 'vasistas', 'portafinestra', 'fisso', 'altro'];

export default function ProductForm({ product, categories, onSubmit, onCancel, isLoading }: ProductFormProps) {
  const [name, setName] = useState(product?.name || '');
  const [sku, setSku] = useState(product?.sku || '');
  const [supplier, setSupplier] = useState(product?.supplier || '');
  const [description, setDescription] = useState(product?.description || '');
  const [categoryId, setCategoryId] = useState(product?.category_id || '');
  const [unit, setUnit] = useState(product?.unit || 'mq');
  const [tier, setTier] = useState(product?.tier || 'base');
  const [price, setPrice] = useState(product?.price?.toString() || '');
  const [appliesTo, setAppliesTo] = useState<string[]>(product?.applies_to || WINDOW_TYPES);

  const toggleWindowType = (type: string) => {
    setAppliesTo(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      name,
      sku: sku || undefined,
      supplier: supplier || undefined,
      description: description || undefined,
      category_id: categoryId || null,
      unit: unit as Product['unit'],
      tier: tier as Product['tier'],
      price: parseFloat(price) || 0,
      applies_to: appliesTo,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <div className="form-grid">
        <div className="form-group">
          <label>Nome prodotto *</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} required
                 placeholder="es. Rehau Brillant Design 70" />
        </div>

        <div className="form-group">
          <label>SKU</label>
          <input type="text" value={sku} onChange={e => setSku(e.target.value)}
                 placeholder="Codice interno" />
        </div>

        <div className="form-group">
          <label>Fornitore</label>
          <input type="text" value={supplier} onChange={e => setSupplier(e.target.value)}
                 placeholder="es. Rehau, Schüco" />
        </div>

        <div className="form-group">
          <label>Categoria</label>
          <select value={categoryId} onChange={e => setCategoryId(e.target.value)}>
            <option value="">— Nessuna —</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Fascia prezzo *</label>
          <div className="tier-selector">
            {TIERS.map(t => (
              <button key={t.value} type="button"
                className={`tier-btn ${tier === t.value ? 'active' : ''}`}
                style={{ '--tier-color': t.color } as React.CSSProperties}
                onClick={() => setTier(t.value as 'base' | 'medio' | 'top')}>
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Prezzo *</label>
            <input type="number" step="0.01" min="0" value={price}
                   onChange={e => setPrice(e.target.value)} required placeholder="0.00" />
          </div>
          <div className="form-group">
            <label>Unità *</label>
            <select value={unit} onChange={e => setUnit(e.target.value as 'mq' | 'ml' | 'pz')}>
              {UNITS.map(u => (
                <option key={u.value} value={u.value}>{u.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group full-width">
          <label>Descrizione</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)}
                    rows={2} placeholder="Descrizione opzionale" />
        </div>

        <div className="form-group full-width">
          <label>Si applica a</label>
          <div className="window-types-grid">
            {WINDOW_TYPES.map(type => (
              <label key={type} className="checkbox-label">
                <input type="checkbox" checked={appliesTo.includes(type)}
                       onChange={() => toggleWindowType(type)} />
                <span>{type}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button type="button" onClick={onCancel} className="btn-secondary">
          Annulla
        </button>
        <button type="submit" disabled={isLoading || !name || !price} className="btn-primary">
          {isLoading ? 'Salvataggio...' : product ? 'Salva modifiche' : 'Aggiungi prodotto'}
        </button>
      </div>
    </form>
  );
}
