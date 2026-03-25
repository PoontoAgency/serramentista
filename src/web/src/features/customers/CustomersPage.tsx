/**
 * CustomersPage.tsx — Lista clienti con ricerca e dettaglio
 */
import { useState } from 'react';
import { useCustomers, useCustomerDetail, useCreateCustomer } from './useCustomers';
import './customers.css';

const STATUS_COLORS: Record<string, string> = {
  draft: '#6b7280', ready: '#2563eb', sent: '#7c3aed',
  accepted: '#16a34a', rejected: '#dc2626',
};

function formatCurrency(amount: number): string {
  return `€ ${amount.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`;
}

export default function CustomersPage() {
  const [search, setSearch] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', address: '', city: '', phone: '', email: '' });

  const { data: customers = [], isLoading } = useCustomers(search || undefined);
  const { data: detail } = useCustomerDetail(selectedId);
  const createCustomer = useCreateCustomer();

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createCustomer.mutate(form, {
      onSuccess: () => {
        setShowForm(false);
        setForm({ name: '', address: '', city: '', phone: '', email: '' });
      },
    });
  };

  return (
    <div className="customers-page">
      <div className="customers-header">
        <div>
          <h2>👥 Clienti</h2>
          <p className="subtitle">Anagrafica e storico preventivi</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          + Nuovo cliente
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="customer-form">
          <div className="form-row">
            <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                   placeholder="Nome *" required />
            <input type="text" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})}
                   placeholder="Telefono" />
            <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                   placeholder="Email" />
          </div>
          <div className="form-row">
            <input type="text" value={form.address} onChange={e => setForm({...form, address: e.target.value})}
                   placeholder="Indirizzo" />
            <input type="text" value={form.city} onChange={e => setForm({...form, city: e.target.value})}
                   placeholder="Città" />
            <button type="submit" className="btn-primary btn-sm" disabled={!form.name}>Aggiungi</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary btn-sm">Annulla</button>
          </div>
        </form>
      )}

      <input
        type="text" value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="🔍 Cerca cliente..."
        className="search-input"
      />

      <div className="customers-layout">
        <div className="customers-list">
          {isLoading ? (
            <div className="loading">Caricamento clienti...</div>
          ) : customers.length === 0 ? (
            <div className="empty-state">Nessun cliente trovato.</div>
          ) : (
            customers.map(c => (
              <div key={c.id}
                   className={`customer-item ${selectedId === c.id ? 'active' : ''}`}
                   onClick={() => setSelectedId(c.id)}>
                <div className="customer-name">{c.name}</div>
                <div className="customer-meta">
                  {c.city || ''} {c.phone ? `· ${c.phone}` : ''}
                </div>
              </div>
            ))
          )}
        </div>

        {selectedId && detail && (
          <div className="customer-detail">
            <h3>{detail.customer?.name}</h3>
            {detail.customer?.address && (
              <p className="detail-item">📍 {detail.customer.address}{detail.customer.city ? `, ${detail.customer.city}` : ''}</p>
            )}
            {detail.customer?.phone && <p className="detail-item">📞 {detail.customer.phone}</p>}
            {detail.customer?.email && <p className="detail-item">📧 {detail.customer.email}</p>}

            <h4>Storico preventivi ({detail.quotes.length})</h4>
            {detail.quotes.length === 0 ? (
              <p className="empty-text">Nessun preventivo</p>
            ) : (
              <div className="customer-quotes">
                {detail.quotes.map((q: any) => (
                  <div key={q.id} className="mini-quote">
                    <span className="mini-number">{q.number}</span>
                    <span className="mini-status" style={{ color: STATUS_COLORS[q.status] || '#6b7280' }}>
                      {q.status}
                    </span>
                    <span className="mini-value">{formatCurrency(q.total_medio || 0)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
