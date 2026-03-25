/**
 * ExtraPresetsManager.tsx — Gestione voci extra preimpostate
 */
import { useState } from 'react';
import { useExtraPresets, useCreateExtraPreset, useUpdateExtraPreset, useDeleteExtraPreset } from './useCatalog';
import type { ExtraPreset } from './catalogService';

const UNITS = [
  { value: 'pz', label: 'pz' },
  { value: 'mq', label: 'm²' },
  { value: 'ml', label: 'ml' },
  { value: 'ora', label: 'ora' },
  { value: 'forfait', label: 'forfait' },
];

export default function ExtraPresetsManager() {
  const { data: presets = [], isLoading } = useExtraPresets();
  const createMutation = useCreateExtraPreset();
  const updateMutation = useUpdateExtraPreset();
  const deleteMutation = useDeleteExtraPreset();

  const [showForm, setShowForm] = useState(false);
  const [editingPreset, setEditingPreset] = useState<ExtraPreset | null>(null);
  const [form, setForm] = useState({ name: '', default_price: '', unit: 'pz', description: '' });

  const resetForm = () => {
    setForm({ name: '', default_price: '', unit: 'pz', description: '' });
    setShowForm(false);
    setEditingPreset(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      name: form.name,
      default_price: parseFloat(form.default_price) || 0,
      unit: form.unit as ExtraPreset['unit'],
      description: form.description || undefined,
    };

    if (editingPreset) {
      updateMutation.mutate({ id: editingPreset.id, ...data }, { onSuccess: resetForm });
    } else {
      createMutation.mutate(data, { onSuccess: resetForm });
    }
  };

  const startEdit = (preset: ExtraPreset) => {
    setEditingPreset(preset);
    setForm({
      name: preset.name,
      default_price: preset.default_price.toString(),
      unit: preset.unit,
      description: preset.description || '',
    });
    setShowForm(true);
  };

  if (isLoading) return <div className="loading">Caricamento voci extra...</div>;

  return (
    <div className="extras-manager">
      <div className="extras-header">
        <h3>🔧 Voci extra</h3>
        {!showForm && (
          <button onClick={() => setShowForm(true)} className="btn-primary btn-sm">
            + Nuova voce
          </button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="extra-form">
          <div className="form-row">
            <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                   placeholder="Nome voce (es. Posa in opera)" required />
            <input type="number" step="0.01" min="0" value={form.default_price}
                   onChange={e => setForm({ ...form, default_price: e.target.value })}
                   placeholder="Prezzo default" />
            <select value={form.unit} onChange={e => setForm({ ...form, unit: e.target.value })}>
              {UNITS.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
            </select>
          </div>
          <div className="form-row">
            <input type="text" value={form.description}
                   onChange={e => setForm({ ...form, description: e.target.value })}
                   placeholder="Descrizione (opzionale)" />
            <button type="submit" className="btn-primary btn-sm" disabled={!form.name}>
              {editingPreset ? 'Salva' : 'Aggiungi'}
            </button>
            <button type="button" onClick={resetForm} className="btn-secondary btn-sm">Annulla</button>
          </div>
        </form>
      )}

      <div className="extras-list">
        {presets.length === 0 ? (
          <p className="empty-text">Nessuna voce extra configurata.</p>
        ) : (
          presets.map(preset => (
            <div key={preset.id} className="extra-item">
              <div className="extra-info">
                <span className="extra-name">{preset.name}</span>
                <span className="extra-price">
                  € {preset.default_price.toFixed(2)} / {preset.unit}
                </span>
                {preset.description && (
                  <span className="extra-desc">{preset.description}</span>
                )}
              </div>
              <div className="extra-actions">
                <button onClick={() => startEdit(preset)} className="btn-icon" title="Modifica">✏️</button>
                <button onClick={() => deleteMutation.mutate(preset.id)} className="btn-icon btn-danger" title="Disattiva">🗑️</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
