/**
 * CategoryManager.tsx — Gestione categorie con CRUD
 */
import { useState } from 'react';
import { useCategories, useCreateCategory, useUpdateCategory, useDeleteCategory } from './useCatalog';

export default function CategoryManager() {
  const { data: categories = [], isLoading } = useCategories();
  const createMutation = useCreateCategory();
  const updateMutation = useUpdateCategory();
  const deleteMutation = useDeleteCategory();
  const [newName, setNewName] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');

  const handleCreate = () => {
    if (!newName.trim()) return;
    createMutation.mutate({ name: newName.trim() }, {
      onSuccess: () => setNewName(''),
    });
  };

  const startEdit = (id: string, name: string) => {
    setEditingId(id);
    setEditName(name);
  };

  const saveEdit = () => {
    if (!editingId || !editName.trim()) return;
    updateMutation.mutate({ id: editingId, name: editName.trim() }, {
      onSuccess: () => setEditingId(null),
    });
  };

  if (isLoading) return <div className="loading">Caricamento categorie...</div>;

  return (
    <div className="category-manager">
      <h3>📂 Categorie</h3>
      <div className="category-list">
        {categories.map(cat => (
          <div key={cat.id} className="category-item">
            {editingId === cat.id ? (
              <div className="category-edit">
                <input type="text" value={editName} onChange={e => setEditName(e.target.value)}
                       onKeyDown={e => e.key === 'Enter' && saveEdit()} autoFocus />
                <button onClick={saveEdit} className="btn-icon" title="Salva">✅</button>
                <button onClick={() => setEditingId(null)} className="btn-icon" title="Annulla">❌</button>
              </div>
            ) : (
              <div className="category-view">
                <span className="category-name">{cat.name}</span>
                <div className="category-actions">
                  <button onClick={() => startEdit(cat.id, cat.name)} className="btn-icon" title="Modifica">✏️</button>
                  <button onClick={() => deleteMutation.mutate(cat.id)} className="btn-icon btn-danger" title="Disattiva">🗑️</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="category-add">
        <input type="text" value={newName} onChange={e => setNewName(e.target.value)}
               placeholder="Nuova categoria..." onKeyDown={e => e.key === 'Enter' && handleCreate()} />
        <button onClick={handleCreate} disabled={!newName.trim() || createMutation.isPending}
                className="btn-primary btn-sm">
          + Aggiungi
        </button>
      </div>
    </div>
  );
}
