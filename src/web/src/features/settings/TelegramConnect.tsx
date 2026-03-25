/**
 * TelegramConnect — Componente per collegare il bot Telegram.
 * Genera un token UUID, mostra istruzioni, e fa polling per verificare il collegamento.
 */
import { useState, useEffect, useCallback } from 'react';
import { supabase } from '../../lib/supabase';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';

interface TelegramConnectProps {
  companyId: string;
  onConnected?: () => void;
}

export function TelegramConnect({ companyId, onConnected }: TelegramConnectProps) {
  const [token, setToken] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [loading, setLoading] = useState(true);

  // Carica stato attuale
  useEffect(() => {
    async function loadStatus() {
      const { data } = await supabase
        .from('companies')
        .select('telegram_token, telegram_chat_id')
        .eq('id', companyId)
        .single();

      if (data) {
        setToken(data.telegram_token);
        setIsConnected(!!data.telegram_chat_id);
      }
      setLoading(false);
    }
    loadStatus();
  }, [companyId]);

  // Genera token UUID
  const generateToken = useCallback(async () => {
    const newToken = crypto.randomUUID();
    const { error } = await supabase
      .from('companies')
      .update({ telegram_token: newToken })
      .eq('id', companyId);

    if (!error) {
      setToken(newToken);
    }
  }, [companyId]);

  // Polling per verificare collegamento (ogni 3 secondi)
  useEffect(() => {
    if (!token || isConnected) return;

    setIsChecking(true);
    const interval = setInterval(async () => {
      const { data } = await supabase
        .from('companies')
        .select('telegram_chat_id')
        .eq('id', companyId)
        .single();

      if (data?.telegram_chat_id) {
        setIsConnected(true);
        setIsChecking(false);
        clearInterval(interval);
        onConnected?.();
      }
    }, 3000);

    return () => {
      clearInterval(interval);
      setIsChecking(false);
    };
  }, [token, isConnected, companyId, onConnected]);

  if (loading) return <Spinner />;

  if (isConnected) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '1.5rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>✅</div>
          <h3 style={{ margin: '0 0 0.5rem 0' }}>Bot Telegram collegato!</h3>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
            Il tuo account è collegato al bot Serramentista.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div style={{ padding: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1rem 0' }}>🤖 Collega il Bot Telegram</h3>

        {!token ? (
          <div style={{ textAlign: 'center' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Genera un token per collegare il tuo account al bot Telegram.
            </p>
            <Button onClick={generateToken}>Genera Token</Button>
          </div>
        ) : (
          <div>
            <p style={{ marginBottom: '1rem' }}>Segui questi passaggi:</p>

            <ol style={{ lineHeight: 2, paddingLeft: '1.5rem' }}>
              <li>
                Apri Telegram e cerca <strong>@SerrBot</strong>
              </li>
              <li>Invia il comando:</li>
            </ol>

            <div
              style={{
                background: 'var(--bg-tertiary, #f3f4f6)',
                padding: '0.75rem 1rem',
                borderRadius: '0.5rem',
                fontFamily: 'monospace',
                fontSize: '0.9rem',
                margin: '0.5rem 0 1rem 0',
                wordBreak: 'break-all',
              }}
            >
              /connect {token}
            </div>

            {isChecking && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                }}
              >
                <Spinner size="sm" />
                In attesa di collegamento...
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
