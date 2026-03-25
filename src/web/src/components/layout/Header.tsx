import { useAuthStore } from '../../store/authStore'

export default function Header() {
  const company = useAuthStore((s) => s.company)

  return (
    <header className="h-16 bg-white border-b border-neutral-200 flex items-center justify-between px-8">
      <div />

      {/* User info */}
      <div className="flex items-center gap-3">
        <div className="text-right">
          <p className="text-sm font-medium text-neutral-900">
            {company?.owner_name || 'Utente'}
          </p>
          <p className="text-xs text-neutral-600">
            {company?.company_name}
          </p>
        </div>
        <div className="h-9 w-9 rounded-full bg-primary/10 text-primary flex items-center justify-center font-semibold text-sm">
          {(company?.owner_name || 'U').charAt(0).toUpperCase()}
        </div>
      </div>
    </header>
  )
}
