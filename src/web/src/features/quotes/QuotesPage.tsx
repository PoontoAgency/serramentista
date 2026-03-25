/**
 * QuotesPage.tsx — Lista preventivi con filtri
 */
import { useState } from 'react';
import { useQuotes, useUpdateQuoteStatus } from './useQuotes';
import './quotes.css';

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  draft: { label: 'Bozza', color: '#6b7280' },
  ready: { label: 'Pronto', color: '#2563eb' },
  sent: { label: 'Inviato', color: '#7c3aed' },
  accepted: { label: 'Accettato', color: '#16a34a' },
  rejected: { label: 'Rifiutato', color: '#dc2626' },
};

function formatCurrency(amount: number): string {
  return `€ ${amount.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`;
}

export default function QuotesPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const { data: quotes = [], isLoading } = useQuotes(
    statusFilter || search ? { status: statusFilter || undefined, search: search || undefined } : undefined
  );
  const updateStatus = useUpdateQuoteStatus();
  const [selectedQuote, setSelectedQuote] = useState<string | null>(null);

  return (
    <div className="quotes-page">
      <div className="quotes-header">
        <h2>📋 Preventivi</h2>
        <p className="subtitle">Gestisci tutti i tuoi preventivi</p>
      </div>

      <div className="quotes-toolbar">
        <input
          type="text" value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="🔍 Cerca per numero..."
          className="search-input"
        />
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">Tutti gli stati</option>
          {Object.entries(STATUS_MAP).map(([key, { label }]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="loading">Caricamento preventivi...</div>
      ) : quotes.length === 0 ? (
        <div className="empty-state">
          <p>Nessun preventivo trovato.</p>
          <p className="hint">Crea il tuo primo preventivo dal bot Telegram con /nuovo</p>
        </div>
      ) : (
        <div className="quotes-grid">
          {quotes.map(q => {
            const status = STATUS_MAP[q.status] || STATUS_MAP.draft;
            const customer = q.customers;
            return (
              <div key={q.id} className="quote-card" onClick={() => setSelectedQuote(q.id)}>
                <div className="quote-card-header">
                  <span className="quote-number">{q.number}</span>
                  <span className="status-badge" style={{ background: status.color }}>
                    {status.label}
                  </span>
                </div>
                <div className="quote-card-body">
                  <div className="customer-name">{customer?.name || 'Cliente N/D'}</div>
                  <div className="quote-date">
                    {new Date(q.created_at).toLocaleDateString('it-IT')}
                  </div>
                </div>
                <div className="quote-card-footer">
                  <div className="tier-prices">
                    <span className="tier base">🟢 {formatCurrency(q.total_base || 0)}</span>
                    <span className="tier medio">🟡 {formatCurrency(q.total_medio || 0)}</span>
                    <span className="tier top">🔴 {formatCurrency(q.total_top || 0)}</span>
                  </div>
                  {q.pdf_url && (
                    <a href={q.pdf_url} target="_blank" rel="noopener noreferrer"
                       className="pdf-link" onClick={e => e.stopPropagation()}>
                      📄 PDF
                    </a>
                  )}
                </div>
                {selectedQuote === q.id && (
                  <div className="quote-actions">
                    {q.status === 'sent' && (
                      <>
                        <button
                          onClick={e => { e.stopPropagation(); updateStatus.mutate({ id: q.id, status: 'accepted' }); }}
                          className="btn-accept">✅ Accettato</button>
                        <button
                          onClick={e => { e.stopPropagation(); updateStatus.mutate({ id: q.id, status: 'rejected' }); }}
                          className="btn-reject">❌ Rifiutato</button>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
