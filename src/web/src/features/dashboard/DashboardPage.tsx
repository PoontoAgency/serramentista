/**
 * DashboardPage.tsx — KPI e statistiche homepage
 */
import { useQuoteStats, useQuotes } from '../quotes/useQuotes';
import './dashboard.css';

function formatCurrency(amount: number): string {
  return `€ ${amount.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`;
}

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  draft: { label: 'Bozza', color: '#6b7280' },
  ready: { label: 'Pronto', color: '#2563eb' },
  sent: { label: 'Inviato', color: '#7c3aed' },
  accepted: { label: 'Accettato', color: '#16a34a' },
  rejected: { label: 'Rifiutato', color: '#dc2626' },
};

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuoteStats();
  const { data: recentQuotes = [] } = useQuotes();

  const recent = recentQuotes.slice(0, 5);
  const conversionRate = stats && stats.total > 0
    ? ((stats.accepted / stats.total) * 100).toFixed(1)
    : '0';

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h2>📊 Dashboard</h2>
        <p className="subtitle">Panoramica della tua attività</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon">📋</div>
          <div className="kpi-value">{statsLoading ? '...' : stats?.total || 0}</div>
          <div className="kpi-label">Preventivi totali</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon">📤</div>
          <div className="kpi-value">{statsLoading ? '...' : stats?.sent || 0}</div>
          <div className="kpi-label">In attesa</div>
        </div>
        <div className="kpi-card accent">
          <div className="kpi-icon">💰</div>
          <div className="kpi-value">{statsLoading ? '...' : formatCurrency(stats?.totalValue || 0)}</div>
          <div className="kpi-label">Valore accettati</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon">📈</div>
          <div className="kpi-value">{statsLoading ? '...' : `${conversionRate}%`}</div>
          <div className="kpi-label">Tasso conversione</div>
        </div>
      </div>

      {/* Ultimi preventivi */}
      <div className="recent-section">
        <h3>Ultimi preventivi</h3>
        {recent.length === 0 ? (
          <div className="empty-state">
            <p>Nessun preventivo ancora.</p>
            <p className="hint">Invia /nuovo al bot Telegram per crearne uno!</p>
          </div>
        ) : (
          <div className="recent-list">
            {recent.map(q => {
              const status = STATUS_MAP[q.status] || STATUS_MAP.draft;
              return (
                <div key={q.id} className="recent-item">
                  <div className="recent-info">
                    <span className="recent-number">{q.number}</span>
                    <span className="recent-customer">{q.customers?.name || 'N/D'}</span>
                  </div>
                  <div className="recent-meta">
                    <span className="status-dot" style={{ background: status.color }}></span>
                    <span className="recent-status">{status.label}</span>
                    <span className="recent-value">{formatCurrency(q.total_medio || 0)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
