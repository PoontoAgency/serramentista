/**
 * ErrorBoundary.tsx — Cattura errori React non gestiti
 */
import { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', minHeight: '60vh', padding: '2rem',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Qualcosa è andato storto
          </h2>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem', maxWidth: '400px' }}>
            Si è verificato un errore imprevisto. Ricarica la pagina per riprovare.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#1a56db', color: 'white', border: 'none',
              padding: '0.625rem 1.5rem', borderRadius: '0.5rem',
              cursor: 'pointer', fontWeight: 500, fontSize: '0.9375rem',
            }}
          >
            Ricarica pagina
          </button>
          {this.state.error && (
            <details style={{ marginTop: '1.5rem', fontSize: '0.75rem', color: '#9ca3af' }}>
              <summary>Dettagli errore</summary>
              <pre style={{ textAlign: 'left', whiteSpace: 'pre-wrap', maxWidth: '500px' }}>
                {this.state.error.message}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
