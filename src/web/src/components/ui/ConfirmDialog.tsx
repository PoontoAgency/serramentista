/**
 * ConfirmDialog.tsx — Dialog di conferma per azioni distruttive
 */
import { useEffect, useRef } from 'react';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  open, title, message,
  confirmLabel = 'Conferma',
  cancelLabel = 'Annulla',
  danger = false,
  onConfirm, onCancel,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    if (open) {
      dialogRef.current?.showModal();
    } else {
      dialogRef.current?.close();
    }
  }, [open]);

  if (!open) return null;

  return (
    <dialog
      ref={dialogRef}
      onClose={onCancel}
      style={{
        position: 'fixed', zIndex: 1000,
        border: 'none', borderRadius: '0.75rem',
        padding: '1.5rem', maxWidth: '420px', width: '90%',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        animation: 'dialogFadeIn 0.2s ease-out',
      }}
    >
      <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>
        {title}
      </h3>
      <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
        {message}
      </p>
      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
        <button
          onClick={onCancel}
          style={{
            padding: '0.5rem 1rem', border: '1px solid #d1d5db',
            borderRadius: '0.5rem', background: 'white', cursor: 'pointer',
            fontWeight: 500, fontSize: '0.875rem',
          }}
        >
          {cancelLabel}
        </button>
        <button
          onClick={() => { onConfirm(); onCancel(); }}
          style={{
            padding: '0.5rem 1rem', border: 'none',
            borderRadius: '0.5rem', cursor: 'pointer',
            fontWeight: 500, fontSize: '0.875rem', color: 'white',
            background: danger ? '#dc2626' : '#1a56db',
          }}
        >
          {confirmLabel}
        </button>
      </div>
      <style>{`
        dialog::backdrop { background: rgba(0,0,0,0.5); }
        @keyframes dialogFadeIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </dialog>
  );
}
